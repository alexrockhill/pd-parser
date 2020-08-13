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
from shutils import copyfile
import numpy as np

from pandas import read_csv
from tqdm import tqdm

import mne


def _read_raw(fname, verbose=True):
    _, ext = op.splitext(fname)
    """Read raw data into an mne.io.Raw object."""
    if verbose:
        print('Reading in {}'.format(fname))
    if ext == '.fif':
        raw = mne.io.read_raw_fif(fname, preload=False)
    elif ext == '.edf':
        raw = mne.io.read_raw_edf(fname, preload=False)
    elif ext == '.bdf':
        raw = mne.io.read_raw_bdf(fname, preload=False)
    elif ext == '.vhdr':
        raw = mne.io.read_raw_brainvision(fname, preload=False)
    elif ext == '.set':
        raw = mne.io.read_raw_eeglab(fname, preload=False)
    else:
        raise ValueError('Extension {} not recognized, options are'
                         'fif, edf, bdf, vhdr (brainvision) and set '
                         '(eeglab)'.format(ext))
    return raw


def _load_beh_df(behf, beh_col, verbose=True):
    """Load the behavioral data frame and check columns."""
    try:
        df = read_csv(behf, sep='\t')
    except Exception as e:
        if verbose:
            print(e)
        raise ValueError('Unable to read tab-separated-value (tsv) file, '
                         'check that behf is a properly formated tsv file')
    if beh_col not in df.columns:
        raise ValueError(f'beh_col {beh_col} not in the columns of '
                         f'behf {behf}. Please check that the correct '
                         'column is provided')
    return np.array(df[beh_col]), df


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
    for i in tqdm(range(len(pd_candidates) - first_alignment_n)):
        these_beh_events = beh_events.copy() + sorted_pds[i]
        errors = list()
        for b_event in these_beh_events[:first_alignment_n]:
            errors.append(_pd_event_dist(b_event, pd_candidates, max_index))
        median_error = np.median(errors)
        if min_error is None or median_error < min_error:
            best_alignment = i
            min_error = median_error
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
                print('Excluding event %i off by %i samples, ' % (i, j))
                pd_section = pd[int(b_event - 10 * sfreq):
                                int(b_event + 10 * sfreq)]
                plt.plot(np.linspace(-10, 10, pd_section.size), pd_section)
                plt.ylabel('voltage')
                plt.xlabel('time')
                plt.show()
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
                    print('%i events found for behvaior event %i, excluding' %
                          (sum(pd_events), i))
                    plt.plot(pd[int(b_event - 10 * sfreq):
                                int(b_event + 10 * sfreq)])
                    plt.show()
    if verbose:
        print(errors)
        print('Final behavior event-photodiode event differences '
              'min %i, q1 %i, med %i, q3 %i, max %i ' %
              (min(errors.values()), np.quantile(list(errors.values()), 0.25),
               np.median(list(errors.values())),
               np.quantile(list(errors.values()), 0.75), max(errors.values())))
        trials = sorted(errors.keys())
        plt.plot(trials, [errors[t] for t in trials])
        plt.ylabel('Difference (samples)')
        plt.xlabel('Trial')
        plt.title('Photodiode Events Compared to Behavior Events')
        plt.show()
    return events


def _save_pd_data(fname, raw, events, event_id, pd_ch_names, beh_df=None):
    """Saves the events determined from the photodiode."""
    basename = op.splitext(op.basename(fname))[0]
    pd_data_dir = op.join(op.dirname(fname), basename + '_pd_data')
    if not op.isdir(pd_data_dir):
        os.makedirs(pd_data_dir)
    onsets = np.array([events[i] for i in sorted(events.keys())])
    annot = mne.Annotations(onset=raw.times[onsets],
                            duration=np.repeat(0.1, len(onsets)),
                            description=np.repeat(event_id,
                                                  len(onsets)))
    events, event_id = mne.events_from_annotations(raw)
    annot.save(op.join(pd_data_dir, basename + '_pd_annot.fif'))
    with open(op.join(pd_data_dir, basename + 'pd_ch_names.tsv'), 'w') as fid:
        fid.write('\t'.join(pd_ch_names))
    if beh_df is not None:
        beh_df.to_csv(op.join(pd_data_dir, basename + '_beh_df.tsv'),
                      sep='\t', index=False)


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
                         '`parse_pd` and optionally `add_relative_events` '
                         'to fix this')
    with open(pd_channels_fname, 'r') as fid:
        pd_ch_names = fid.readline().rstrip().split('\t')
    return mne.read_annotations(annot_fname), pd_ch_names, behf


