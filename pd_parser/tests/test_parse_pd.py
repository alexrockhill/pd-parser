# -*- coding: utf-8 -*-
"""Test the pd_parsing.

For each supported file format, implement a test.
"""
# Authors: Alex Rockhill <aprockhill@mailbox.org>
#
# License: BSD (3-clause)

# TO DO: 1) optimize _find_best_alignment
#        2) implement pd simulation
#        3) test for more than one photodiode event

import os
import os.path as op
import numpy as np
import platform

import pytest

import mne
from mne.utils import _TempDir, run_subprocess

import pd_parser
from pd_parser.parse_pd import _load_pd_data, _read_tsv, _to_tsv

basepath = op.join(op.dirname(pd_parser.__file__), 'tests', 'data')


# from mne_bids.tests.test_write._bids_validate
@pytest.fixture(scope="session")
def _bids_validate():
    """Fixture to run BIDS validator."""
    vadlidator_args = ['--config.error=41']
    exe = os.getenv('VALIDATOR_EXECUTABLE', 'bids-validator')

    if platform.system() == 'Windows':
        shell = True
    else:
        shell = False

    bids_validator_exe = [exe, *vadlidator_args]

    def _validate(bids_root):
        cmd = [*bids_validator_exe, bids_root]
        run_subprocess(cmd, shell=shell)

    return _validate


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_parse_pd(_bids_validate):
    # load in data
    out_dir = _TempDir()
    fname = op.join(out_dir, 'pd_data-raw.fif')
    behf = op.join(basepath, 'pd_beh.tsv')
    events = _read_tsv(op.join(basepath, 'pd_events.tsv'))
    events_relative = _read_tsv(op.join(basepath, 'pd_events_relative.tsv'))

    raw_tmp = mne.io.read_raw_fif(op.join(basepath, 'pd_data-raw.fif'),
                                  preload=True)
    info = mne.create_info(['ch1', 'ch2', 'ch3'], raw_tmp.info['sfreq'],
                           ['seeg'] * 3)
    raw_tmp2 = \
        mne.io.RawArray(np.random.random((3, raw_tmp.times.size)) * 1e-6,
                        info)
    raw_tmp2.info['lowpass'] = raw_tmp.info['lowpass']
    raw_tmp.add_channels([raw_tmp2])
    raw_tmp.info['dig'] = None
    raw_tmp.info['line_freq'] = 60
    raw_tmp.save(fname)
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
    assert event_indices == events['trial']
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
    pd_parser.pd_parser_save_to_bids(bids_dir, fname, '1', 'test',
                                     verbose=False)
    _bids_validate(bids_dir)
