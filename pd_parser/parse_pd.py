# -*- coding: utf-8 -*-
"""Find photodiode events.

Take a potentially corrupted photodiode channel and find
the event time samples at which it turned on.
"""
# Authors: Alex Rockhill <aprockhill@mailbox.org>
#
# License: BSD (3-clause)

import os
import os.path as op
import numpy as np
from tqdm import tqdm

import mne


def _read_tsv(fname):
    """Read tab-separated value file data."""
    if op.splitext(fname)[-1] != '.tsv':
        raise ValueError(f'Unable to read {fname}, tab-separated-value '
                         '(tsv) is required.')
    if op.getsize(fname) == 0:
        raise ValueError(f'Error in reading tsv, file {fname} empty')
    df = dict()
    with open(fname, 'r') as fid:
        headers = fid.readline().rstrip().split('\t')
        for header in headers:
            df[header] = list()
        for line in fid:
            line_data = line.rstrip().split('\t')
            if len(line_data) != len(headers):
                raise ValueError(f'Error with file {fname}, the columns are '
                                 'different lengths')
            for i, data in enumerate(line_data):
                numeric = all([c.isdigit() or c in ('.', '-')
                               for c in data])
                if numeric:
                    if data.isdigit():
                        df[headers[i]].append(int(data))
                    else:
                        df[headers[i]].append(float(data))
                else:
                    df[headers[i]].append(data)
    if any([not val for val in df.values()]):  # no empty lists
        raise ValueError(f'Error in reading tsv, file {fname} '
                         'contains no data')
    return df


def _to_tsv(fname, df):
    """Write tab-separated value file data."""
    if op.splitext(fname)[-1] != '.tsv':
        raise ValueError(f'Unable to write to {fname}, tab-separated-value '
                         '(tsv) is required.')
    if len(df.keys()) == 0:
        raise ValueError('Empty data file, no keys')
    first_column = list(df.keys())[0]
    with open(fname, 'w') as fid:
        fid.write('\t'.join([str(k) for k in df.keys()]) + '\n')
        for i in range(len(df[first_column])):
            fid.write('\t'.join([str(val[i]) for val in df.values()]) + '\n')


def _read_raw(fname, preload=True, verbose=True):
    _, ext = op.splitext(fname)
    """Read raw data into an mne.io.Raw object."""
    if verbose:
        print('Reading in {}'.format(fname))
    if ext == '.fif':
        raw = mne.io.read_raw_fif(fname, preload=preload)
    elif ext == '.edf':
        raw = mne.io.read_raw_edf(fname, preload=preload)
    elif ext == '.bdf':
        raw = mne.io.read_raw_bdf(fname, preload=preload)
    elif ext == '.vhdr':
        raw = mne.io.read_raw_brainvision(fname, preload=preload)
    elif ext == '.set':
        raw = mne.io.read_raw_eeglab(fname, preload=preload)
    else:
        raise ValueError('Extension {} not recognized, options are'
                         'fif, edf, bdf, vhdr (brainvision) and set '
                         '(eeglab)'.format(ext))
    return raw


def _load_beh_df(behf, beh_col):
    """Load the behavioral data frame and check columns."""
    df = _read_tsv(behf)
    if beh_col not in df:
        raise ValueError(f'beh_col {beh_col} not in the columns of '
                         f'behf {behf}. Please check that the correct '
                         'column is provided')
    return df[beh_col], df


def _get_pd_channel_data(raw, pd_ch_names):
    """Get the time-series data from the channel names."""
    if any([ch not in raw.ch_names for ch in pd_ch_names]):
        raise ValueError(f'Not all pd_ch_names, {pd_ch_names}, '
                         'in raw channel names')
    if len(pd_ch_names) == 2:
        pd = raw._data[raw.ch_names.index(pd_ch_names[0])]
        pd -= raw._data[raw.ch_names.index(pd_ch_names[1])]
    else:
        pd = raw._data[raw.ch_names.index(pd_ch_names[0])]
    pd -= np.median(pd)
    return pd


def _get_pd_data(raw, pd_ch_names):
    """Get the names of the photodiode channels from the user."""
    # if pd_ch_names provided
    if pd_ch_names is not None:
        if any([ch not in raw.ch_names for ch in pd_ch_names]):
            raise ValueError(f'Not all pd_ch_names, {pd_ch_names}, '
                             'in raw channel names')
    else:  # if no pd_ch_names provided
        pd_ch_names = input('Enter photodiode channel names separated by a '
                            'comma or type "plot" to plot the data first:\t')
        if pd_ch_names.lower() == 'plot':
            raw.plot()
        n_chs = 0 if pd_ch_names == 'plot' else len(pd_ch_names.split(','))
        while n_chs not in (1, 2) or not all([ch.strip() in raw.ch_names for
                                              ch in pd_ch_names.split(',')]):
            pd_ch_names = input('Enter photodiode channel names '
                                'separated by a comma:\t')
            for ch in pd_ch_names.split(','):
                if not ch.strip() in raw.ch_names:
                    print(f'{ch.strip()} not in raw channel names')
            n_chs = len(pd_ch_names.split(','))
            if n_chs > 2:
                print(f'{n_chs} is too many names, enter 1 name '
                      'for common referenced photodiode data or '
                      '2 names for bipolar reference')
        pd_ch_names = [ch.strip() for ch in pd_ch_names.split(',')]
    # get pd data using channel names
    pd = _get_pd_channel_data(raw, pd_ch_names)
    return pd, pd_ch_names