def parse_pd(fname, pd_event_name='Fixation', behf=None, beh_col=None,
             pd_ch_names=None, chunk=2, baseline=0.25, overlap=0.25,
             exclude_shift=0.1, zscore=10, min_i=10, alignment_prop=0.2,
             overwrite=False, verbose=True):
    """ Parses photodiode events from a likely very corrupted channel
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
        The filepath to a tsv file with the behavioral timing
    beh_col : str
        The column of the behf tsv that corresponds to the events
    pd_ch_names : list
        Names of the channel(s) containing the photodiode data.
        One channel is to be given for a common reference and
        two for a bipolar reference. If no channels are provided,
        the data will be plotted and the user will provide them.
    chunk: float
        The size of the window to chunk the photodiode events by
        should be larger than 2x the longest photodiode event
    baseline: float
        How much relative to the chunk to use to idenify the time before
        the photodiode event.
    overlap: float
        How much to overlap the windows of the photodiode event-finding
        process.
    exclude_shift: float
        How many seconds different than expected from the behavior events
        to exclude that event.
    zscore: float
        How large of a z-score difference to use to threshold photodiode
        events.
    min_i: int
        The minimum number of samples the photodiode event must be on for.
    alignment_prop : float
        Proportion of events to use to score the alignment to the first event.
        This number should be low to have an accurate score without the
        photodiode drifting and causing unexpected alignments (and it's
        faster).
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
    if not np.isnumeric(alignment_prop
                        ) or alignment_prop < 0 or alignment_prop > 1:
        raise ValueError(f'Cannot align using {alignment_prop} events, '
                         'alignment_prop must be between 0 and 1')
    first_alignment_n = alignment_prop * beh_events.size
    beh_events *= raw.info['sfreq']
    beh_events -= beh_events[0]
    best_alignment = _find_best_alignment(beh_events, pd_candidates,
                                          sorted_pds, first_alignment_n,
                                          verbose)
    events = _exclude_ambiguous_events(beh_events, pd_candidates, sorted_pds,
                                       pd, best_alignment, raw.info['sfreq'],
                                       chunk, exclude_shift, verbose)
    _save_pd_data(fname, raw, events, pd_event_name, pd_ch_names, beh_df)


def diagnose_parser_issues(fname, pd_ch_names=None, verbose=True):
    """ Plots the data so the user can determine the right parameters.

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
    raw = _read_raw(fname, verbose=verbose)
    pd = _get_pd_data(raw, pd_ch_names)


def add_relative_events(fname, behf, relative_event_cols,
                        relative_event_names=None,
                        overwrite=False, verbose=True):
    """ Adds events relative to those determined from the photodiode
        to the events.
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
    relative_events = [_load_beh_df(behf, rel_event) for rel_event in
                       relative_event_cols]
    relative_events = {name: rel_events for rel_events, name in
                       zip(relative_events, relative_event_names)}
    raw = _read_raw(fname, verbose=verbose)
    basename = op.splitext(op.basename(fname))[0]
    pd_data_dir = op.join(op.dirname(fname), basename + '_pd_data')
    annot_fname = op.join(pd_data_dir, basename + '_pd_annot.fif')
    if not op.isfile(annot_fname):
        raise ValueError(f'{annot_fname} does not exist, this is either '
                         'because `parse_pd` hasn\'t been run, or it failed '
                         f'to find events or {pd_data_dir} was moved '
                         'or deleted. Rerun `parse_pd` to fix this')
    annot = mne.read_annotations(annot_fname)
    events, event_id = mne.events_from_annotations(annot)
    for event_name in relative_event_names:
        if event_name in event_id and not overwrite:
            raise ValueError(f'Event name {event_name} already exists in '
                             'saved events and overwrite=False, use '
                             'overwrite=True to overwrite')
    for name, beh_array in relative_events.items():
        onsets = \
            [events[i] + int(np.round(beh_array[i] * raw.info['sfreq']))
             for i in sorted(events.keys()) if not np.isnan(beh_array[i])]
        annot += mne.Annotations(onset=raw.times[np.array(onsets)],
                                 duration=np.repeat(0.1, len(onsets)),
                                 description=np.repeat(name, len(onsets)))
    annot.save(annot_fname)


def add_events_to_raw(fname, out_fname=None, verbose=True, overwrite=False):
    """ Saves out a new raw file with photodiode events.

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
    annot, pd_ch_names = _load_pd_data()
    raw.set_annotations(annot)
    raw.drop_channels([ch for ch in pd_ch_names if ch in raw.ch_names])
    if op.splitext(out_fname)[-1] != '.fif':
        raise ValueError('Only saving as fif is supported, got '
                         f'{op.splitext(out_fname)}')
    raw.save(out_fname, overwrite=overwrite)
    return raw


def save_to_bids(bids_dir, fname, sub, task, ses=None, run=None,
                 data_type=None, eogs=None, ecgs=None, emgs=None,
                 verbose=True, overwrite=False):
    """Convert iEEG data collected at OHSU to BIDS format
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
    '''    eegf, data_ch_type, list() if eogs is None else eogs,
                   list() if ecgs is None else ecgs, list() if
                   emgs is None else emgs)
    '''
    annot, pd_channels, behf = _load_pd_data(fname)
    raw.set_annotations(annot)
    events, event_id = mne.events_from_annotations(raw)
    raw = raw.drop_channels([ch for ch in pd_channels if ch in raw.ch_names])
    mne_bids.write_raw_bids(raw, bids_basename, bids_dir,
                            events_data=events, event_id=event_id,
                            verbose=verbose, overwrite=overwrite)
    copyfile(behf, op.join(bids_beh_dir, bids_basename + '_beh.tsv'))
