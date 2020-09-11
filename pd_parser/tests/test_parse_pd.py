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
import platform
from subprocess import call

import pytest

import matplotlib.pyplot as plt
import mne
from mne.utils import _TempDir, run_subprocess

import pd_parser
from pd_parser.parse_pd import (_read_tsv, _to_tsv,
                                _read_raw, _load_beh_df, _get_pd_data,
                                _find_pd_candidates, _pd_event_dist,
                                _check_alignment, _find_best_alignment,
                                _exclude_ambiguous_events,
                                _save_pd_data, _load_pd_data)

basepath = op.join(op.dirname(pd_parser.__file__), 'tests', 'data')

behf = op.join(basepath, 'pd_beh.tsv')
events = _read_tsv(op.join(basepath, 'pd_events.tsv'))
events_relative = _read_tsv(op.join(basepath, 'pd_relative_events.tsv'))

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

pd_event_name = 'Fixation'
beh_col = 'fix_onset_time'
pd_ch_names = ['pd']
exclude_shift = 0.03
chunk = 2
zscore = 20
min_i = 10
baseline = 0.25
resync = 0.075


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


def test_core():
    out_dir = _TempDir()
    # test tsv
    df = dict(test=[1, 2], test2=[2, 1])
    _to_tsv(op.join(out_dir, 'test.tsv'), df)
    assert df == _read_tsv(op.join(out_dir, 'test.tsv'))
    with pytest.raises(ValueError, match='Unable to read'):
        _read_tsv('test.foo')
    with pytest.raises(ValueError, match='Error in reading tsv'):
        with open(op.join(out_dir, 'test.tsv'), 'w') as _:
            pass
        _read_tsv(op.join(out_dir, 'test.tsv'))
    with pytest.raises(ValueError, match='contains no data'):
        with open(op.join(out_dir, 'test.tsv'), 'w') as f:
            f.write('test')
        _read_tsv(op.join(out_dir, 'test.tsv'))
    with pytest.raises(ValueError, match='different lengths'):
        with open(op.join(out_dir, 'test.tsv'), 'w') as f:
            f.write('test\ttest2\n1\t1\n1')
        _read_tsv(op.join(out_dir, 'test.tsv'))
    with pytest.raises(ValueError, match='Empty data file, no keys'):
        _to_tsv(op.join(out_dir, 'test.tsv'), dict())
    with pytest.raises(ValueError, match='Unable to write'):
        _to_tsv('foo.bar', dict(test=1))
    # test read
    raw, events = pd_parser.simulate_pd_data(n_secs_on=1.)
    raw.save(op.join(out_dir, 'test-raw.fif'), overwrite=True)
    with pytest.raises(ValueError, match='not recognized'):
        _read_raw('foo.bar')
    raw2 = _read_raw(op.join(out_dir, 'test-raw.fif'))
    np.testing.assert_array_almost_equal(raw._data, raw2._data, decimal=5)
    # test load beh
    with pytest.raises(ValueError, match='not in the columns'):
        _load_beh_df(op.join(basepath, 'pd_events.tsv'), 'foo')
    # test get pd data
    raw, events = pd_parser.simulate_pd_data()
    with pytest.raises(ValueError, match='not in raw channel names'):
        _get_pd_data(raw, ['foo'])
    # test find pd candidates
    exclude_shift_i = np.round(raw.info['sfreq'] * exclude_shift).astype(int)
    chunk_i = np.round(raw.info['sfreq'] * chunk).astype(int)
    baseline_i = np.round(chunk_i * baseline / 2).astype(int)
    resync_i = np.round(raw.info['sfreq'] * resync).astype(int)
    pd_candidates, sorted_pds = _find_pd_candidates(
        raw._data[0], chunk_i=chunk_i, baseline_i=baseline_i,
        zscore=zscore, min_i=min_i)
    assert all([event in sorted_pds for event in sorted_pds])
    # test pd event dist
    assert _pd_event_dist(len(raw) + 10, pd_candidates, len(raw),
                          exclude_shift_i) == exclude_shift_i
    assert _pd_event_dist(events[2, 0] + 10, pd_candidates, len(raw),
                          exclude_shift_i) == 10
    assert _pd_event_dist(events[2, 0] - 10, pd_candidates, len(raw),
                          exclude_shift_i) == -10
    # test find best alignment
    np.random.seed(12)
    beh_events = events[2:, 0].astype(float)
    offsets = (np.random.random(len(beh_events)) * 0.03 - 0.015
               ) * raw.info['sfreq']
    beh_events += offsets
    beh_events = {i: beh_ev - beh_events[0] for i, beh_ev in
                  enumerate(beh_events)}
    beh_events_sorted = np.array(sorted(beh_events.values()))
    beh_df = dict(fix_onset_time=beh_events_sorted,
                  trial=np.arange(len(beh_events_sorted)))
    errors = _check_alignment(beh_events_sorted + sorted_pds[2],
                              pd_candidates, sorted_pds[-1],
                              resync_i)
    assert all([e < exclude_shift_i for e in errors])
    best_alignment = _find_best_alignment(beh_events_sorted, sorted_pds,
                                          resync_i, raw.info['sfreq'],
                                          verbose=True)
    assert abs(best_alignment - sorted_pds[2]) < exclude_shift_i
    # test exclude ambiguous
    pd = raw._data[0]
    pd_events = _exclude_ambiguous_events(
        beh_events, sorted_pds, best_alignment, pd, exclude_shift_i, chunk_i,
        resync_i, raw.info['sfreq'], verbose=True)
    np.testing.assert_array_equal(list(pd_events.values()), events[2:, 0])
    # test i/o
    fname = op.join(out_dir, 'test-raw.fif')
    _save_pd_data(fname, raw, events=pd_events,
                  event_id='Fixation', pd_ch_names=['pd'],
                  beh_df=beh_df, add_events=False)
    with pytest.raises(ValueError, match='The column name `pd_sample`'):
        _save_pd_data(fname, raw, events=pd_events,
                      event_id='Fixation', pd_ch_names=['pd'],
                      beh_df=beh_df, add_events=False)
    annot, pd_ch_names, beh_df = _load_pd_data(fname)
    with pytest.raises(ValueError, match='Photodiode data not found'):
        annot, pd_ch_names, beh_df = _load_pd_data('bar/foo.fif')
    raw.set_annotations(annot)
    events2, event_id = mne.events_from_annotations(raw)
    np.testing.assert_array_equal(events2[:, 0], events[2:, 0])
    assert event_id == {'Fixation': 1}
    assert pd_ch_names == ['pd']
    np.testing.assert_array_equal(beh_df['fix_onset_time'], beh_events_sorted)
    assert beh_df['pd_sample'] == list(pd_events.values())
    # check overwrite
    behf = op.join(out_dir, 'behf-test.tsv')
    _to_tsv(behf, beh_df)
    with pytest.raises(ValueError, match='directory already exists'):
        pd_parser.parse_pd(fname, behf=behf)
    pd_parser.parse_pd(fname, behf=None, pd_ch_names=['pd'], overwrite=True)
    annot, pd_ch_names, beh_df = _load_pd_data(fname)
    raw.set_annotations(annot)
    events2, _ = mne.events_from_annotations(raw)
    assert all([event in events2[:, 0] for event in events[:, 0]])
    assert pd_ch_names == ['pd']
    assert beh_df is None
    # test when resync is needed
    with pytest.raises(ValueError, match='cannot be longer'):
        pd_parser.parse_pd(fname, behf=behf, exclude_shift=1, resync=0.5)
    beh_events = events[2:, 0].astype(float)
    offsets = (np.random.random(len(beh_events)) * 0.07 - 0.035
               ) * raw.info['sfreq']
    beh_events += offsets
    beh_events = {i: beh_ev - beh_events[0] for i, beh_ev in
                  enumerate(beh_events)}
    beh_events_sorted = np.array(sorted(beh_events.values()))
    beh_df = dict(fix_onset_time=beh_events_sorted,
                  trial=np.arange(len(beh_events_sorted)))
    errors = _check_alignment(beh_events_sorted + sorted_pds[2],
                              pd_candidates, sorted_pds[-1],
                              resync_i)
    resync_exclusions = np.where(abs(errors) > exclude_shift_i)[0]
    assert len(resync_exclusions) > 0
    assert abs(best_alignment - sorted_pds[2]) < exclude_shift_i
    # test exclude ambiguous
    pd = raw._data[0]
    pd_events = _exclude_ambiguous_events(
        beh_events, sorted_pds, best_alignment, pd, exclude_shift_i, chunk_i,
        resync_i, raw.info['sfreq'], verbose=True)
    np.testing.assert_array_equal(list(pd_events.values()),
                                  np.delete(events[2:, 0], resync_exclusions))


