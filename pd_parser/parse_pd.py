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


def _read_raw(raw, preload=None, verbose=True):
    """Read raw object from file if it's not already loaded."""
    if isinstance(raw, mne.io.BaseRaw):
        if preload:
            raw.load_data()
        elif preload is not None:
            if raw.preload:
                raise ValueError('`raw` object cannot be preloaded')
        if raw.filenames[0] is None:
            raise ValueError('`raw` object must be loaded from disk')
    else:
        _, ext = op.splitext(raw)
        """Read raw data into an mne.io.Raw object."""
        if verbose:
            print('Reading in {}'.format(raw))
        if ext == '.fif':
            raw = mne.io.read_raw_fif(raw, preload=preload)
        elif ext == '.edf':
            raw = mne.io.read_raw_edf(raw, preload=preload)
        elif ext == '.bdf':
            raw = mne.io.read_raw_bdf(raw, preload=preload)
        elif ext == '.vhdr':
            raw = mne.io.read_raw_brainvision(raw, preload=preload)
        elif ext == '.set':
            raw = mne.io.read_raw_eeglab(raw, preload=preload)
        else:
            raise ValueError('Extension {} not recognized, options are'
                             'fif, edf, bdf, vhdr (brainvision), set '
                             '(eeglab)'.format(ext))
    return raw


def _load_beh(beh, beh_key):
    """Load the behavioral data frame and check columns."""
    if not isinstance(beh, dict):
        beh = _read_tsv(beh)
    if beh_key not in beh:
        raise ValueError(f'`beh_key` {beh_key} not in the columns of '
                         f'the `beh` behavior dictionary. Please check '
                         'that the correct column is provided')
    for beh_e in beh[beh_key]:
        if beh_e != 'n/a' and not isinstance(beh_e, (int, float)):
            raise ValueError('Expected numeric value or \'n/a\' for '
                             f'behavior values, got {beh_e}')
    return np.array([np.nan if beh_e == 'n/a' else beh_e
                     for beh_e in beh[beh_key]]), beh


def _get_channel_data(raw, ch_names):
    """Get the time-series data from the channel names."""
    if any([ch not in raw.ch_names for ch in ch_names]):
        raise ValueError(f'Not all pd_ch_names, {ch_names}, '
                         'in raw channel names')
    ch_raw = raw.copy().pick_channels(ch_names).load_data()
    ch_data = ch_raw._data[0] - ch_raw._data[1] if len(ch_names) == 2 \
        else ch_raw._data[0]
    ch_data -= np.median(ch_data)
    return ch_data


def _get_data(raw, ch_names):
    """Get the names of the photodiode channels from the user."""
    # if pd_ch_names provided
    if ch_names is not None:
        if any([ch not in raw.ch_names for ch in ch_names]):
            raise ValueError(f'Not all channel names, {ch_names}, '
                             'in raw channel names')
    else:  # if no pd_ch_names provided
        ch_names = input('Enter channel names separated by a '
                         'comma or type "plot" to plot the data first:\t')
        if ch_names.lower() == 'plot':
            raw.plot()
        n_chs = 0 if ch_names == 'plot' else len(ch_names.split(','))
        while n_chs not in (1, 2) or not all([ch.strip() in raw.ch_names for
                                              ch in ch_names.split(',')]):
            ch_names = input('Enter channel names separated by a comma:\t')
            for ch in ch_names.split(','):
                if not ch.strip() in raw.ch_names:
                    print(f'{ch.strip()} not in raw channel names')
            n_chs = len(ch_names.split(','))
            if n_chs > 2:
                print(f'{n_chs} is too many names, enter 1 name '
                      'for common referenced photodiode data or '
                      '2 names for bipolar reference')
        ch_names = [ch.strip() for ch in ch_names.split(',')]
    # get pd data using channel names
    ch_data = _get_channel_data(raw, ch_names)
    return ch_data, ch_names


def _check_if_pd_event(pd_diff, i, max_len_i, zscore, max_flip_i,
                       baseline_std):
    """Take one stretch of data and determine if there is an event there.

    Use almost all events for on/off due to noise in photodiode causing
    the last event to hop under the threshold and back.
    """
    s = pd_diff[i:i + max_len_i].copy()
    s -= np.median(s)
    s /= baseline_std
    binned_s = np.digitize(s, [-np.inf, -zscore, zscore, np.inf]) - 2
    for direction, binary_s in {'up': binned_s, 'down': -binned_s}.items():
        onset = np.where(binary_s == 1)[0]
        # must be flip on but can't flip back and forth
        if onset.size > 0 and onset.size < max_flip_i:
            e = onset[0]
            almost_all_on = sum(binary_s[onset[0]:onset[-1]]) >= onset.size - 2
            if all(binary_s[:e] == 0) and almost_all_on:  # must start off
                # must have an offset and no more events
                offset = np.where(binary_s[e:] == -1)[0]
                if offset.size > 0 and offset.size < max_flip_i:
                    o = offset[0]
                    almost_all_off = -sum(binary_s[e + o:e + offset[-1]]) \
                        >= offset.size - 2
                    almost_all_zero = \
                        sum(abs(binary_s[e + o + max_flip_i:])) <= 1
                    if almost_all_zero and almost_all_off:
                        return direction, i + e + 1, i + e + o + 2
    return None, None, None


