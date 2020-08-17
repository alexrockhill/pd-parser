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


def _read_raw(fname, verbose=True):
    _, ext = op.splitext(fname)
    """Read raw data into an mne.io.Raw object."""
    if verbose:
        print('Reading in {}'.format(fname))
    if ext == '.fif':
        raw = mne.io.read_raw_fif(fname, preload=True)
    elif ext == '.edf':
        raw = mne.io.read_raw_edf(fname, preload=True)
    elif ext == '.bdf':
        raw = mne.io.read_raw_bdf(fname, preload=True)
    elif ext == '.vhdr':
        raw = mne.io.read_raw_brainvision(fname, preload=True)
    elif ext == '.set':
        raw = mne.io.read_raw_eeglab(fname, preload=True)
    else:
        raise ValueError('Extension {} not recognized, options are'
                         'fif, edf, bdf, vhdr (brainvision) and set '
                         '(eeglab)'.format(ext))
    return raw


def _load_beh_df(behf, beh_col, verbose=True):
    """Load the behavioral data frame and check columns."""
    df = _read_tsv(behf)
    if beh_col not in df:
        raise ValueError(f'beh_col {beh_col} not in the columns of '
                         f'behf {behf}. Please check that the correct '
                         'column is provided')
    return df[beh_col], df