def test_two_pd_alignment():
    """Test spliting photodiode events into two and adding."""
    out_dir = _TempDir()
    raw, events = pd_parser.simulate_pd_data()
    fname = op.join(out_dir, 'test-raw.fif')
    raw.save(fname)
    events2 = events[::2]
    events3 = events[1:][::2]
    # make behavior data
    np.random.seed(12)
    beh_events2 = events2[:, 0].astype(float) / raw.info['sfreq']
    offsets2 = np.random.random(len(beh_events2)) * 0.05 - 0.025
    beh_events2 += offsets2
    # make next one
    beh_events3 = events3[:, 0].astype(float) / raw.info['sfreq']
    offsets3 = np.random.random(len(beh_events3)) * 0.05 - 0.025
    beh_events3 += offsets3
    n_na = abs(len(beh_events2) - len(beh_events3))
    if len(beh_events2) > len(beh_events3):
        beh_events3 = list(beh_events3) + ['n/a'] * n_na
    elif len(beh_events3) > len(beh_events2):
        beh_events2 = list(beh_events2) + ['n/a'] * n_na
    beh_df = dict(trial=np.arange(len(beh_events2)),
                  fix_onset_time=beh_events2,
                  response_onset_time=beh_events3)
    behf = op.join(out_dir, 'behf-test.tsv')
    _to_tsv(behf, beh_df)
    pd_parser.parse_pd(fname, pd_event_name='Fixation', behf=behf,
                       pd_ch_names=['pd'], beh_col='fix_onset_time',
                       zscore=20, exclude_shift=0.05)
    pd_parser.parse_pd(fname, pd_event_name='Response', behf=behf,
                       pd_ch_names=['pd'], beh_col='response_onset_time',
                       zscore=20, add_events=True, exclude_shift=0.05)
    annot, pd_ch_names, beh_df2 = _load_pd_data(fname)
    raw.set_annotations(annot)
    events4, event_id = mne.events_from_annotations(raw)
    np.testing.assert_array_equal(events4[events4[:, 2] == 1, 0],
                                  events2[:, 0])
    np.testing.assert_array_equal(events4[events4[:, 2] == 2, 0],
                                  events3[:, 0])
    assert pd_ch_names == ['pd']
    np.testing.assert_array_equal(beh_df2['pd_sample'], events2[:, 0])


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_parse_pd(_bids_validate):
    # load in data
    out_dir = _TempDir()
    fname = op.join(out_dir, 'pd_data-raw.fif')
    raw_tmp.save(fname)
    # this needs to be tested with user interaction, this
    # just tests that it launches
    pd_parser.find_pd_params(fname, pd_ch_names=['pd'])
    plt.close('all')
    # test core functionality
    pd_parser.parse_pd(fname, behf=behf, pd_ch_names=['pd'],
                       exclude_shift=0.05)
    plt.close('all')
    raw = mne.io.read_raw_fif(fname)
    annot, pd_ch_names, beh_df = _load_pd_data(fname)
    raw.set_annotations(annot)
    events2, event_id = mne.events_from_annotations(raw)
    np.testing.assert_array_equal(events2[:, 0], events['pd_sample'])
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
    np.testing.assert_array_equal(events2[:, 0], events_relative['sample'])
    assert pd_ch_names == ['pd']
    np.testing.assert_array_equal(
        events2[:, 2], [event_id[tt] for tt in events_relative['trial_type']])
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


def test_cli():
    out_dir = _TempDir()
    fname = op.join(out_dir, 'pd_data-raw.fif')
    raw_tmp.save(fname)
    # can't test with a live plot, but if this should be called by hand
    # call([f'find_pd_params {fname} --pd_ch_names pd'], shell=True,
    #      env=os.environ)
    assert call([f'parse_pd {fname} --behf {behf} --pd_ch_names pd'],
                shell=True, env=os.environ) == 0
    assert call([f'add_pd_relative_events {fname} --behf {behf} '
                 '--relative_event_cols fix_duration go_time response_time '
                 '--relative_event_names "ISI Onset" "Go Cue" "Response"'],
                shell=True, env=os.environ) == 0
    assert call([f'add_pd_events_to_raw {fname} --drop_pd_channels False'],
                shell=True, env=os.environ) == 0
    bids_dir = op.join(out_dir, 'bids_dir')
    assert call([f'pd_parser_save_to_bids {bids_dir} {fname} 1 test'],
                shell=True, env=os.environ) == 0