def _check_if_pd_event(pd, i, max_len_i, zscore, min_i, baseline_i):
    """Take one stretch of data and determine if there is an event there.

    Move in chunks twice as long as your longest photodiode signal
    with the first 0.25 as baseline to test whether the signal goes
    above/below baseline and back below/above.
    The event onset must have a minimum length `min_i`.
    """
    b = pd[i - baseline_i:i]
    # use twice the length so event can be centered
    s = (pd[i:i + 2 * max_len_i] - np.median(b)) / np.std(b)
    binned_s = np.digitize(s, [-np.inf, -zscore, zscore, np.inf]) - 2
    for direction, binary_s in {'up': binned_s, 'down': s < -binned_s}.items():
        onset = np.where(binary_s[:max_len_i] == 1)[0]
        if onset.size > min_i:  # must be long enough
            e = onset[0]
            if all(binary_s[:e] == 0):  # must start off:
                # must have an offset and no more events
                offset = np.where(binary_s[e:] < 1)[0]
                if offset.size > 0:
                    oe = offset[0]
                    if oe <= max_len_i and \
                            all(binary_s[e + oe:e + max_len_i] == 0):
                        return direction, i + e, i + e + oe
    return None, None, None


def _find_pd_candidates(pd, max_len_i, baseline_i, zscore, min_i,
                        verbose=True):
    """Find all points in the signal that look like a square wave."""
    if verbose:
        print('Finding photodiode events')
    pd_candidates = dict(up=set(), down=set())
    for i in tqdm(range(baseline_i, len(pd) - max_len_i - baseline_i,
                        baseline_i // 2)):
        direction, onset, _ = _check_if_pd_event(
            pd, i, max_len_i, zscore, min_i, baseline_i)
        # no rounding errors
        if onset is not None and all(
            [onset + j not in this_pd_cs for j in range(-min_i, min_i + 1)
             for this_pd_cs in pd_candidates.values()]):
            pd_candidates[direction].add(onset)
    pd_direction = 'down' if \
        len(pd_candidates['down']) > len(pd_candidates['up']) else 'up'
    pd_candidates = pd_candidates[pd_direction]
    if verbose:
        print(f'{len(pd_candidates)} {pd_direction}-deflection photodiode '
              'candidate events found')
    sorted_pds = np.array(sorted(pd_candidates))
    return pd_candidates, sorted_pds


def _pd_event_dist(b_event, pd_candidates, max_index, exclude_shift_i):
    """Find the shortest distance from the behavioral event to a pd event."""
    j = 0
    max_index += 2 * exclude_shift_i
    b_event = np.round(b_event).astype(int)
    while b_event + j < max_index and b_event - j > 0 and j < exclude_shift_i:
        if b_event - j in pd_candidates:
            return j
        if b_event + j in pd_candidates:
            return -j
        j += 1
    return exclude_shift_i


def _check_alignment(beh_events, pd_candidates, max_index, max_i):
    """Check the alignment, account for misalignment accumulation."""
    errors = np.zeros(beh_events.size)
    for i, b_event in enumerate(beh_events):
        j = _pd_event_dist(b_event, pd_candidates, max_index, max_i)
        if abs(j) < max_i:
            beh_events -= j
            errors[i] = j
        else:
            errors[i] = max_i
    return errors


def _find_best_alignment(beh_events, sorted_pds, max_i, sfreq,
                         verbose=True):
    """Find the beh event that causes the best alignment when used to start."""
    beh_diffs = beh_events[1:] - beh_events[:-1]
    pd_candidates = set(sorted_pds)
    pd_dists = np.ones((sorted_pds.size - 1, sorted_pds.size - 1)) * np.inf
    for i in range(1, sorted_pds.size):
        for j in range(sorted_pds.size - 1):
            if i > j:
                pd_dists[j, i - 1] = abs(sorted_pds[i] - sorted_pds[j])
    # check best alignments
    min_error = best_alignment = best_errors = None
    if verbose:
        print('Checking best behavior-photodiode difference alignments')
    for i, beh_diff in enumerate(tqdm(beh_diffs)):
        best_offset = np.argmin(np.min(abs(pd_dists - beh_diff), axis=1))
        bevs = beh_events.copy() - beh_events[i] + sorted_pds[best_offset]
        beh_errors = _check_alignment(bevs, pd_candidates,
                                      sorted_pds[-1], max_i)
        error_metric = np.median(abs(beh_errors))
        if min_error is None or error_metric < min_error:
            best_alignment = sorted_pds[best_offset] - beh_events[i]
            min_error = error_metric
            best_errors = beh_errors
    if verbose:
        print('Best alignment with the photodiode shifted {:.0f} ms '
              'relative to the first behavior event\nerrors: min {:.0f}, '
              'q1 {:.0f}, med {:.0f}, q3 {:.0f}, max {:.0f}'.format(
                  (beh_events[0] + best_alignment) / sfreq, min(best_errors),
                  np.quantile(best_errors, 0.25), np.median(best_errors),
                  np.quantile(best_errors, 0.75), max(best_errors)))
    return best_alignment


def _recover_event(pd, b_event, exclude_shift_i, zscore):
    """Recover with a corrupted baseline or plateau but not on/offset."""
    b_event_i = np.round(b_event).astype(int)
    section = pd[b_event_i - exclude_shift_i:
                 b_event_i + exclude_shift_i].copy()
    baseline = pd[b_event_i - 2 * exclude_shift_i: b_event_i - exclude_shift_i]
    section = (section - np.median(baseline)) / baseline.std()
    event = np.where(abs(section) > zscore)[0]
    return b_event_i - exclude_shift_i + event[0]if event.size > 0 else None


def _exclude_ambiguous_events(beh_events, sorted_pds, best_alignment, pd,
                              exclude_shift_i, max_len_i, resync_i, sfreq,
                              zscore, recover, verbose=True):
    """Exclude all events that are outside the given shift compared to beh."""
    if verbose:
        import matplotlib.pyplot as plt
        pd_section_data = dict(b_event=list(), title=list())
        print('Excluding events that have zero close events or more than '
              'one photodiode event within `max_len` time')
    sfreq_i = np.round(sfreq).astype(int)
    events = dict()
    errors = dict()
    pd_candidates = set(sorted_pds)
    max_index = max(sorted_pds)
    for i in sorted(beh_events.keys()):
        b_event = beh_events[i] + best_alignment
        j = _pd_event_dist(b_event, pd_candidates, max_index,
                           exclude_shift_i=np.inf)
        if abs(j) < exclude_shift_i:
            best_alignment -= j
            events[i] = np.round(b_event - j).astype(int)
            errors[i] = j
            pd_events = np.logical_and(sorted_pds < (events[i] + max_len_i),
                                       sorted_pds > (events[i] - max_len_i))
            if sum(pd_events) > 1:
                events.pop(i)
                errors.pop(i)
                if verbose:
                    print(f'Excluding event {i}, {sum(pd_events)} events')
                    pd_section_data['b_event'].append(b_event)
                    pd_section_data['title'].append(
                        f'{sum(pd_events)} events found '
                        f'for\nbeh event {i}, excluding')
        else:
            if verbose:
                # if off by nearly exclude_shift_i, still use for adjusting
                if abs(j) < resync_i:
                    best_alignment -= j
                # if off by a less than max_len, report samples
                if abs(j) < max_len_i:
                    j_ms = int(j / sfreq * 1000)
                    text = f'Excluding event {i},\noff by {j_ms} ms'
                else:  # if off by more than max_len, just say missing
                    if recover:
                        event = _recover_event(pd, b_event, exclude_shift_i,
                                               zscore)
                        if event is None:
                            text = f'No event found to recover\nfor event {i}'
                        else:
                            fig, ax = plt.subplots()
                            section = \
                                pd[event - 2 * sfreq_i: event + 2 * sfreq_i]
                            ax.plot(np.linspace(-2, 2, 4 * sfreq_i), section)
                            ax.plot([0, 0], [section.min(), section.max()])
                            ax.set_title(f'Corrupted Event {i}')
                            ax.set_xlabel('time (s)')
                            ax.set_ylabel('voltage')
                            fig.show()
                            if input('Recover event? (y/N) ').lower() == 'y':
                                events[i] = event
                                text = f'Event {i} recovered\n(not excluded)'
                            else:
                                text = f'Recovered event {i}\ndiscarded'
                    else:
                        text = f'Excluding event {i},\nno event found'
                print(text.replace('\n', ' '))
                pd_section_data['b_event'].append(b_event)
                pd_section_data['title'].append(text)
    if verbose:
        n_events_ex = len(pd_section_data['b_event'])
        if n_events_ex:  # only plot if some events were excluded
            nrows = int(n_events_ex**0.5)
            ncols = int(np.ceil(n_events_ex / nrows))
            fig, axes = plt.subplots(nrows, ncols, figsize=(nrows * 10,
                                                            ncols * 5))
            fig.suptitle('Excluded Events')
            fig.subplots_adjust(hspace=0.75, wspace=0.5)
            if nrows == 1 and ncols == 1:
                axes = [axes]
            else:
                axes = axes.flatten()
            for ax in axes[n_events_ex:]:
                ax.axis('off')  # turn off all unused axes
            for b_event, title, ax in zip(pd_section_data['b_event'],
                                          pd_section_data['title'],
                                          axes[:n_events_ex]):
                pd_section = pd[int(b_event - max_len_i):
                                int(b_event + max_len_i)]
                ax.plot(np.linspace(-1, 1, pd_section.size), pd_section)
                ax.plot([0, 0], [pd_section.min(), pd_section.max()],
                        color='r')
                ax.set_title(title, fontsize=12)
                ax.set_ylabel('voltage')
                ax.set_xticks(np.linspace(-1, 1, 5))
                ax.set_xticklabels(np.round(np.linspace(
                    -max_len_i / sfreq, max_len_i / sfreq, 5), 2))
                ax.set_xlabel('time (s)')
            fig.show()
        trials = sorted(errors.keys())
        fig, ax = plt.subplots()
        ax.plot(trials, [errors[t] / sfreq * 1000 for t in trials])
        ax.set_ylabel('Difference (ms)')
        ax.set_xlabel('Trial')
        ax.set_title('Photodiode Events Compared to Behavior Events')
        fig.show()
    return events


def _save_pd_data(fname, raw, events, event_id, pd_ch_names, beh_df=None,
                  add_events=False, overwrite=False):
    """Save the events determined from the photodiode."""
    basename = op.splitext(op.basename(fname))[0]
    pd_data_dir = op.join(op.dirname(fname), basename + '_pd_data')
    if not op.isdir(pd_data_dir):
        os.makedirs(pd_data_dir)
    behf = op.join(pd_data_dir, basename + '_beh_df.tsv')
    if beh_df is None:
        if op.isfile(behf) and overwrite:
            os.remove(behf)
    else:
        if 'pd_sample' in beh_df and not add_events and not overwrite:
            raise ValueError(
                'The column name `pd_sample` is not allowed in the behavior '
                'tsv file (it\'s reserved for internal use. Please rename '
                'that column to continue.')
        if not add_events:
            beh_df['pd_sample'] = \
                [events[i] if i in events else 'n/a' for i in
                 range(len(beh_df[list(beh_df.keys())[0]]))]
            _to_tsv(behf, beh_df)
    onsets = np.array([events[i] for i in sorted(events.keys())])
    annot = mne.Annotations(onset=raw.times[onsets],
                            duration=np.repeat(0.1, len(onsets)),
                            description=np.repeat(event_id,
                                                  len(onsets)))
    if add_events:
        annot_orig, pd_ch_names_orig, _ = _load_pd_data(fname)
        annot += annot_orig
        pd_ch_names += [ch for ch in pd_ch_names if ch not in pd_ch_names]
    annot.save(op.join(pd_data_dir, basename + '_pd_annot.fif'))
    with open(op.join(pd_data_dir, basename + 'pd_ch_names.tsv'), 'w') as fid:
        fid.write('\t'.join(pd_ch_names))


def _load_pd_data(fname):
    """Load previously saved photodiode data--annot and pd channel names."""
    basename = op.splitext(op.basename(fname))[0]
    pd_data_dir = op.join(op.dirname(fname), basename + '_pd_data')
    annot_fname = op.join(pd_data_dir, basename + '_pd_annot.fif')
    pd_channels_fname = op.join(pd_data_dir, basename + 'pd_ch_names.tsv')
    behf = op.join(pd_data_dir, basename + '_beh_df.tsv')
    if not op.isfile(annot_fname) or not op.isfile(pd_channels_fname):
        raise ValueError(f'Photodiode data not found in {pd_data_dir}, '
                         f'specifically, {annot_fname} and '
                         f'{pd_channels_fname}. Either `parse_pd` was '
                         f'not run, or it failed or {pd_data_dir} '
                         'may have been moved or deleted. Rerun '
                         '`parse_pd` and optionally `add_pd_relative_events` '
                         'to fix this')
    with open(pd_channels_fname, 'r') as fid:
        pd_ch_names = fid.readline().rstrip().split('\t')
    beh_df = _read_tsv(behf) if op.isfile(behf) else None
    return mne.read_annotations(annot_fname), pd_ch_names, beh_df


def find_pd_params(fname, pd_ch_names=None, verbose=True):
    """Plot the data so the user can determine the right parameters.

    The user can adjust window size to determine max_len and horizontal
    line height to determine zscore.

    Parameters
    ----------
    fname: str
        The filepath to the electrophysiology file (meg/eeg/ieeg).
    pd_ch_names : list
        Names of the channel(s) containing the photodiode data.
        One channel is to be given for a common reference and
        two for a bipolar reference. If no channels are provided,
        the data will be plotted and the user will provide them.
    verbose : bool
        Whether to display or supress text output on the progress
        of the function.

    """
    # load raw data file with the photodiode data
    import matplotlib as mpl
    mpl.rcParams['toolbar'] = 'None'
    import matplotlib.pyplot as plt
    raw = _read_raw(fname, verbose=verbose)
    pd, _ = _get_pd_data(raw, pd_ch_names)
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.subplots_adjust(top=0.75, left=0.15)
    plot_data = dict()
    recs = dict()

    def zoom(amount):
        ymin, ymax = ax.get_ylim()
        # ymin < 0 and ymax > 0 because median subtracted
        ymin *= amount
        ymax *= amount
        ax.set_ylim([ymin, ymax])
        fig.canvas.draw()

    def scale(amount):
        xmin, xmax = ax.get_xlim()
        # ymin < 0 and ymax > 0 because median subtracted
        xmin -= amount
        xmax += amount
        if xmin < xmax:
            ax.set_xlim([xmin, xmax])
            fig.canvas.draw()

    def set_zscore(event):
        if event.key == 'enter':
            ymin, ymax = ax.get_ylim()
            xmin, xmax = plot_data['xlims']
            b = pd[raw.time_as_index(xmin)[0]: raw.time_as_index(
                xmin + (xmax - xmin) * 0.25)[0]]  # 0.25 == default baseline
            zy = plot_data['zscore'].get_ydata()[0]
            recs['zscore'] = (zy - np.median(b)) / np.std(b)
            recommendations = (
                'Recommendations\nmax_len: {:.2f}, zscore: {:.2f}\n'
                'Try using these parameters for `parse_pd` and\n'
                'please report to the developers if there are issues\n'
                ''.format(recs['max_len'], recs['zscore']))
            ax.set_title(recommendations + 'You may now close the window')
            print(recommendations)
            fig.canvas.draw()
        elif event.key in ('up', 'down'):
            ymin, ymax = ax.get_ylim()
            delta = (ymax - ymin) / 100
            zy = plot_data['zscore'].get_ydata()[0]
            zy_ref = plot_data['zscore_reflection'].get_ydata()[0]
            zy += delta if event.key == 'up' else -delta
            zy_ref -= delta if event.key == 'up' else -delta
            plot_data['zscore'].set_ydata(np.ones((pd.size)) * zy)
            plot_data['zscore_reflection'].set_ydata(
                np.ones((pd.size)) * zy_ref)
            fig.canvas.draw()
        elif event.key in ('-', '+', '='):
            scale(1 if event.key == '-' else -1)

    def set_max_len(event):
        if event.key == 'enter':
            xmin, xmax = ax.get_xlim()
            plot_data['xlims'] = (xmin, xmax)
            recs['max_len'] = (xmax - xmin) / 2 * 1.1
            eid = fig.canvas.mpl_connect('key_press_event', set_zscore)
            fig.canvas.mpl_disconnect(eid - 1)  # disconnect previous
            plot_data['zscore'] = ax.plot(
                raw.times, np.ones((pd.size)) * np.quantile(pd, 0.25),
                color='g')[0]
            plot_data['zscore_reflection'] = ax.plot(
                raw.times, -np.ones((pd.size)) * np.quantile(pd, 0.25),
                color='r')[0]
            ax.set_title(
                'Scale\nUse the up/down arrows to set the horizontal line \n'
                'at a level where the plateau of all the photodiode events \n'
                'is above the green line nothing is below the red line\n'
                'Use +/- to scale the time axis to see more events\n'
                'press enter when finished')
            fig.canvas.draw()
        elif event.key in ('up', 'down'):
            xmin, xmax = ax.get_xlim()
            # ymin < 0 and ymax > 0 because median subtracted
            xmin += 0.1 if event.key == 'up' else -0.1
            xmax -= 0.1 if event.key == 'up' else -0.1
            ax.set_xlim([xmin, xmax])
            fig.canvas.draw()

    def align_keypress(event):
        if event.key == 'enter':
            eid = fig.canvas.mpl_connect('key_press_event', set_max_len)
            fig.canvas.mpl_disconnect(eid - 1)  # disconnect previous
            ax.set_title(
                'Window\nUse the up/down arrows to increase/decrease the\n'
                'size of the window so that only one pd event is in the\n'
                'window (leave room for the longest event if this isn\'t it)\n'
                'press enter when finished')
            fig.canvas.draw()
        elif event.key in ('-', '+', '='):
            zoom(1.1 if event.key == '-' else 0.9)
        elif event.key in ('left', 'right'):
            xmin, xmax = ax.get_xlim()
            xmin += 0.1 if event.key == 'right' else -0.1
            xmax += 0.1 if event.key == 'right' else -0.1
            ax.set_xlim([xmin, xmax])
            zerox = plot_data['zero'].get_xdata()[0]
            zerox += 0.1 if event.key == 'right' else -0.1
            plot_data['zero'].set_xdata([zerox, zerox])
            fig.canvas.draw()
        elif event.key in ('up', 'down'):
            ymin, ymax = ax.get_ylim()
            delta = (ymax - ymin) / 100
            ymin += delta if event.key == 'up' else -delta
            ymax += delta if event.key == 'up' else -delta
            ax.set_ylim([ymin, ymax])
            fig.canvas.draw()

    ax.set_title(
        'Align\nUse the left/right keys to find an uncorrupted photodiode '
        'event\nand align the onset to the center of the window\n'
        'use +/- to zoom the yaxis in and out (up/down to translate)\n'
        'press enter when finished')
    ax.set_xlabel('time (s)')
    ax.set_ylabel('voltage')
    ax.plot(raw.times, pd, color='b')
    midpoint = raw.times[pd.size // 2]
    plot_data['zero'] = ax.plot(
        [midpoint, midpoint], [pd.min() * 10, pd.max() * 10], color='k')[0]
    ax.set_xlim(midpoint - 2.5, midpoint + 2.5)
    ax.set_ylim(pd.min() * 1.25, pd.max() * 1.25)
    fig.canvas.mpl_connect('key_press_event', align_keypress)
    fig.show()


def parse_pd(fname, pd_event_name='Fixation', behf=None,
             beh_col='fix_onset_time', pd_ch_names=None,
             exclude_shift=0.03, resync=0.075,
             max_len=1., zscore=100, min_i=10, baseline=0.25,
             add_events=False, recover=False, overwrite=False, verbose=True):
    """Parse photodiode events.

    Parses photodiode events from a likely very corrupted channel
    using behavioral data to sync events to determine which
    behavioral events don't have a match and are thus corrupted
    and should be excluded (while ignoring events that look like
    photodiode events but don't match behavior)

    Parameters
    ----------
    fname: str
        The filepath to the electrophysiology file (meg/eeg/ieeg).
    pd_event_name: str
        The name of the event corresponding to the photodiode.
    behf : str
        The filepath to a tsv file with the behavioral timing.
    beh_col : str
        The column of the behf tsv that corresponds to the events.
    pd_ch_names : list
        Names of the channel(s) containing the photodiode data.
        One channel is to be given for a common reference and
        two for a bipolar reference. If no channels are provided,
        the data will be plotted and the user will provide them.
    exclude_shift: float
        How many seconds different than expected from the behavior events
        to exclude that event. Use `find_pd_params` to determine if unsure.
    resync : float
        The number of seconds to difference allowed to still use a photodiode
        event to resynchronize with time-stamped events. Events with
        differences between `resync` and `exclude_shift` will still be
        used for alignment but will be excluded from the events. When
        `exclude_shift` is smaller than `resync`, this parameter allows
        event differences less than `exclude_shift` to be removed without
        losing an alignment which depends on resynchronizing to these events
        between `exclude_shift` and `resync`. This is most likely to happen
        when the drift between behavior events and the photodiode is large,
        so many events are to be excluded for being off by a small amount
        but still correctly correspond to a behavior event.
    max_len: float
        The longest photodiode event can be.
    zscore: float
        How large of a z-score difference to use to threshold photodiode
        events. Note, the must be large enough that any overshoot when
        returning to threshold is less than zscore compared to baseline.
    min_i: int
        The minimum number of samples the photodiode event must be on for.
        This should not be changed unless the event is shorter.
    baseline: float
        How much relative to the max_len to use to idenify the time before
        the photodiode event. This should not be changed most likely
        unless there is a specific reason/issue.
    add_events : bool
        Whether to add the events found from the current call of `parse_pd`
        to a events found previously (e.g. first parse with
        `pd_event_name='Fixation'` and then parse with
        `pd_event_name='Response'`.
        Note: `pd_parser.add_pd_relative_events` will be relative to the
        first event added.
    recover : bool
        Whether to recover corrupted events manually.
    verbose : bool
        Whether to display or supress text output on the progress
        of the function.
    overwrite : bool
        Whether to overwrite existing data if it exists.

    Returns
    -------
    events: DataFrame
        A DataFrame that has a column for to the (zero)
        indexed behavioral events and another column corresponding
        to the time stamp of the eeg file.

    """
    if resync < exclude_shift:
        raise ValueError(f'`exclude_shift` ({exclude_shift}) cannot be longer '
                         f'than `resync` ({resync})')
    if baseline <= 0 or baseline > 1:
        raise ValueError(f'baseline must be between 0 and 1, got {baseline}')
    # check if already parsed
    basename = op.splitext(op.basename(fname))[0]
    if op.isdir(op.join(op.dirname(fname), basename + '_pd_data')
                ) and not overwrite and not add_events:
        raise ValueError('Photodiode data directory already exists and '
                         'overwrite=False, set overwrite=True to overwrite')
    # load raw data file with the photodiode data
    raw = _read_raw(fname, verbose=verbose)
    # transform behavior events to sample time
    max_len_i = np.round(raw.info['sfreq'] * max_len).astype(int)
    exclude_shift_i = np.round(raw.info['sfreq'] * exclude_shift).astype(int)
    baseline_i = np.round(max_len_i * baseline).astype(int)
    resync_i = np.round(raw.info['sfreq'] * resync).astype(int)
    # use keyword argument if given, otherwise get the user to enter pd names
    # and get data
    pd, pd_ch_names = _get_pd_data(raw, pd_ch_names)
    pd_candidates, sorted_pds = _find_pd_candidates(
        pd=pd, max_len_i=max_len_i, baseline_i=baseline_i, zscore=zscore,
        min_i=min_i, verbose=verbose)
    # load behavioral data with which to validate event timing
    if behf is None:
        if verbose:
            print('No behavioral tsv file was provided so the photodiode '
                  'events will be returned without validation by task '
                  'timing')
        events = {i: pd_event for i, pd_event in enumerate(sorted_pds)}
        _save_pd_data(fname, raw=raw, events=events, event_id=pd_event_name,
                      pd_ch_names=pd_ch_names, overwrite=overwrite)
        return
    # if behavior is given use it to synchronize and exclude events
    beh_events, beh_df = _load_beh_df(behf=behf, beh_col=beh_col)
    beh_events = {i: beh_ev * raw.info['sfreq'] for i, beh_ev in
                  enumerate(beh_events) if beh_ev != 'n/a'}
    beh_events_sorted = np.array(list(beh_events.values()))
    best_alignment = _find_best_alignment(
        beh_events=beh_events_sorted, sorted_pds=sorted_pds,
        max_i=resync_i, sfreq=raw.info['sfreq'], verbose=verbose)
    events = _exclude_ambiguous_events(
        beh_events=beh_events, sorted_pds=sorted_pds,
        best_alignment=best_alignment, pd=pd, exclude_shift_i=exclude_shift_i,
        max_len_i=max_len_i, resync_i=resync_i, sfreq=raw.info['sfreq'],
        zscore=zscore, recover=recover, verbose=verbose)
    _save_pd_data(fname, raw=raw, events=events, event_id=pd_event_name,
                  pd_ch_names=pd_ch_names, beh_df=beh_df,
                  add_events=add_events, overwrite=overwrite)


def add_pd_off_events(fname, off_event_name='Stim Off', max_len=1.,
                      zscore=100, min_i=10, baseline=0.25,
                      verbose=True, overwrite=False):
    """Add events for when the photodiode deflection returns to baseline.

    Parameters
    ----------
    fname: str
        The filepath to the electrophysiology file (meg/eeg/ieeg).
    off_event : str
        If None, no event will be assigned to cessation of the photodiode
        deflection. If a string is provided, an event of that name will
        be assigned to the cessation of the deflection.
    max_len: float
        The maximum length of the photodiode events.
    zscore: float
        How large of a z-score difference to use to threshold photodiode
        events.
    min_i: int
        The minimum number of samples the photodiode event must be on for.
    baseline: float
        How much relative to max_len to use to idenify the time before
        the photodiode event.
    verbose : bool
        Whether to display or supress text output on the progress
        of the function.
    overwrite : bool
        Whether to overwrite existing data if it exists.

    """
    recover_data = dict(event=None)
    recovered_events = list()

    def align_keypress(event):
        if event.key in ('enter', 'e'):
            if event.key == 'enter':
                recover_data['event'] = recover_data['line'].get_xdata()[0]
            else:
                recover_data['event'] = None
            plt.close(fig)
        elif event.key in ('left', 'right'):
            xmin, xmax = ax.get_xlim()
            linex = recover_data['line'].get_xdata()[0]
            linex += 1 if event.key == 'right' else -1
            if linex >= xmin and linex <= xmax:
                recover_data['line'].set_xdata([linex, linex])
                fig.canvas.draw()
        elif event.key in ('-', '+', '='):
            xmin, xmax = ax.get_xlim()
            linex = recover_data['line'].get_xdata()[0]
            xmin = np.round(max([0, xmin - (linex - xmin)]) if event.key == '-'
                            else np.mean([linex, xmin])).astype(int)
            xmax = np.round(xmax + (xmax - linex) if event.key == '-' else
                            np.mean([linex, xmax])).astype(int)
            ax.set_xlim([xmin, xmax])
            ax.set_ylim([section[xmin: xmax].min(), section[xmin: xmax].max()])
            fig.canvas.draw()

    raw = _read_raw(fname, verbose=verbose)
    annot, pd_ch_names, beh_df = _load_pd_data(fname)
    pd = _get_pd_channel_data(raw, pd_ch_names)
    max_len_i = np.round(raw.info['sfreq'] * max_len).astype(int)
    baseline_i = np.round(max_len_i * baseline).astype(int)
    events = {i: samp for i, samp in enumerate(beh_df['pd_sample'])
              if samp != 'n/a'}
    off_events = {'up': dict(), 'down': dict()}
    for event_idx, i in events.items():
        i -= baseline_i  # move back one baseline avoid ramp up
        direction, pd_start, pd_end = _check_if_pd_event(
            pd, i, max_len_i, zscore, min_i, baseline_i)
        if pd_start is None:  # event added manually, get offset manually
            import matplotlib.pyplot as plt
            sfreq_i = np.round(raw.info['sfreq']).astype(int)
            section = pd[i: i + np.round(max_len * sfreq_i).astype(int)]
            fig, ax = plt.subplots(figsize=(6, 6))
            fig.subplots_adjust(top=0.75)
            ax.set_title('Use the left/right keys to find the event offset\n'
                         '+/- to scale the x axis\npress enter when finished\n'
                         'or `e` to exclude the event')
            ax.set_xlabel('time (s)')
            ax.set_ylabel('voltage')
            ax.plot(section, color='b')
            ax.set_xticks([0, section.size])
            ax.set_xticklabels([0, max_len])
            recover_data['line'] = ax.plot(
                [section.size - 1, section.size - 1],
                [section.min(), section.max()], color='k')[0]
            fig.canvas.mpl_connect('key_press_event', align_keypress)
            plt.show()
            if recover_data['event'] is not None:
                recovered_events.append(recover_data['event'] + i)
        else:
            assert abs(pd_start - events[event_idx]) < min_i
            off_events[direction][event_idx] = pd_end
    pd_direction = 'down' if \
        len(off_events['down']) > len(off_events['up']) else 'up'
    off_events = off_events[pd_direction]
    onsets = np.array(list(off_events.values()) + recovered_events)
    annot += mne.Annotations(
        onset=raw.times[onsets], duration=np.repeat(0.1, onsets.size),
        description=np.repeat(off_event_name, onsets.size))
    # save modified data
    basename = op.splitext(op.basename(fname))[0]
    pd_data_dir = op.join(op.dirname(fname), basename + '_pd_data')
    annot.save(op.join(pd_data_dir, basename + '_pd_annot.fif'))


def add_pd_relative_events(fname, behf, relative_event_cols,
                           relative_event_names=None,
                           overwrite=False, verbose=True):
    """Add events relative to those determined from the photodiode.

    Parameters
    ----------
    fname: str
        The filepath to the electrophysiology file (meg/eeg/ieeg).
    behf : str
        The filepath to a tsv file with the behavioral timing
    relative_event_cols : list
        The names of the columns where time data is stored
        relative to the photodiode event
    relative_event_names : list
        The names of the events in `relative_event_cols`.
    verbose : bool
        Whether to display or supress text output on the progress
        of the function.
    overwrite : bool
        Whether to overwrite existing data if it exists.

    """
    if relative_event_names is None:
        if verbose:
            print('Using relative event cols {} as relative event '
                  'names'.format(', '.join(relative_event_cols)))
        relative_event_names = relative_event_cols
    if len(relative_event_cols) != len(relative_event_names):
        raise ValueError('Mismatched length of relative event behavior '
                         f'file column names, {len(relative_event_cols)} and '
                         f'names of the events {len(relative_event_names)}')
    raw = _read_raw(fname, verbose=verbose)
    relative_events = \
        {name: _load_beh_df(behf, rel_event)[0]
         for name, rel_event in zip(relative_event_names, relative_event_cols)}
    annot, _, beh_df = _load_pd_data(fname)
    for event_name in relative_event_names:
        if event_name in annot.description:
            if overwrite:
                annot.delete([i for i, desc in enumerate(annot.description)
                              if desc == event_name])
            else:
                raise ValueError(f'Event name {event_name} already exists in '
                                 'saved events and `overwrite=False`, use '
                                 '`overwrite=True` to overwrite')
    events = {i: samp for i, samp in enumerate(beh_df['pd_sample'])
              if samp != 'n/a'}
    for name, beh_events in relative_events.items():
        onsets = np.array([events[i] + (beh_events[i] * raw.info['sfreq'])
                           for i in sorted(events.keys())
                           if beh_events[i] != 'n/a']).round().astype(int)
        annot += mne.Annotations(onset=raw.times[onsets],
                                 duration=np.repeat(0.1, onsets.size),
                                 description=np.repeat(name, onsets.size))
    # save modified data
    basename = op.splitext(op.basename(fname))[0]
    pd_data_dir = op.join(op.dirname(fname), basename + '_pd_data')
    annot.save(op.join(pd_data_dir, basename + '_pd_annot.fif'))


def add_pd_events_to_raw(fname, out_fname=None, drop_pd_channels=True,
                         verbose=True, overwrite=False):
    """Save out a new raw file with photodiode events.

    Note: this function is not recommended, rather just skip it and
    use `save_to_bids` which doesn't modify the underlying raw data
    especially converting it to fif if it isn't fif already. In
    `save_to_bids` the raw file itself doens't contain the event
    information, it's only stored in the sidecar.

    Parameters
    ----------
    fname: str
        The filepath to the electrophysiology file (meg/eeg/ieeg).
    out_fname : str
        The filepath to save the modified raw data to.
    drop_pd_channels : bool
        Whether to drop the channel(s) the photodiode data was on.
    verbose : bool
        Whether to display or supress text output on the progress
        of the function.
    overwrite : bool
        Whether to overwrite existing data if it exists.

    Returns
    -------
    out_fname : str
        The filepath to save the modified raw data to.

    """
    raw = _read_raw(fname, verbose=verbose)
    if out_fname is None:
        _, ext = op.splitext(fname)
        out_fname = fname.replace(ext, 'pd_raw.fif')
    if op.isfile(out_fname) and not overwrite:
        raise ValueError(f'out_fname {out_fname} exists, and overwrite=False, '
                         'set overwrite=True to overwrite')
    annot, pd_ch_names, _ = _load_pd_data(fname)
    raw.set_annotations(annot)
    if drop_pd_channels:
        raw.drop_channels([ch for ch in pd_ch_names if ch in raw.ch_names])
    if op.splitext(out_fname)[-1] != '.fif':
        raise ValueError('Only saving as fif is supported, got '
                         f'{op.splitext(out_fname)}')
    raw.save(out_fname, overwrite=overwrite)
    return out_fname


def pd_parser_save_to_bids(bids_dir, fname, sub, task, ses=None, run=None,
                           data_type=None, eogs=None, ecgs=None, emgs=None,
                           verbose=True, overwrite=False):
    """Convert data to BIDS format with events found from the photodiode.

    Parameters
    ----------
    bids_dir : str
        The subject directory in the bids directory where the data
        should be saved.
    fname : str
        The filepath to the electrophysiology file (meg/eeg/ieeg).
    sub : str
        The name of the subject.
    task : str
        The name of the task.
    ses : str
        The name of the session (optional).
    run : str
        The name of the run (optional).
    data_type: str
        The type of the channels containing data, i.e. 'eeg' or 'seeg'.
    eogs: list | None
        The channels recording eye electrophysiology.
    ecgs: list | None
        The channels recording heart electrophysiology.
    emgs: list | None
        The channels recording muscle electrophysiology.
    verbose : bool
        Whether to display or supress text output on the progress
        of the function.
    overwrite : bool
        Whether to overwrite existing data if it exists.

    """
    import mne_bids
    if not op.isdir(bids_dir):
        os.makedirs(bids_dir)
    raw = _read_raw(fname, preload=False, verbose=verbose)
    aux_chs = list()
    for name, ch_list in zip(['eog', 'ecg', 'emg'], [eogs, ecgs, emgs]):
        if ch_list is not None:
            aux_chs += ch_list
            raw.set_channel_types({ch: name for ch in ch_list})
    if data_type is not None:
        raw.set_channel_types({ch: data_type for ch in raw.ch_names if
                               ch not in aux_chs})
    annot, pd_channels, beh_df = _load_pd_data(fname)
    raw.set_annotations(annot)
    events, event_id = mne.events_from_annotations(raw)
    raw.set_channel_types({ch: 'stim' for ch in pd_channels
                           if ch in raw.ch_names})
    bids_path = mne_bids.BIDSPath(subject=sub, session=ses, task=task,
                                  run=run, root=bids_dir)
    mne_bids.write_raw_bids(raw, bids_path, events_data=events,
                            event_id=event_id, verbose=verbose,
                            overwrite=overwrite)
    '''
    beh_path = bids_path.copy().update(datatype='beh', extension='tsv')
    if not op.isdir(op.dirname(beh_path.fpath)):
        os.makedirs(op.dirname(beh_path.fpath))
    if beh_df is not None:
        _to_tsv(beh_path.fpath, beh_df)
    '''
    bids_beh_dir = \
        op.join(bids_dir, f'sub-{sub}', f'ses-{ses}' if ses else '', 'beh')
    if not op.isdir(bids_beh_dir):
        os.makedirs(bids_beh_dir)
    if beh_df is not None:
        _to_tsv(op.join(bids_beh_dir, bids_path.basename + '_beh.tsv'), beh_df)


def simulate_pd_data(n_events=10, n_secs_on=1.0, amp=300., iti=6.,
                     iti_jitter=1.5, drift=0.1, prop_corrupted=0.1,
                     sfreq=1000., seed=11, show=False):
    """Simulate photodiode data.

    Simulate data that is a square wave with a linear change in deflection
    `drift` amount towards zero that then over shoots and drifts back as
    photodiodes tend to do. Some events are also corrupted.

    Parameters
    ----------
    n_events : float
        The number of events to simulate.
    n_secs_on : float | np.array
        The number of seconds each event is on. If a float is provided, the
        time is the same for each event. If an array is provided, it must be
        the length of the number of events, and it determines the length of
        each event respectively.
    amp : float
        The amplitude of the photodiode in standard deviations above baseline.
    iti : float
        The interval in between events.
    iti_jitter : float
        The jitter displacing the events from exactly `iti` distance
        away from each other.
    drift : float
        The factor controlling how much the photodiode changes value
        over time with no external simulus (0. == perfect square wave).
    sfreq : float
        The sampling frequency of the data.
    show : bool
        Whether to plot the data.

    Returns
    -------
    raw : mne.io.Raw
        The raw object containing the photodiode data
    beh_df : dict
        A dictionary with columns:

            `trial` : int
                The index of the event.

            `time` : float
                The time that both the corrupted and uncorrupted events
                occurred in seconds.

    events : np.array
        The uncorrupted events where the first column is the time stamp,
        the second column is unused (zero) and the third column is the
        event identifier.
    corrupted_indices : np.array
        The indices of the events which were corrupted in the simulation.
    """
    if isinstance(n_secs_on, list) and len(n_secs_on) != n_events:
        raise ValueError('If a list of `n_secs_on` is provided, it must '
                         f'match the number of events, {n_events}, got '
                         f'{len(n_secs_on)}')
    assert drift > 0 and iti > 0 and iti_jitter > 0
    # n_secs on as list is okay, just make an array
    if isinstance(n_secs_on, list):
        n_secs_on = np.array(n_secs_on)
    # convert events to samples
    if isinstance(n_secs_on, np.ndarray):
        n_samp_on = np.round(n_secs_on * sfreq).astype(int)
    else:
        n_samp_on = np.repeat(np.round(n_secs_on * sfreq).astype(int),
                              n_events)
    iti_samp = np.round(iti * sfreq).astype(int)
    iti_jitter_samp = np.round(iti_jitter * sfreq).astype(int)
    if iti_samp - iti_jitter_samp <= n_samp_on.min():
        raise ValueError(
            f'Events will run into each other because `iti` ({iti})'
            f' - `iti_jitter` ({iti_jitter}) is less the than minimum'
            f' `n_secs_on` ({n_samp_on.min() / sfreq})')
    # seed random number generator
    np.random.seed(seed)
    # make events
    events = np.zeros((n_events, 3), dtype=int)
    events[:, 0] = iti_samp + np.cumsum(np.round(
        (np.random.random(n_events) * iti_jitter + iti) * sfreq)).astype(int)
    events[:, 2] = 1
    # make pink noise
    n_points = events[:, 0].max() + int(2 * iti * sfreq)
    n_points += n_points % 2  # must be even
    x = np.random.randn(n_points // 2) + np.random.randn(n_points // 2) * 1j
    x /= np.sqrt(np.arange(1, x.size + 1))
    pd_data = np.fft.irfft(x).real
    pd_data /= pd_data.std()
    # add photodiode square waves to pink noise
    for event, n_on in zip(events[:, 0], n_samp_on):
        drift_array = np.linspace(0, 1, n_on)
        pd_data[event: event + n_on] += \
            amp - drift * amp * drift_array
        pd_data[event + n_on: event + 2 * n_on] += \
            drift * amp * drift_array - amp * drift
    # corrupt some events
    n_events_corrupted = np.round(n_events * prop_corrupted).astype(int)
    corrupted_indices = np.random.choice(range(n_events), n_events_corrupted,
                                         replace=False)
    for i in corrupted_indices:
        n_on = n_samp_on[i]
        samp_range = range(events[i, 0] - iti_jitter_samp,
                           events[i, 0] + n_on + iti_jitter_samp)
        # about 2% of times corrupted
        ts_cor = int(len(samp_range) * np.random.random() * 0.02 + 0.005)
        for ts in np.random.choice(samp_range, ts_cor, replace=False):
            # disrupt 1 / 5 of on time, 5 times amplitude
            pd_data[ts - n_on // 10: ts + n_on // 10] = \
                np.random.random() * 5 * amp - amp
    beh_df = dict(trial=np.arange(n_events),
                  time=events[:, 0].astype(float) / sfreq)
    events = np.delete(events, corrupted_indices, axis=0)
    # plot if show
    if show:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(np.linspace(0, sfreq * n_points, pd_data.size), pd_data)
        ax.set_xlabel('time (s)')
        ax.set_ylabel('amp')
        ax.set_title('Photodiode Data')
        fig.show()
    # create mne.io.Raw object
    info = mne.create_info(['pd'], sfreq, ['stim'])
    raw = mne.io.RawArray(pd_data[np.newaxis], info)
    return raw, beh_df, events, corrupted_indices