def _get_pd_data(raw, pd_ch_names):
    """Get the names of the photodiode channels from the user."""
    # if pd_ch_names provided
    if pd_ch_names is not None:
        for ch in pd_ch_names:
            if ch not in raw.ch_names:
                raise ValueError(f'{ch} in pd_ch_names {pd_ch_names} not '
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
    if len(pd_ch_names) == 2:
        pd = raw._data[raw.ch_names.index(pd_ch_names[0])]
        pd -= raw._data[raw.ch_names.index(pd_ch_names[1])]
    else:
        pd = raw._data[raw.ch_names.index(pd_ch_names[0])]
    pd -= np.median(pd)
    return pd, pd_ch_names


def _find_pd_candidates(pd, sfreq, chunk, baseline, zscore, min_i, overlap,
                        verbose=True):
    """Find all points in the signal that look like a square wave."""
    if verbose:
        print('Finding photodiode events')
    ''' Move in chunks twice as long as your longest photodiode signal
        with the first 0.25 as baseline to test whether the signal goes
        above/below baseline and back below/above.
        The event onset must have a minimum length `min_i` and
        `overlap` should be set such that no events will be missed
        and if a pd event gets cut off, you'll find it the next chunk'''
    chunk_i = int(chunk * sfreq)
    baseline_i = int(chunk_i * baseline / 2)
    pd_candidates = set()
    for i in tqdm(range(baseline_i, len(pd) - chunk_i - baseline_i,
                        int(chunk_i * overlap))):
        b = pd[i - baseline_i:i]
        s = (pd[i:i + chunk_i] - np.median(b)) / np.std(b)
        for binary_s in [s > zscore, s < -zscore]:
            if not binary_s[0]:  # must start off
                onset = np.where(binary_s)[0]
                if onset.size > min_i:
                    e = onset[0]
                    offset = np.where(1 - binary_s[e:])[0]
                    # must have an offset and no more events
                    if offset.size > 0 and not any(binary_s[e + offset[0]:]):
                        if not any([i + e + j in pd_candidates for j in
                                    range(-1, 2)]):  # off by one error
                            pd_candidates.add(i + e)
    if verbose:
        print(f'{len(pd_candidates)} photodiode candidate events found')
    return pd_candidates


def _pd_event_dist(b_event, pd_candidates, max_index):
    """Find the shortest distance from the behavioral event to a pd event."""
    j = 0
    # short circuit for alignments way to far forward
    if b_event >= max_index:
        return np.inf
    while b_event + j < max_index and b_event - j > 0:
        if any([b_idx in pd_candidates for b_idx in
                (int(b_event - j), int(b_event + j))]):
            return j
        j += 1
    return np.inf


def _find_best_alignment(beh_events, pd_candidates, sorted_pds,
                         first_alignment_n, verbose=True):
    """Find the beh event that causes the best alignment when used to start."""
    if verbose:
        print('Finding best alignment with behavioral events using the '
              f'first {first_alignment_n} events')
    min_error = best_alignment = best_errors = None
    max_index = max(pd_candidates)
    # may want first_alignment to be small to avoid drift
    for i, pd_i in tqdm(enumerate(sorted_pds)):  # try starting with each pd
        these_beh_events = beh_events.copy() + pd_i
        errors = list()
        for b_event in these_beh_events[:first_alignment_n]:
            errors.append(_pd_event_dist(b_event, pd_candidates, max_index))
        # use the third quartile for robustness-- because of multiple
        # comparisons, some may have a better median by chance, this
        # is less likely for the third quartile. On the other hand,
        # several events may be outliers but this event is robust
        # to a full quarter of events being lost
        error_metric = np.quantile(errors, 0.75)
        if min_error is None or error_metric < min_error:
            best_alignment = i
            min_error = error_metric
            best_errors = errors
    if verbose:
        print('Best alignment starting with photodiode event '
              '#%i, min %i, q1 %i, med %i, q3 %i, max %i ' %
              (best_alignment, min(best_errors),
               np.quantile(best_errors, 0.25), np.median(best_errors),
               np.quantile(best_errors, 0.75), max(best_errors)))
    return best_alignment


def _exclude_ambiguous_events(beh_events, pd_candidates, sorted_pds,
                              pd, best_alignment, sfreq, chunk,
                              exclude_shift, verbose=True):
    """Exclude all events that are outside the given shift compared to beh."""
    if verbose:
        import matplotlib.pyplot as plt
        pd_section_data = dict(b_event=list(), title=list())
        print('Excluding events that have zero close events or more than '
              'one photodiode event within `chunk` time')
    events = dict()
    errors = dict()
    max_index = max(sorted_pds)
    chunk_i = int(sfreq * chunk)
    exclude_shift_i = int(sfreq * exclude_shift)
    beh_events_aligned = beh_events.copy() + sorted_pds[best_alignment]

    for i, b_event in enumerate(beh_events_aligned):
        j = _pd_event_dist(b_event, pd_candidates, max_index)
        if j > exclude_shift_i:
            if verbose:
                pd_section_data['b_event'].append(b_event)
                pd_section_data['title'].append(
                    f'Excluding event {i}\noff by {j} samples')
        else:
            if int(b_event + j) in pd_candidates:
                beh_events_aligned += j
                events[i] = int(b_event + j)
                errors[i] = j
            else:
                beh_events_aligned -= j
                events[i] = int(b_event - j)
                errors[i] = -j
            pd_events = np.logical_and(sorted_pds < (events[i] + chunk_i),
                                       sorted_pds > (events[i] - chunk_i))
            if sum(pd_events) > 1:
                events.pop(i)
                errors.pop(i)
                if verbose:
                    pd_section_data['b_event'].append(b_event)
                    pd_section_data['title'].append(
                        f'{sum(pd_events)} events found '
                        f'for\nbeh event {i}, excluding')
    if verbose:
        n_events_ex = len(pd_section_data['b_event'])
        if n_events_ex:  # only plot if some events were excluded
            nrows = int(n_events_ex**0.5)
            ncols = int(np.ceil(n_events_ex / nrows))
            fig, axes = plt.subplots(nrows, ncols, figsize=(nrows * 5,
                                                            ncols * 3))
            fig.suptitle('Excluded Events')
            fig.subplots_adjust(hspace=0.5, wspace=0.5)
            axes = axes.flatten()
            for ax in axes[n_events_ex:]:
                ax.axis('off')  # turn off all unused axes
            for b_event, title, ax in zip(pd_section_data['b_event'],
                                          pd_section_data['title'],
                                          axes[:n_events_ex]):
                pd_section = pd[int(b_event - 10 * sfreq):
                                int(b_event + 10 * sfreq)]
                ax.plot(np.linspace(-10, 10, pd_section.size), pd_section)
                ax.set_title(title, fontsize=12)
                ax.set_ylabel('voltage')
                ax.set_xlabel('time')
            fig.show()
        print('Final behavior event-photodiode event differences '
              'min %i, q1 %i, med %i, q3 %i, max %i ' %
              (min(errors.values()), np.quantile(list(errors.values()), 0.25),
               np.median(list(errors.values())),
               np.quantile(list(errors.values()), 0.75), max(errors.values())))
        trials = sorted(errors.keys())
        fig, ax = plt.subplots()
        ax.plot(trials, [errors[t] for t in trials])
        ax.set_ylabel('Difference (samples)')
        ax.set_xlabel('Trial')
        ax.set_title('Photodiode Events Compared to Behavior Events')
        fig.show()
    return events


def _save_pd_data(fname, raw, events, event_id, pd_ch_names, beh_df=None):
    """Saves the events determined from the photodiode."""
    basename = op.splitext(op.basename(fname))[0]
    pd_data_dir = op.join(op.dirname(fname), basename + '_pd_data')
    if not op.isdir(pd_data_dir):
        os.makedirs(pd_data_dir)
    if beh_df is not None:
        if 'pd_sample' in beh_df:
            raise ValueError(
                'The column name `pd_sample` is not allowed in the behavior '
                'tsv file (it\'s reserved for internal use. Please rename '
                'that column to continue.')
        beh_df['pd_sample'] = \
            [events[i] if i in events else 'n/a' for i in
             range(len(beh_df[list(beh_df.keys())[0]]))]
        _to_tsv(op.join(pd_data_dir, basename + '_beh_df.tsv'), beh_df)
    onsets = np.array([events[i] for i in sorted(events.keys())])
    annot = mne.Annotations(onset=raw.times[onsets],
                            duration=np.repeat(0.1, len(onsets)),
                            description=np.repeat(event_id,
                                                  len(onsets)))
    annot.save(op.join(pd_data_dir, basename + '_pd_annot.fif'))
    with open(op.join(pd_data_dir, basename + 'pd_ch_names.tsv'), 'w') as fid:
        fid.write('\t'.join(pd_ch_names))


def _load_pd_data(fname):
    """Loads previously saved photodiode data--annot and pd channel names."""
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
    """Plots the data so the user can determine the right parameters.

    The user can adjust window size to determine chunk, horizontal
    line height to determine zscore and seperation length of two
    vertical lines to determine min_i.

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
    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.75, left=0.15)
    plot_data = dict()

    def zoom(amount):
        ymin, ymax = ax.get_ylim()
        # ymin < 0 and ymax > 0 because median subtracted
        ymin *= amount
        ymax *= amount
        ax.set_ylim([ymin, ymax])
        fig.canvas.draw()

    def set_min_i(event):
        if event.key == 'enter':
            xmin, xmax = ax.get_xlim()
            chunk = (xmax - xmin) * 1.1
            b = pd[raw.time_as_index(xmin)[0]: raw.time_as_index(
                xmin + (xmax - xmin) * 0.25)[0]]  # 0.25 == default baseline
            zy = plot_data['zscore'].get_ydata()[0]
            zscore = (zy - np.median(b)) / np.std(b)
            min_i = plot_data['min_i'].get_xdata()[0]
            min_i -= plot_data['zero'].get_xdata()[0]
            min_i = int(min_i * raw.info['sfreq'])
            ax.set_title('Recommendations\nchunk: {:.2f}, zscore: {:.2f}, '
                         'min_i: {:d}\nYou may now close the window\n'
                         'Try using these parameters for `parse_pd` and\n'
                         'please report to the developers if there are issues'
                         ''.format(chunk, zscore, min_i))
            fig.canvas.draw()
        elif event.key in ('left', 'right'):
            min_i_x = plot_data['min_i'].get_xdata()[0]
            min_i_x += 0.01 if event.key == 'left' else -0.01
            plot_data['min_i'].set_xdata([min_i_x, min_i_x])
            fig.canvas.draw()

    def set_zscore(event):
        if event.key == 'enter':
            eid = fig.canvas.mpl_connect('key_press_event', set_min_i)
            fig.canvas.mpl_disconnect(eid - 1)  # disconnect previous
            xmin, xmax = ax.get_xlim()
            zerox = plot_data['zero'].get_xdata()[0]
            min_i_x = (xmax + zerox) / 2
            ymin, ymax = ax.get_ylim()
            plot_data['min_i'] = ax.plot([min_i_x, min_i_x], [ymin, ymax],
                                         color='r')[0]
            ax.set_title(
                'Length\nUse the left/right arrows to set the vertical\n'
                'line to a point on the photodiode plateau\n'
                'where all events would still be on the plateau\n'
                'press enter when finished')
            fig.canvas.draw()
        elif event.key in ('up', 'down'):
            ymin, ymax = ax.get_ylim()
            delta = (ymax - ymin) / 100
            zy = plot_data['zscore'].get_ydata()[0]
            zy += delta if event.key == 'up' else -delta
            plot_data['zscore'].set_ydata(np.ones((pd.size)) * zy)
            fig.canvas.draw()

    def set_chunk(event):
        if event.key == 'enter':
            eid = fig.canvas.mpl_connect('key_press_event', set_zscore)
            fig.canvas.mpl_disconnect(eid - 1)  # disconnect previous
            plot_data['zscore'] = ax.plot(
                raw.times, np.ones((pd.size)) * np.quantile(pd, 0.25),
                color='g')[0]
            ax.set_title(
                'Scale\nUse the up/down arrows to set the horizontal\n'
                'line at a level where the plateau of all the\n'
                'photodiode events would still be above the line\n'
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
            eid = fig.canvas.mpl_connect('key_press_event', set_chunk)
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
        'Align\nUse the left/right keys to find a photodiode event\n'
        'and align the onset to the center of the window\n'
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
             beh_col='fix_onset_time', pd_ch_names=None, exclude_shift=0.1,
             chunk=2, zscore=10, min_i=10, alignment_prop=0.1,
             baseline=0.25, overlap=0.25, overwrite=False, verbose=True):
    """Parses photodiode events.

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
    chunk: float
        The size of the window to chunk the photodiode events by
        should be larger than 2x the longest photodiode event.
        Use `find_pd_params` to determine if unsure.
    zscore: float
        How large of a z-score difference to use to threshold photodiode
        events. Use `find_pd_params` to determine if unsure.
    min_i: int
        The minimum number of samples the photodiode event must be on for.
        Use `find_pd_params` to determine if unsure.
    alignment_prop : float
        Proportion of events to use to score the alignment to the first event.
        This number should be low to have an accurate score without the
        photodiode drifting and causing unexpected alignments (and it's
        faster). e.g. for 300 behavior events and 350 photodiode events
        if alignment_prop=0.05 it will probably work and will take 15
        seconds, if alignment_prop=0.1 it will almost always work
        and take 30 seconds and if alignment_prop=0.2 it will work
        if it's going to and take 75 seconds.
    baseline: float
        How much relative to the chunk to use to idenify the time before
        the photodiode event. This should not be changed most likely
        unless there is a specific reason/issue.
    overlap: float
        How much to overlap the windows of the photodiode event-finding
        process. This should not be changed most likely unless there is
        a specific reason/issue.
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
    # check if already parsed
    basename = op.splitext(op.basename(fname))[0]
    if op.isdir(op.join(op.dirname(fname), basename + '_pd_data')
                ) and not overwrite:
        raise ValueError('Photodiode data directory already exists and '
                         'overwrite=False, set overwrite=True to overwrite')
    # load raw data file with the photodiode data
    raw = _read_raw(fname, verbose=verbose)
    # load behavioral data with which to validate event timing
    if behf is None:
        if verbose:
            print('No behavioral tsv file was provided so the photodiode '
                  'events will be returned without validation by task '
                  'timing')
        beh_events = beh_df = None
    else:
        beh_events, beh_df = _load_beh_df(behf, beh_col)
        for beh_event in beh_events:
            if not np.real(beh_event):
                raise ValueError(f'Non-numeric value {beh_event} found '
                                 'in event column used to synchronize '
                                 'with the photodiode, this is not allowed')
        beh_events = np.array(beh_events)
    # use keyword argument if given, otherwise get the user to enter pd names
    # and get data
    pd, pd_ch_names = _get_pd_data(raw, pd_ch_names)
    pd_candidates = _find_pd_candidates(pd, raw.info['sfreq'], chunk, baseline,
                                        zscore, min_i, overlap, verbose)
    sorted_pds = np.array(sorted(pd_candidates))
    if beh_events is None:
        events = {i: pd_event for i, pd_event in enumerate(sorted_pds)}
        _save_pd_data(fname, raw, events, pd_event_name, pd_ch_names)
        return
    if not np.isreal(alignment_prop
                     ) or alignment_prop < 0 or alignment_prop > 1:
        raise ValueError(f'Cannot align using {alignment_prop} events, '
                         'alignment_prop must be between 0 and 1')
    first_alignment_n = int(alignment_prop * beh_events.size)
    beh_events *= raw.info['sfreq']
    beh_events -= beh_events[0]
    best_alignment = _find_best_alignment(beh_events, pd_candidates,
                                          sorted_pds, first_alignment_n,
                                          verbose)
    events = _exclude_ambiguous_events(beh_events, pd_candidates, sorted_pds,
                                       pd, best_alignment, raw.info['sfreq'],
                                       chunk, exclude_shift, verbose)
    _save_pd_data(fname, raw, events, pd_event_name, pd_ch_names, beh_df)


def add_pd_relative_events(fname, behf, relative_event_cols,
                           relative_event_names=None,
                           overwrite=False, verbose=True):
    """ Adds events relative to those determined from the photodiode.

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

    Returns
    -------
    events: DataFrame
        A DataFrame that has a column for to the (zero)
        indexed behavioral events and another column corresponding
        to the time stamp of the eeg file.

    """
    if relative_event_names is None:
        if verbose:
            print('Using relative event cols {} as relative event '
                  'names'.format(', '.join(relative_event_cols)))
    if len(relative_event_cols) != len(relative_event_names):
        raise ValueError('Mismatched length of relative event behavior '
                         f'file column names, {len(relative_event_cols)} and '
                         f'names of the events {len(relative_event_names)}')
    relative_events = {name: _load_beh_df(behf, rel_event)[0]
                       for name, rel_event in zip(relative_event_names,
                                                  relative_event_cols)}
    raw = _read_raw(fname, verbose=verbose)
    annot, _, beh_df = _load_pd_data(fname)
    for event_name in relative_event_names:
        if event_name in annot.description and not overwrite:
            raise ValueError(f'Event name {event_name} already exists in '
                             'saved events and overwrite=False, use '
                             'overwrite=True to overwrite')
    events = {i: samp for i, samp in enumerate(beh_df[f'pd_sample'])
              if samp != 'n/a'}
    for name, beh_events in relative_events.items():
        onsets = np.array([events[i] + beh_events[i] * raw.info['sfreq']
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
    """Saves out a new raw file with photodiode events.

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
    bids_basename = 'sub-%s' % sub
    bids_beh_dir = op.join(bids_dir, 'sub-%s' % sub)
    if ses is not None:
        bids_basename += '_ses-%s' % ses
        bids_beh_dir = op.join(bids_beh_dir, 'ses-%s' % ses)
    bids_basename += '_task-%s' % task
    bids_beh_dir = op.join(bids_beh_dir, 'beh')
    if run is not None:
        bids_basename += '_run-%s' % run
    if not op.isdir(bids_beh_dir):
        os.makedirs(bids_beh_dir)
    raw = _read_raw(fname, verbose=verbose)
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
    raw = raw.drop_channels([ch for ch in pd_channels if ch in raw.ch_names])
    mne_bids.write_raw_bids(raw, bids_basename, bids_dir,
                            events_data=events, event_id=event_id,
                            verbose=verbose, overwrite=overwrite)
    if beh_df is not None:
        _to_tsv(op.join(bids_beh_dir, bids_basename + '_beh.tsv'), beh_df)
