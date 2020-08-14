# -*- coding: utf-8 -*-
"""Test the pd_parsing.

For each supported file format, implement a test.
"""
# Authors: Alex Rockhill <aprockhill@mailbox.org>
#
# License: BSD (3-clause)

import os
import os.path as op
import numpy as np

import pytest

import mne
from mne.utils import _TempDir

import pd_parser
from pd_parser.parse_pd import _load_pd_data, _read_tsv

basepath = op.join(op.dirname(pd_parser.__file__), 'tests', 'data')
out_dir = _TempDir()

fname = op.join(out_dir, 'pd_data-raw.fif')
behf = op.join(basepath, 'pd_beh.tsv')
events = _read_tsv(op.join(basepath, 'pd_events.tsv'))
events_relative = _read_tsv(op.join(basepath, 'pd_events_relative.tsv'))

raw_tmp = mne.io.read_raw_fif(op.join(basepath, 'pd_data-raw.fif'),
                              preload=True)
info = mne.create_info(['ch1', 'ch2', 'ch3'], raw_tmp.info['sfreq'],
                       ['seeg'] * 3)
raw_tmp2 = mne.io.RawArray(np.random.random((3, raw_tmp.times.size)) * 1e-6,
                           info)
raw_tmp2.info['lowpass'] = raw_tmp.info['lowpass']
raw_tmp.add_channels([raw_tmp2])
raw_tmp.save(fname)


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_parse_pd():
    # this needs to be tested with user interaction, this
    # just tests that it launches
    pd_parser.find_pd_params(fname, pd_ch_names=['pd'])
    # test core functionality
    pd_parser.parse_pd(fname, behf=behf, pd_ch_names=['pd'],
                       alignment_prop=0.05)  # reduce alignment_prop -> faster
    raw = mne.io.read_raw_fif(fname)
    annot, pd_ch_names, beh_df = _load_pd_data(fname)
    raw.set_annotations(annot)
    events2, event_id = mne.events_from_annotations(raw)
    assert all(events2[:, 0] == events['pd_sample'])
    assert pd_ch_names == ['pd']
    event_indices = [i for i, s in enumerate(beh_df['pd_sample'])
                     if s != 'n/a']
    assert all(event_indices == events['trial'])
    assert all([beh_df['pd_sample'][j] == events['pd_sample'][i]
                for i, j in enumerate(event_indices)])
    # test add_pd_relative_events
    pd_parser.add_pd_relative_events(
        fname, behf,
        relative_event_cols=['fix_duration', 'go_time', 'response_time'],
        relative_event_names=['ISI Onset', 'Go Cue', 'Response'])
    annot, pd_ch_names, beh_df = _load_pd_data(fname)
    raw.set_annotations(annot)
    events2, event_id = mne.events_from_annotations(raw)
    assert all(events2[:, 0] == events_relative['sample'])
    assert pd_ch_names == ['pd']
    assert all(events2[:, 2] == [event_id[tt] for tt in
                                 events_relative['trial_type']])
    # test add_pd_events_to_raw
    out_fname = pd_parser.add_pd_events_to_raw(fname, drop_pd_channels=False)
    raw2 = mne.io.read_raw_fif(out_fname)
    events3, event_id2 = mne.events_from_annotations(raw2)
    np.testing.assert_array_equal(events3, events2)
    assert event_id2 == event_id
    # test pd_parser_save_to_bids
    bids_dir = op.join(out_dir, 'bids_dir')
    os.makedirs(bids_dir)
    pd_parser.pd_parser_save_to_bids(bids_dir, '1', 'test')


def simulate_pd_data(sfreq=512):
    """Simulates photodiode data."""
    info = mne.create_info(['pd'], sfreq, ['stim'])
    data = np.zeros((1, 1000))
    raw = mne.RawArray(data, info)
    return raw