def _find_pd_candidates(pd, max_len, baseline, zscore,
                        max_flip_i, sfreq, verbose=True):
    """Find all points in the signal that look like a square wave."""
    if verbose:
        print('Finding photodiode events')
    max_len_i = np.round(sfreq * max_len).astype(int)
    baseline_i = np.round(max_len_i * baseline).astype(int)
    # zscore photodiode based on baseline values
    pd_diff = np.diff(pd)
    pd_diff -= np.median(pd_diff)
    median_std = np.median([np.std(pd_diff[i - baseline_i:i]) for i in
                            range(baseline_i, len(pd_diff) - baseline_i,
                                  baseline_i)])
    # find indices to check based on being the first above zscore
    check_i = set(np.where(abs(pd_diff) / median_std > zscore)[0])
    check_remove = set()
    for i in check_i:
        if i + 1 in check_i:
            check_remove.add(i + 1)
    check_i = check_i.difference(check_remove)
    # check for clean onset and offset
    pd_candidates = dict(up=list(), down=list(),
                         up_off=list(), down_off=list())
    for i in tqdm(sorted(list(check_i))):
        direction, onset, offset = _check_if_pd_event(
            pd_diff, i, max_len_i, zscore, max_flip_i, median_std)
        # no events immediately following (caused by noise)
        if onset is not None:
            in_flip = onset - pd_candidates[direction][-1] < max_flip_i if \
                pd_candidates[direction] else False
            if not in_flip:
                pd_candidates[direction].append(onset)
                pd_candidates[direction + '_off'].append(offset)
    this_dir = 'down' if \
        len(pd_candidates['down']) > len(pd_candidates['up']) else 'up'
    pd_candidates = pd_candidates[this_dir], pd_candidates[this_dir + '_off']
    if len(pd_candidates[0]) == 0:
        raise ValueError('No photodiode candidates found, please raise an '
                         'issue with code to reproduce the error on GitHub')
    if verbose:
        print(f'{len(pd_candidates[0])} {this_dir}-deflection photodiode '
              'candidate events found')
    return (np.array(sorted(pd_candidates[0])),
            np.array(sorted(pd_candidates[1])))


def _get_audio_zscore(audio, fs):
    import matplotlib as mpl
    mpl.rcParams['toolbar'] = 'None'
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.subplots_adjust(top=0.75, left=0.15)

    def scale(event):
        amount = 0.95 if event.key in ('left', 'down') else 1.25
        if event.key in ('up', 'down'):
            ymin, ymax = ax.get_ylim()
            # ymin < 0 and ymax > 0 because median subtracted
            ymin *= amount
            ymax *= amount
            ax.set_ylim([ymin, ymax])
        elif event.key in ('left', 'right'):
            xmin, xmax = ax.get_xlim()
            # ymin < 0 and ymax > 0 because median subtracted
            xmin /= amount
            xmax *= amount
            if xmin < xmax:
                ax.set_xlim([xmin, xmax])
        fig.canvas.draw()

    ax.set_title(
        'Use the left/right keys to scale time on the x axis '
        '\nand use the up/down keys to zoom the yaxis in and out'
        '\nfind a y value that includes all the events'
        '\nit is recommended to choose the lowest value that is above baseline'
        '\nclose the window when finished')
    ax.set_xlabel('time (s)')
    ax.set_ylabel('zscore')
    ax.plot(audio, color='b')
    xmin = max([0, audio.size // 2 - 10 * fs])
    xmax = min([audio.size, audio.size // 2 + 10 * fs])
    ax.set_xlim(xmin, xmax)
    ax.set_xticks(np.linspace(0, audio.size, 5))
    ax.set_xticklabels(np.round(np.linspace(0, audio.size / fs, 5), 2))
    ax.set_ylim(audio.min() * 0.9, audio.max() * 1.25)
    fig.canvas.mpl_connect('key_press_event', scale)
    fig.show()

    # get user input of zscore
    zscore = None
    while zscore is None:
        zscore = input('What zscore should be used? ')
        if not zscore or any([not d.isdigit() and d != '.' for d in zscore]):
            print('A positive number input is required for zscore')
            zscore = None
        else:
            zscore = float(zscore)
    return zscore


def _find_audio_candidates(audio, max_len, zscore, sfreq, verbose=True):
    if verbose:
        print('Finding points where the audio is above `zscore` threshold...')
    max_len_i = np.round(max_len * sfreq).astype(int)
    audio = abs((audio - np.median(audio)) / audio.std())
    if zscore is None:
        zscore = _get_audio_zscore(audio, sfreq)
    candidates = np.where(audio > zscore)[0]
    delete_indices = list()
    for i, candidate in enumerate(candidates):
        if any(audio[candidate - max_len_i: candidate] > zscore):
            delete_indices.append(i)
    candidates = np.delete(candidates, delete_indices)
    if verbose:
        print(f'{len(candidates)} audio candidate events found')
    return candidates


def _event_dist(beh_e, candidates_set, max_samp, resync_i):
    """Find the shortest distance from the behavioral event to a pd event."""
    j = 0
    if np.isnan(beh_e):
        return np.nan, np.nan
    beh_e = np.round(beh_e).astype(int)
    while beh_e + j < max_samp + resync_i and beh_e - j > 0 and j < resync_i:
        if beh_e - j in candidates_set:
            return j, beh_e - j
        if beh_e + j in candidates_set:
            return -j, beh_e + j
        j += 1
    return np.nan, np.nan


def _check_alignment(beh_events, alignment, candidates, candidates_set,
                     resync_i, check_i=None):
    """Check the alignment, account for misalignment accumulation."""
    check_i = resync_i if check_i is None else check_i
    beh_events = beh_events.copy()  # don't modify original
    events = np.zeros((beh_events.size))
    start = np.argmin([abs(beh_e - candidates).min()
                       for beh_e in beh_events + alignment])
    for i, beh_e in enumerate(beh_events[start:]):
        error, events[start + i] = \
            _event_dist(beh_e + alignment, candidates_set, candidates[-1],
                        check_i)
        if abs(error) <= resync_i and start + i + 1 < beh_events.size:
            beh_events[start + i + 1:] -= error
    for i, beh_e in enumerate(beh_events[:start][::-1]):
        error, events[start - i - 1] = \
            _event_dist(beh_e + alignment, candidates_set, candidates[-1],
                        check_i)
        if abs(error) <= resync_i and start - i - 2 > 0:
            beh_events[:start - i - 2] -= error
    return beh_events, events


def _plot_trial_errors(beh_events, alignment, events,
                       errors, exclude_shift, sfreq):
    """Plot the synchronization error on every trial."""
    import matplotlib.pyplot as plt
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    # plot scrollable dot pattern to first pass check alignment
    beh_events_s = (beh_events + alignment) / sfreq
    beh_d = np.diff(beh_events_s).mean()
    ax.scatter(beh_events_s, np.repeat(-1, beh_events.size))
    ax.scatter(events / sfreq, np.repeat(1, events.size))
    ax.set_xlim([beh_events_s.min() - beh_d, beh_events_s[:10].max() + beh_d])
    ax.set_ylim([-5, 5])
    ax.set_xlabel('Time (s)')
    ax.set_yticks([-1, 1])
    ax.set_yticklabels(['Beh', 'Sync'])
    ax.set_title('Alignment (First 10)')
    # plot the difference between expected and adjusted behavior
    errors = errors.copy()  # don't modify the original
    # don't show huge errors
    errors[abs(errors) / sfreq > 2 * exclude_shift] = np.nan
    ax2.plot(errors / sfreq * 1000)
    exclude_shift_a = np.array([exclude_shift, exclude_shift]) * 1000
    ax2.plot([0, errors.size], exclude_shift_a, color='r')
    ax2.plot([0, errors.size], -exclude_shift_a, color='r')
    ax2.set_ylabel('Difference (ms)')
    ax2.set_xlabel('Trial')
    ax2.set_title('Event Differences')
    fig.tight_layout()
    fig.show()


def _find_best_alignment(beh_events, candidates, exclude_shift, resync,
                         sfreq, verbose=True):
    """Find the beh event that causes the best alignment when used to start."""
    beh_adjusted = np.zeros((beh_events.size))
    events = np.zeros((beh_events.size))
    beh_idx = np.where(~np.isnan(beh_events))[0]
    missing_idx = np.where(np.isnan(beh_events))[0]
    beh_events = beh_events[~np.isnan(beh_events)]  # can't use missing
    resync_i = np.round(sfreq * resync).astype(int)
    min_error = best_alignment = None
    bin_size = np.diff(beh_events).min() / 2
    candidates_set = set(candidates)
    if verbose:
        print('Checking best alignments')
    for beh_e in tqdm(beh_events):
        this_min_error = alignment = None
        for sync_e in candidates:
            bins = np.zeros((2 * beh_events.size))
            bins[::2] = beh_events - beh_e - bin_size / 2
            bins[1::2] = beh_events - beh_e + bin_size / 2
            indices = np.digitize(candidates - sync_e, bins=bins)
            matched_b = \
                beh_events[(indices[indices % 2 == 1] - 1) // 2] - beh_e
            matched_c = candidates[indices % 2 == 1] - sync_e
            unmatched_b = beh_events.size - \
                np.unique(indices[indices % 2 == 1]).size
            errors = abs(matched_b - matched_c)
            error = np.median(errors) + bin_size * unmatched_b
            if this_min_error is None or this_min_error > error:
                alignment = sync_e - beh_e
                this_min_error = error
        beh_events_adjusted, these_events = _check_alignment(
            beh_events, alignment, candidates,
            candidates_set, resync_i)
        errors = beh_events_adjusted - these_events + alignment
        error = np.nansum(abs(errors)) + \
            resync_i * errors[np.isnan(errors)].size
        if min_error is None or error < min_error:
            min_error = error
            best_alignment = alignment
    best_beh_events_adjusted, best_events = _check_alignment(
        beh_events, best_alignment, candidates, candidates_set, resync_i,
        check_i=3 * resync_i)  # get all errors even if more than resync away
    if verbose:
        best_errors = best_beh_events_adjusted - best_events + best_alignment
        errors = best_errors[~np.isnan(best_errors)] / sfreq * 1000
        errors = errors[abs(errors) < resync * 1000]
        n_missed_events = beh_events.size - errors.size
        beh0 = beh_events[~np.isnan(beh_events)][0]
        shift = (beh0 + best_alignment - candidates[0]) / sfreq
        print('Best alignment is with the first behavioral event shifted '
              '{:.2f} s relative to the first synchronization event and '
              'has errors: min {:.2f} ms, q1 {:.2f} ms, med {:.2f} ms, '
              'q3 {:.2f} ms, max {:.2f} ms, {:d} missed events'.format(
                  shift, min(errors), np.quantile(errors, 0.25),
                  np.median(errors), np.quantile(errors, 0.75),
                  max(errors), n_missed_events))
        _plot_trial_errors(beh_events, best_alignment, best_events,
                           best_errors, exclude_shift, sfreq)
    beh_adjusted[beh_idx] = best_beh_events_adjusted
    beh_adjusted[missing_idx] = np.nan
    events[beh_idx] = best_events
    events[missing_idx] = np.nan
    return beh_adjusted, best_alignment, events


def _recover_event(idx, ch_data, beh_e, exclude_shift,
                   zscore, max_len, sfreq):
    """Recover with a corrupted baseline or plateau but not on/offset."""
    import matplotlib.pyplot as plt
    beh_e_i = np.round(beh_e).astype(int)
    max_len_i = np.round(max_len * sfreq).astype(int)
    exclude_shift_i = np.round(exclude_shift * sfreq).astype(int)
    section = np.diff(ch_data[beh_e_i - exclude_shift_i:
                              beh_e_i + exclude_shift_i])
    baseline = np.diff(ch_data[beh_e_i - 2 * exclude_shift_i:
                               beh_e_i - exclude_shift_i])
    section = (section - np.median(baseline)) / baseline.std()
    check_i = set(np.where(abs(section) > zscore)[0])
    check_remove = set()
    for i in check_i:
        if i + 1 in check_i:
            check_remove.add(i + 1)
    check_i = check_i.difference(check_remove)
    if len(check_i) == 0:
        return np.nan, f'{idx}\nnone found to recover'
    elif len(check_i) > 3:  # only can recover 3, don't overwhelm user
        return np.nan, f'{idx}\ntoo many ({len(check_i)}) to recover'
    event, text = np.nan, f'{idx}\nrecovered but discarded'
    for i in check_i:
        sync_e = i + beh_e_i - exclude_shift_i
        fig, ax = plt.subplots()
        section_size = np.round(1.5 * max_len_i).astype(int)
        section = ch_data[sync_e - section_size: sync_e + section_size]
        ax.plot(np.linspace(-1.5 * max_len, 1.5 * max_len, section.size),
                section)
        ax.plot([0, 0], [section.min(), section.max()])
        ax.set_title(f'Corrupted Event {idx}')
        ax.set_xlabel('time (s)')
        ax.set_ylabel('voltage')
        fig.show()
        if input('Recover event? (y/N) ').lower() == 'y':
            return sync_e, f'{idx}\nrecovered (not excluded)'
    return event, text


def _plot_excluded_events(section_data, max_len):
    """Plot events that were more than `exclude_shift` away."""
    import matplotlib.pyplot as plt
    n_events_ex = len(section_data)
    if not n_events_ex:
        return
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
    ymax = np.quantile([abs(sect[2]).max() for sect in section_data
                        if sect[2].size > 0], 0.25) * 1.1
    for i, (event, title, section) in enumerate(section_data):
        axes[i].plot(np.linspace(-1, 1, section.size), section)
        axes[i].plot([0, 0], [-ymax, ymax], color='r')
        axes[i].set_ylim([-ymax, ymax])
        axes[i].set_title(title, fontsize=12)
        if i % ncols == 0:
            axes[i].set_ylabel('voltage')
        axes[i].set_yticks([])
        if i // ncols == nrows - 1:
            axes[i].set_xticks(np.linspace(-1, 1, 3))
            axes[i].set_xticklabels(
                np.round(np.linspace(-2 * max_len, 2 * max_len, 3), 2))
            axes[i].set_xlabel('time (s)')
        else:
            axes[i].set_xticks([])
    fig.show()


def _exclude_ambiguous_events(beh_events, alignment, events, ch_data,
                              candidates, exclude_shift, max_len, sfreq,
                              recover, zscore, verbose=True):
    """Exclude all events that are outside the given shift compared to beh."""
    if verbose:
        section_data = list()
        print('Excluding events that have zero close synchronization events '
              'or more than one synchronization event within `max_len` time')
    max_len_i = np.round(sfreq * max_len).astype(int)
    exclude_shift_i = np.round(sfreq * exclude_shift).astype(int)
    for i, (beh_e, sync_e) in enumerate(zip(beh_events, events)):
        error = beh_e - sync_e + alignment
        if np.abs(error) < exclude_shift_i:
            n_events = np.logical_and(candidates > (sync_e - max_len_i),
                                      candidates < (sync_e + max_len_i)).sum()
            if n_events > 1:
                events[i] = np.nan
                text = (f'{i}\n{n_events} sync events found')
                if recover:
                    events[i], text = _recover_event(
                        i, ch_data, beh_e + alignment, exclude_shift, zscore,
                        max_len, sfreq)
                if verbose:
                    print(text.replace('\n', ' '))
                    event = np.round(beh_e + alignment).astype(int)
                    section_data.append(
                        (beh_e, text, ch_data[event - 2 * max_len_i:
                                              event + 2 * max_len_i]))
        elif not np.isnan(beh_e):
            if recover:
                events[i], text = _recover_event(
                    i, ch_data, beh_e + alignment, exclude_shift, zscore,
                    max_len, sfreq)
            else:
                events[i] = np.nan
                # if off by a less than max_len, report samples
                text = f'{i}\noff by {int(error / sfreq * 1000)} ms' \
                    if abs(error) < max_len_i else f'{i}\nnone found'
            if verbose:
                print(text.replace('\n', ' '))
                event = np.round(beh_e + alignment).astype(int)
                section_data.append(
                    (beh_e, text, ch_data[event - 2 * max_len_i:
                                          event + 2 * max_len_i]))
    if verbose:
        _plot_excluded_events(section_data, max_len)
    return events


def _save_data(raw, events, event_id, ch_names, beh=None,
               add_events=False, overwrite=False):
    """Save the events determined from the photodiode."""
    fname = raw.filenames[0]
    basename = op.splitext(op.basename(fname))[0]
    out_dir = op.join(op.dirname(fname), basename + '_pd_parser_data')
    if not op.isdir(out_dir):
        os.makedirs(out_dir)
    behf = op.join(out_dir, basename + '_beh_df.tsv')
    if beh is None:
        if op.isfile(behf) and overwrite:
            os.remove(behf)
    else:
        if 'pd_parser_sample' in beh and not add_events and not overwrite:
            raise ValueError(
                'The key (column name) `pd_parser_sample` is not allowed '
                'in the behavior tsv file (it\'s reserved for internal use. '
                'Please rename that key (column) to continue.')
        if not add_events:
            beh['pd_parser_sample'] = ['n/a' if np.isnan(e) else int(e) for
                                       e in events]
            _to_tsv(behf, beh)
    onsets = events[~np.isnan(events)].astype(int)
    annot = mne.Annotations(onset=raw.times[onsets],
                            duration=np.repeat(0.1, len(onsets)),
                            description=np.repeat(event_id,
                                                  len(onsets)))
    if add_events:
        annot_orig, ch_names_orig, _ = _load_data(raw)
        annot += annot_orig
        ch_names += [ch for ch in ch_names_orig if ch not in ch_names]
        overwrite = True
    annot.save(op.join(out_dir, basename + '_annot.fif'), overwrite=overwrite)
    with open(op.join(out_dir, basename + '_ch_names.tsv'), 'w') as fid:
        fid.write('\t'.join(ch_names))
    return annot, None if beh is None else beh['pd_parser_sample']


def _load_data(raw):
    """Load previously saved photodiode data--annot and pd channel names."""
    raw = _read_raw(raw, preload=None)
    fname = raw.filenames[0]
    basename = op.splitext(op.basename(fname))[0]
    out_dir = op.join(op.dirname(fname), basename + '_pd_parser_data')
    annot_fname = op.join(out_dir, basename + '_annot.fif')
    channels_fname = op.join(out_dir, basename + '_ch_names.tsv')
    behf = op.join(out_dir, basename + '_beh_df.tsv')
    if not op.isfile(annot_fname) or not op.isfile(channels_fname):
        raise ValueError(f'pd-parser data not found in {out_dir}, '
                         f'specifically, {annot_fname} and '
                         f'{channels_fname}. Either `parse_pd` was '
                         f'not run, or it failed or {out_dir} '
                         'may have been moved or deleted. Rerun '
                         '`parse_pd` and optionally `add_relative_events` '
                         'to fix this')
    with open(channels_fname, 'r') as fid:
        ch_names = fid.readline().rstrip().split('\t')
    beh_df = _read_tsv(behf) if op.isfile(behf) else None
    return mne.read_annotations(annot_fname), ch_names, beh_df


def _check_overwrite(raw, add_events, overwrite):
    """Check if the ``pd-parser`` data directory already exists."""
    basename = op.splitext(op.basename(raw.filenames[0]))[0]
    if op.isdir(op.join(op.dirname(
        raw.filenames[0]), basename + '_pd_parser_data')) and \
            not overwrite and not add_events:
        raise ValueError('Photodiode data directory already exists and '
                         'overwrite=False, set overwrite=True to overwrite')


def find_pd_params(raw, pd_ch_names=None, verbose=True):
    """Plot the data so the user can determine the right parameters.

    The user can adjust window size to determine max_len and horizontal
    line height to determine zscore.

    Parameters
    ----------
    raw: str | mne Raw object
        The object or filepath of the time-series data file
        (e.g. meg, eeg, ieeg).
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
    raw = _read_raw(raw, verbose=verbose)
    pd, _ = _get_data(raw, pd_ch_names)
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
            pd_diff = np.diff(pd)
            baseline_i = np.round(0.25 * raw.info['sfreq']).astype(int)
            median_std = np.median(
                [np.std(pd_diff[i - baseline_i:i]) for i in
                 range(baseline_i, len(pd_diff) - baseline_i, baseline_i)])
            zy = plot_data['zscore'].get_ydata()[0]
            recs['zscore'] = zy / median_std
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
                'half way up the photodiode onset event with the baseline \n'
                'in the middle of the y-axis\n'
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


def parse_pd(raw, pd_event_name='Fixation', beh=None,
             beh_key='fix_onset_time', pd_ch_names=None,
             exclude_shift=0.03, resync=0.075, max_len=1., zscore=10,
             max_flip_i=40, baseline=0.25, add_events=False, recover=False,
             overwrite=False, verbose=True):
    """Parse photodiode events.

    Parses photodiode events from a likely very corrupted channel
    using behavioral data to sync events to determine which
    behavioral events don't have a match and are thus corrupted
    and should be excluded (while ignoring events that look like
    photodiode events but don't match behavior)

    Parameters
    ----------
    raw: str | mne Raw object
        The object or filepath of the time-series data file
        (e.g. meg, eeg, ieeg).
    pd_event_name: str
        The name of the event corresponding to the photodiode.
    beh: str | dict
        The dictionary or filepath to a tsv file with the behavioral timing.
    beh_key: str
        The key (column name) of the beh dictionary that corresponds
        to the events.
    pd_ch_names : list
        Names of the channel(s) containing the photodiode data.
        One channel is to be given for a common reference and
        two for a bipolar reference. If no channels are provided,
        the data will be plotted and the user will provide them.
    exclude_shift: float
        How many seconds different than expected from the behavior events
        to exclude that event. Use `find_pd_params` to determine if unsure.
    resync: float
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
    max_flip_i: int
        The maximum number of samples the photodiode event can take to
        transition. This shouldn't usually need to be changed unless
        the transition takes longer.
    baseline: float
        How much relative to the max_len to use to idenify the time before
        the photodiode event. This should not be changed most likely
        unless there is a specific reason/issue.
    add_events: bool
        Whether to add the events found from the current call of `parse_pd`
        to a events found previously (e.g. first parse with
        `pd_event_name='Fixation'` and then parse with
        `pd_event_name='Response'`.
        Note: `pd_parser.add_relative_events` will be relative to the
        first event added.
    recover: bool
        Whether to recover corrupted events manually.
    verbose: bool
        Whether to display or supress text output on the progress
        of the function.
    overwrite: bool
        Whether to overwrite existing data if it exists.

    Returns
    -------
    annot: mne.Annotations
        The annotations with the added events.
    samples: list
        The samples corresponding to the events, with 'n/a' if no event is
        found.

    """
    if baseline <= 0 or baseline > 1:
        raise ValueError(f'baseline must be between 0 and 1, got {baseline}')
    # load raw data file with the photodiode data
    raw = _read_raw(raw, verbose=verbose)
    # check if already parsed
    _check_overwrite(raw, add_events, overwrite)
    # use keyword argument if given, otherwise get the user
    # to enter pd names and get data
    pd, pd_ch_names = _get_data(raw, pd_ch_names)
    candidates = _find_pd_candidates(
        pd=pd, max_len=max_len, baseline=baseline, zscore=zscore,
        max_flip_i=max_flip_i, sfreq=raw.info['sfreq'], verbose=verbose)[0]
    # load behavioral data with which to validate event timing
    if beh is None:
        if verbose:
            print('No behavioral tsv file was provided so the photodiode '
                  'events will be returned without validation by task '
                  'timing')
        _save_data(raw=raw, events=candidates, event_id=pd_event_name,
                   ch_names=pd_ch_names, overwrite=overwrite)
        return
    # if behavior is given use it to synchronize and exclude events
    beh_events, beh = _load_beh(beh=beh, beh_key=beh_key)
    beh_events *= raw.info['sfreq']  # convert to samples
    beh_events_adjusted, alignment, events = _find_best_alignment(
        beh_events=beh_events, candidates=candidates,
        exclude_shift=exclude_shift, resync=resync, sfreq=raw.info['sfreq'],
        verbose=verbose)
    events = _exclude_ambiguous_events(
        beh_events=beh_events_adjusted, alignment=alignment, events=events,
        ch_data=pd, candidates=candidates, exclude_shift=exclude_shift,
        max_len=max_len, sfreq=raw.info['sfreq'], recover=recover,
        zscore=zscore, verbose=verbose)
    return _save_data(raw=raw, events=events, event_id=pd_event_name,
                      ch_names=pd_ch_names, beh=beh,
                      add_events=add_events, overwrite=overwrite)


def parse_audio(raw, audio_event_name='Tone', beh=None,
                beh_key='tone_onset_time', audio_ch_names=None,
                exclude_shift=0.03, resync=0.075, max_len=0.25,
                zscore=None, add_events=False, recover=False,
                overwrite=False, verbose=True):
    """Parse audio events.

    Parses photodiode events from a likely very corrupted channel
    using behavioral data to sync events to determine which
    behavioral events don't have a match and are thus corrupted
    and should be excluded (while ignoring events that look like
    photodiode events but don't match behavior)

    Parameters
    ----------
    raw: str | mne Raw object
        The object or filepath of the time-series data file
        (e.g. meg, eeg, ieeg).
    audio_event_name: str
        The name of the event corresponding to the audio.
    beh: str | dict
        The dictionary or filepath to a tsv file with the behavioral timing.
    beh_key: str
        The key (column name) of the beh dictionary that corresponds
        to the events.
    audio_ch_names: list
        Names of the channel(s) containing the audio data.
        One channel is to be given for a common reference and
        two for a bipolar reference. If no channels are provided,
        the data will be plotted and the user will provide them.
    exclude_shift: float
        How many seconds different than expected from the behavior events
        to exclude that event.
    resync: float
        The number of seconds to difference allowed to still use an audio event
        event to resynchronize with time-stamped events. See
        :func:`pd_parser.parse_pd` for more information.
    max_len: float
        The longest audio event can be.
    zscore: float
        How large of a z-score difference to use to threshold the correlation
        of the audio with the sound. If None is passed a plot will be shown to
        pick a reasonable zscore. 25 is a typical value that works.
    add_events: bool
        Whether to add the events found from the current call of `parse_pd`
        to a events found previously (e.g. first parse with
        `pd_event_name='Fixation'` and then parse with
        `pd_event_name='Response'`.
        Note: `pd_parser.add_relative_events` will be relative to the
        first event added.
    recover: bool
        Whether to recover corrupted events manually.
    verbose: bool
        Whether to display or supress text output on the progress
        of the function.
    overwrite: bool
        Whether to overwrite existing data if it exists.

    Returns
    -------
    annot: mne.Annotations
        The annotations with the added events.
    samples: list
        The samples corresponding to the events, with 'n/a' if no event is
        found.

    """
    if resync < exclude_shift:
        raise ValueError(f'`exclude_shift` ({exclude_shift}) cannot be longer '
                         f'than `resync` ({resync})')
    # load raw data file with the photodiode data
    raw = _read_raw(raw, verbose=verbose)
    # check if already parsed
    _check_overwrite(raw, add_events, overwrite)
    # use keyword argument if given, otherwise get the user
    # to enter pd names and get data
    audio, audio_ch_names = _get_data(raw, audio_ch_names)
    candidates = _find_audio_candidates(
        audio=audio, max_len=max_len, zscore=zscore,
        sfreq=raw.info['sfreq'], verbose=verbose)
    # load behavioral data with which to validate event timing
    if beh is None:
        if verbose:
            print('No behavioral tsv file was provided so the photodiode '
                  'events will be returned without validation by task '
                  'timing')
        _save_data(raw=raw, events=candidates, event_id=audio_event_name,
                   ch_names=audio_ch_names, overwrite=overwrite)
        return
    # if behavior is given use it to synchronize and exclude events
    beh_events, beh = _load_beh(beh=beh, beh_key=beh_key)
    beh_events *= raw.info['sfreq']  # convert to samples
    beh_events_adjusted, alignment, events = _find_best_alignment(
        beh_events=beh_events, candidates=candidates,
        exclude_shift=exclude_shift, resync=resync, sfreq=raw.info['sfreq'],
        verbose=verbose)
    events = _exclude_ambiguous_events(
        beh_events=beh_events_adjusted, alignment=alignment, events=events,
        ch_data=audio, candidates=candidates, exclude_shift=exclude_shift,
        max_len=max_len, sfreq=raw.info['sfreq'], recover=recover,
        zscore=zscore, verbose=verbose)
    return _save_data(raw=raw, events=events, event_id=audio_event_name,
                      ch_names=audio_ch_names, beh=beh,
                      add_events=add_events, overwrite=overwrite)


def add_pd_off_events(raw, off_event_name='Stim Off', max_len=1., zscore=10,
                      max_flip_i=40, baseline=0.25, verbose=True,
                      overwrite=False):
    """Add events for when the photodiode deflection returns to baseline.

    Parameters
    ----------
    raw: str | mne Raw object
        The object or filepath of the time-series data file
        (e.g. meg, eeg, ieeg).
    off_event : str
        If None, no event will be assigned to cessation of the photodiode
        deflection. If a string is provided, an event of that name will
        be assigned to the cessation of the deflection.
    max_len: float
        The maximum length of the photodiode events.
    zscore: float
        How large of a z-score difference to use to threshold photodiode
        events.
    max_flip_i: int
        The maximum number of samples the photodiode event may take to
        transition.
    baseline: float
        How much relative to max_len to use to idenify the time before
        the photodiode event.
    verbose : bool
        Whether to display or supress text output on the progress
        of the function.
    overwrite : bool
        Whether to overwrite existing data if it exists.

    Returns
    -------
    annot: mne.Annotations
        The annotations with the added events.

    .. note::
       The same parameters must be used for :func:`pd_parser.parse_pd`.
    """
    raw = _read_raw(raw, verbose=verbose)
    annot, pd_ch_names, beh = _load_data(raw)
    max_len_i = np.round(raw.info['sfreq'] * max_len).astype(int)
    pd = _get_channel_data(raw, pd_ch_names)
    events = {samp: i for i, samp in enumerate(beh['pd_parser_sample'])
              if samp != 'n/a'}
    on_candidates, off_candidates = _find_pd_candidates(
        pd=pd, max_len=max_len, baseline=baseline, zscore=zscore,
        max_flip_i=max_flip_i, sfreq=raw.info['sfreq'], verbose=verbose)
    off_events = {events[onset]: offset for onset, offset in
                  zip(on_candidates, off_candidates) if onset in events}
    recovered = [event_idx for event_idx in events.values()
                 if event_idx not in off_events.keys()]
    if recovered:  # some events found manually, recover
        for idx in recovered:
            # from half of max length, look backward and forward half
            beh_e = \
                beh['pd_parser_sample'][idx] + max_flip_i + max_len_i // 2
            event, text = _recover_event(idx, pd, beh_e, max_len / 2,
                                         zscore, max_len, raw.info['sfreq'])
            if not np.isnan(event):
                off_events[idx] = event
            if verbose:
                print(text.replace('\n', ' '))
    onsets = np.array(list(off_events.values()))
    annot += mne.Annotations(
        onset=raw.times[onsets], duration=np.repeat(0.1, onsets.size),
        description=np.repeat(off_event_name, onsets.size))
    # save modified data
    basename = op.splitext(op.basename(raw.filenames[0]))[0]
    out_dir = op.join(op.dirname(raw.filenames[0]),
                      basename + '_pd_parser_data')
    annot.save(op.join(out_dir, basename + '_annot.fif'), overwrite=True)
    return annot


def add_relative_events(raw, beh, relative_event_keys,
                        relative_event_names=None,
                        overwrite=False, verbose=True):
    """Add events relative to those determined from the photodiode.

    Parameters
    ----------
    raw: str | mne Raw object
        The object or filepath of the time-series data file
        (e.g. meg, eeg, ieeg).
    beh: str | dict
        The dictionary or filepath to a tsv file with the behavioral timing.
    relative_event_keys : list
        The names of the keys where time data is stored
        relative to the photodiode event
    relative_event_names : list
        The names of the events in `relative_event_keys`.
    verbose: bool
        Whether to display or supress text output on the progress
        of the function.
    overwrite: bool
        Whether to overwrite existing data if it exists.

    Returns
    -------
    annot: mne.Annotations
        The annotations with the added events.

    """
    if relative_event_names is None:
        if verbose:
            print('Using relative event keys {} as relative event '
                  'names'.format(', '.join(relative_event_keys)))
        relative_event_names = relative_event_keys
    if len(relative_event_keys) != len(relative_event_names):
        raise ValueError(
            'Mismatched length of relative event behavior '
            f'file keys (column names), {len(relative_event_keys)} and '
            f'names of the events {len(relative_event_names)}')
    raw = _read_raw(raw, verbose=verbose)
    relative_events = \
        {name: _load_beh(beh, rel_event)[0]
         for name, rel_event in zip(relative_event_names, relative_event_keys)}
    annot, _, beh = _load_data(raw)
    for event_name in relative_event_names:
        if event_name in annot.description:
            if overwrite:
                annot.delete([i for i, desc in enumerate(annot.description)
                              if desc == event_name])
            else:
                raise ValueError(f'Event name {event_name} already exists in '
                                 'saved events and `overwrite=False`, use '
                                 '`overwrite=True` to overwrite')
    events = {i: samp for i, samp in enumerate(beh['pd_parser_sample'])
              if samp != 'n/a'}
    for name, beh_events in relative_events.items():
        onsets = np.array([events[i] + (beh_events[i] * raw.info['sfreq'])
                           for i in sorted(events.keys())
                           if not np.isnan(beh_events[i])]).round().astype(int)
        annot += mne.Annotations(onset=raw.times[onsets],
                                 duration=np.repeat(0.1, onsets.size),
                                 description=np.repeat(name, onsets.size))
    # save modified data
    basename = op.splitext(op.basename(raw.filenames[0]))[0]
    out_dir = op.join(op.dirname(raw.filenames[0]),
                      basename + '_pd_parser_data')
    annot.save(op.join(out_dir, basename + '_annot.fif'), overwrite=True)
    return annot


def add_events_to_raw(raw, keep_pd_channels=False, verbose=True):
    """Save out a new raw file with photodiode events.

    Note: this function is not recommended, rather just skip it and
    use `save_to_bids` which doesn't modify the underlying raw data
    especially converting it to fif if it isn't fif already. In
    `save_to_bids` the raw file itself doens't contain the event
    information, it's only stored in the sidecar.

    Parameters
    ----------
    raw: str | mne Raw object
        The object or filepath of the time-series data file
        (e.g. meg, eeg, ieeg).
    keep_pd_channels : bool
        Whether to keep the channel(s) the photodiode data was on.
    verbose: bool
        Whether to display or supress text output on the progress
        of the function.

    Returns
    -------
    raw : mne.io.Raw
        The modified raw object with events.

    """
    raw = _read_raw(raw, verbose=verbose)
    annot, pd_ch_names, _ = _load_data(raw)
    raw.set_annotations(annot)
    chs = [ch for ch in pd_ch_names if ch in raw.ch_names]
    if not keep_pd_channels and chs and not chs == raw.ch_names:
        raw.drop_channels(chs)
    return raw


def save_to_bids(bids_dir, raw, sub, task, ses=None, run=None,
                 data_type=None, eogs=None, ecgs=None, emgs=None,
                 verbose=True, overwrite=False):
    """Convert data to BIDS format with events found from the photodiode.

    Parameters
    ----------
    bids_dir: str
        The subject directory in the bids directory where the data
        should be saved.
    raw: str | mne Raw object
        The object or filepath of the time-series data file
        (e.g. meg, eeg, ieeg).
    sub: str
        The name of the subject.
    task: str
        The name of the task.
    ses: str
        The name of the session (optional).
    run: str
        The name of the run (optional).
    data_type: str
        The type of the channels containing data, i.e. 'eeg' or 'seeg'.
    eogs: list | None
        The channels recording eye electrophysiology.
    ecgs: list | None
        The channels recording heart electrophysiology.
    emgs: list | None
        The channels recording muscle electrophysiology.
    beh: None | str | dict
        The dictionary or filepath to a tsv file with the behavioral timing.
        If None, the stored data is used.
    verbose: bool
        Whether to display or supress text output on the progress
        of the function.
    overwrite: bool
        Whether to overwrite existing data if it exists.

    """
    import mne_bids
    if not op.isdir(bids_dir):
        os.makedirs(bids_dir)
    raw = _read_raw(raw, preload=False, verbose=verbose)
    aux_chs = list()
    for name, ch_list in zip(['eog', 'ecg', 'emg'], [eogs, ecgs, emgs]):
        if ch_list is not None:
            aux_chs += ch_list
            raw.set_channel_types({ch: name for ch in ch_list})
    if data_type is not None:
        raw.set_channel_types({ch: data_type for ch in raw.ch_names if
                               ch not in aux_chs})
    annot, pd_channels, beh = _load_data(raw)
    raw.set_annotations(annot)
    events, event_id = mne.events_from_annotations(raw)
    raw.info['bads'] += [ch for ch in pd_channels
                         if ch not in raw.info['bads']]
    # raw.set_channel_types({ch: 'stim' for ch in pd_channels
    #                        if ch in raw.ch_names})
    bids_path = mne_bids.BIDSPath(subject=sub, session=ses, task=task,
                                  run=run, root=bids_dir)
    mne_bids.write_raw_bids(raw, bids_path, verbose=verbose,
                            overwrite=overwrite)
    beh_path = bids_path.copy().update(datatype='beh')
    if not op.isdir(op.dirname(beh_path.fpath)):
        os.makedirs(op.dirname(beh_path.fpath))
    if beh is not None:
        _to_tsv(str(beh_path.fpath) + '_beh.tsv', beh)


def simulate_pd_data(n_events=10, n_secs_on=1.0, amp=300., iti=6.,
                     iti_jitter=1.5, rc_decay=0.0001, prop_corrupted=0.1,
                     sfreq=1000., seed=11, show=False):
    """Simulate photodiode data.

    Simulate data that is a square wave with a linear change in deflection
    `drift` amount towards zero that then over shoots and drifts back as
    photodiodes tend to do. Some events are also corrupted.

    Parameters
    ----------
    n_events: float
        The number of events to simulate.
    n_secs_on: float | np.array
        The number of seconds each event is on. If a float is provided, the
        time is the same for each event. If an array is provided, it must be
        the length of the number of events, and it determines the length of
        each event respectively.
    amp: float
        The amplitude of the photodiode in standard deviations above baseline.
    iti: float
        The interval in between events.
    iti_jitter: float
        The jitter displacing the events from exactly `iti` distance
        away from each other.
    rc_decay: float
        The factor controlling how much the photodiode decays back to baseline
        over time with no external simulus (0. == perfect square wave).
    sfreq: float
        The sampling frequency of the data.
    show: bool
        Whether to plot the data.

    Returns
    -------
    raw: mne.io.Raw
        The raw object containing the photodiode data
    beh: dict
        A dictionary with keys (columns names):

            `trial` : int
                The index of the event.

            `time` : float
                The time that both the corrupted and uncorrupted events
                occurred in seconds.

    events: np.array
        The uncorrupted events where the first column is the time stamp,
        the second column is unused (zero) and the third column is the
        event identifier.
    corrupted_indices: np.array
        The indices of the events which were corrupted in the simulation.
    """
    if isinstance(n_secs_on, list) and len(n_secs_on) != n_events:
        raise ValueError('If a list of `n_secs_on` is provided, it must '
                         f'match the number of events, {n_events}, got '
                         f'{len(n_secs_on)}')
    assert rc_decay >= 0 and iti > 0 and iti_jitter > 0
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
    n_secs_on_mean = n_secs_on if isinstance(n_secs_on, (float, int)) else \
        np.array(n_secs_on).max()
    n_points = events[:, 0].max() + int(10 * n_secs_on_mean * sfreq)
    n_points += n_points % 2  # must be even
    x = np.random.randn(n_points // 2) + np.random.randn(n_points // 2) * 1j
    x /= np.sqrt(np.arange(1, x.size + 1))
    pd_data = np.fft.irfft(x).real
    pd_data /= pd_data.std()
    # add photodiode square waves to pink noise
    flip_data = np.zeros((pd_data.shape))
    for i in range(n_events):
        event = events[i, 0]
        n_on = n_samp_on[i]
        next_event = events[i + 1, 0] - n_on if i < n_events - 1 else \
            pd_data.size - n_on
        flip_data[event] += amp
        for i in range(1, n_on):  # on decay
            flip_data[event + i] += flip_data[event + i - 1] * (1 - rc_decay)
        flip_data[event + n_on - 1] -= amp * ((1 - rc_decay)**(n_on / 2))
        max_i = min([next_event - event, int(i / rc_decay), int(10 * sfreq)])
        for i in range(max_i):
            flip_data[event + n_on + i] += \
                flip_data[event + n_on + i - 1] * (1 - rc_decay)
    pd_data += flip_data
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
            pd_data[ts - n_on // 10: ts + n_on // 10] += \
                (np.random.random() - 0.5) * 5 * amp - amp
    beh = dict(trial=np.arange(n_events),
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
    return raw, beh, events, corrupted_indices
