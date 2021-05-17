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
import mock
from subprocess import call
from scipy.io import wavfile

import pytest

import matplotlib.pyplot as plt
import mne
from mne.utils import _TempDir, run_subprocess

import pd_parser
from pd_parser.parse_pd import (_read_tsv, _to_tsv, _read_raw,
                                _load_beh, _get_channel_data,
                                _get_data, _check_if_pd_event,
                                _find_pd_candidates, _event_dist,
                                _check_alignment, _find_best_alignment,
                                _exclude_ambiguous_events,
                                _save_data, _load_data, _check_overwrite,
                                _recover_event, _find_audio_candidates,
                                _plot_trial_errors, _plot_excluded_events)

basepath = op.join(op.dirname(pd_parser.__file__), 'tests', 'data')

pd_event_name = 'Fixation'
off_event_name = 'Stim Off'
beh_key = 'fix_onset_time'
pd_ch_names = ['pd']
max_len = 1
zscore = 10
max_flip_i = 40
baseline = 0.25
exclude_shift = 0.03
resync = 0.075
recover = False
add_events = False
verbose = True
overwrite = False


def make_raw(out_dir):
    np.random.seed(99)
    raw, beh, events, corrupted = pd_parser.simulate_pd_data(seed=99)
    raw2 = mne.io.RawArray(np.random.random((3, raw._data.shape[1])),
                           mne.create_info([f'ch{i}' for i in range(3)],
                                           raw.info['sfreq'], ['eeg'] * 3))
    raw.add_channels([raw2])
    offsets = np.random.random(beh['time'].size) * 0.05 - 0.025
    beh['fix_onset_time'] = beh['time'] + offsets
    response_times = list(np.random.random(beh['time'].size))
    for i in np.random.choice(range(beh['time'].size), 3):
        response_times[i] = 'n/a'
    beh['fix_duration'] = [0.6] * beh['time'].size
    beh['go_time'] = np.random.random(beh['time'].size)
    beh['response_time'] = response_times
    fname = op.join(out_dir, 'test-raw.fif')
    raw.save(fname)
    behf = op.join(out_dir, 'behf-test.tsv')
    _to_tsv(behf, beh)
    return fname, behf, corrupted


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
def test_inputs():
    """Test that inputs for functions raise necessary errors."""
    out_dir = _TempDir()
    # test tsv
    beh = dict(test=[1, 2], test2=[2, 1])
    _to_tsv(op.join(out_dir, 'test.tsv'), beh)
    assert beh == _read_tsv(op.join(out_dir, 'test.tsv'))
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
    raw, beh, events, corrupted_indices = pd_parser.simulate_pd_data()
    with pytest.raises(ValueError, match='must be loaded from disk'):
        _read_raw(raw, preload=True)
    raw.save(op.join(out_dir, 'test-raw.fif'), overwrite=True)
    with pytest.raises(ValueError, match='not recognized'):
        _read_raw('foo.bar')
    raw2 = _read_raw(op.join(out_dir, 'test-raw.fif'), preload=True)
    np.testing.assert_array_almost_equal(raw._data, raw2._data, decimal=3)
    # test load beh
    with pytest.raises(ValueError, match='not in the columns'):
        _load_beh(op.join(basepath, 'pd_events.tsv'), 'foo')
    # test get pd data
    with pytest.raises(ValueError, match='in raw channel names'):
        _get_data(raw, ['foo'])
    with pytest.raises(ValueError, match='in raw channel names'):
        _get_channel_data(raw, ['foo'])
    with pytest.raises(ValueError, match='baseline must be between 0 and 1'):
        pd_parser.parse_pd(raw, beh=beh, baseline=2)
    with pytest.raises(FileNotFoundError, match='fname does not exist'):
        _load_data('bar/foo.fif')
    with pytest.raises(ValueError, match='pd-parser data not found'):
        raw.save(op.join(out_dir, 'foo.fif'))
        _load_data(op.join(out_dir, 'foo.fif'))
    # test i/o
    raw3 = _read_raw(op.join(out_dir, 'test-raw.fif'))
    _save_data(raw3, events=np.arange(10), event_id='Fixation',
               ch_names=['pd'], beh=beh, add_events=False)
    with pytest.raises(ValueError, match='`pd_parser_sample` is not allowed'):
        _save_data(raw3, events=events, event_id='Fixation', ch_names=['pd'],
                   beh=beh, add_events=False)
    annot, pd_ch_names, beh2 = _load_data(raw3)
    raw.set_annotations(annot)
    events2, event_id = mne.events_from_annotations(raw)
    np.testing.assert_array_equal(events2[:, 0], np.arange(10))
    assert event_id == {'Fixation': 1}
    assert pd_ch_names == ['pd']
    np.testing.assert_array_equal(beh2['time'], beh['time'])
    np.testing.assert_array_equal(beh2['pd_parser_sample'], np.arange(10))
    # check overwrite
    behf = op.join(out_dir, 'behf-test.tsv')
    _to_tsv(behf, beh)
    with pytest.raises(ValueError, match='directory already exists'):
        pd_parser.parse_pd(raw3, beh=behf)
    pd_parser.parse_pd(raw3, beh=None, pd_ch_names=['pd'], overwrite=True)
    annot, pd_ch_names, beh = _load_data(raw3)
    raw3.set_annotations(annot)
    events2, _ = mne.events_from_annotations(raw3)
    assert all([event in events2[:, 0] for event in events[:, 0]])
    assert pd_ch_names == ['pd']
    assert beh is None
    # test overwrite
    raw = _read_raw(op.join(out_dir, 'test-raw.fif'))
    with pytest.raises(ValueError, match='data directory already exists'):
        _check_overwrite(raw, add_events=False, overwrite=False)


def test_core():
    """Test the core functions of aligning photodiode events."""
    np.random.seed(121)
    raw, beh, events, corrupted_indices = pd_parser.simulate_pd_data(seed=1211)
    pd = raw._data[0]
    # test find pd candidates
    max_len = 1.5
    exclude_shift_i = np.round(raw.info['sfreq'] * exclude_shift).astype(int)
    max_len_i = np.round(raw.info['sfreq'] * max_len).astype(int)
    baseline_i = np.round(max_len_i * baseline / 2).astype(int)
    resync_i = np.round(raw.info['sfreq'] * resync).astype(int)
    pd_diff = np.diff(pd)
    pd_diff -= np.median(pd_diff)
    median_std = np.median([np.std(pd_diff[i - baseline_i:i]) for i in
                            range(baseline_i, len(pd_diff) - baseline_i,
                                  baseline_i)])
    assert _check_if_pd_event(pd_diff, events[0, 0] - 1, max_len_i, zscore,
                              max_flip_i, median_std) == \
        ('up', events[0, 0], events[0, 0] + raw.info['sfreq'])  # one sec event
    assert _check_if_pd_event(pd, baseline_i,
                              max_len_i, zscore, max_flip_i, median_std) == \
        (None, None, None)
    candidates = _find_pd_candidates(
        pd, max_len=max_len, baseline=baseline,
        zscore=zscore, max_flip_i=max_flip_i, sfreq=raw.info['sfreq'])[0]
    candidates_set = set(candidates)
    assert all([event in candidates for event in events[:, 0]])
    # test pd event dist
    assert np.isnan(_event_dist(len(raw) + 10, candidates_set, len(raw),
                                exclude_shift_i)).all()
    assert _event_dist(events[2, 0] + 10, candidates_set, len(raw),
                       exclude_shift_i) == (10, events[2, 0])
    assert _event_dist(events[2, 0] - 10, candidates_set, len(raw),
                       exclude_shift_i) == (-10, events[2, 0])
    # test find best alignment
    beh_events = beh['time'][2:] * raw.info['sfreq']
    offsets = (np.random.random(beh_events.size) * exclude_shift / 2
               ) * raw.info['sfreq']
    beh_events += offsets
    beh_events -= beh_events[0]  # throw off the alignment, make it harder
    beh_events_adjusted, best_events = _check_alignment(
        beh_events, candidates[2], candidates, candidates_set, resync_i)
    errors = beh_events_adjusted - best_events + candidates[2]
    assert all([np.isnan(e) if i + 2 in corrupted_indices
                else e < exclude_shift_i for i, e in enumerate(errors)])
    beh_events_adjusted, alignment, best_events = _find_best_alignment(
        beh_events, candidates, exclude_shift, resync, raw.info['sfreq'])
    assert abs(alignment - candidates[2]) < exclude_shift_i
    errors = beh_events_adjusted - best_events + alignment
    assert all([np.isnan(e) or abs(e) > exclude_shift_i
                if i + 2 in corrupted_indices else abs(e) < exclude_shift_i
                for i, e in enumerate(errors)])
    # test exclude ambiguous
    pd_events = _exclude_ambiguous_events(
        beh_events, alignment, best_events, pd, candidates,
        exclude_shift, max_len, raw.info['sfreq'], recover, zscore)
    assert all([i - 2 not in pd_events for i in corrupted_indices])
    np.testing.assert_array_equal(
        pd_events[~np.isnan(pd_events)], events[2:, 0])


def test_resync():
    """Test when event resynchronicazationu using ``resync`` is needed."""
    np.random.seed(12)
    raw, beh, events, corrupted_indices = \
        pd_parser.simulate_pd_data(prop_corrupted=0.)
    pd = raw._data[0]
    exclude_shift_i = np.round(raw.info['sfreq'] * exclude_shift).astype(int)
    candidates = _find_pd_candidates(
        pd, max_len=max_len, baseline=baseline,
        zscore=zscore, max_flip_i=max_flip_i, sfreq=raw.info['sfreq'])[0]
    beh_events = beh['time'] * raw.info['sfreq']
    offsets = (2 * resync * np.random.random(beh_events.size) - 1
               ) * raw.info['sfreq']
    beh_events += offsets
    beh_events -= beh_events[0]
    beh_events_adjusted, alignment, best_events = _find_best_alignment(
        beh_events, candidates, exclude_shift, resync, raw.info['sfreq'])
    errors = beh_events_adjusted - best_events + alignment
    resync_exclusions = np.where(abs(errors) > exclude_shift_i)[0]
    idx = resync_exclusions[0]
    correct = (best_events[idx], f'{idx}\nrecovered (not excluded)')
    assert len(resync_exclusions) > 0
    # test exclude ambiguous
    pd_events = _exclude_ambiguous_events(
        beh_events_adjusted, alignment, best_events, pd, candidates,
        exclude_shift, max_len, raw.info['sfreq'], recover, zscore)
    assert np.isnan(pd_events[resync_exclusions]).all()
    assert np.isnan(pd_events[np.isnan(best_events)]).all()
    with mock.patch('builtins.input', return_value='y'):
        found = _recover_event(
            idx, pd, beh_events_adjusted[idx] + alignment, 2 * resync, zscore,
            max_len, raw.info['sfreq'])
        assert abs(found[0] - correct[0]) < 2
        assert found[1] == correct[1]


def test_two_pd_alignment():
    """Test spliting photodiode events into two and adding."""
    out_dir = _TempDir()
    raw, _, events, _ = pd_parser.simulate_pd_data(prop_corrupted=0.)
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
    beh = dict(trial=np.arange(len(beh_events2)),
               fix_onset_time=beh_events2,
               response_onset_time=beh_events3)
    behf = op.join(out_dir, 'behf-test.tsv')
    _to_tsv(behf, beh)
    pd_parser.parse_pd(fname, pd_event_name='Fixation', beh=beh,
                       pd_ch_names=['pd'], beh_key='fix_onset_time',
                       zscore=20, exclude_shift=0.05)
    pd_parser.parse_pd(fname, pd_event_name='Response', beh=beh,
                       pd_ch_names=['pd'], beh_key='response_onset_time',
                       zscore=20, add_events=True, exclude_shift=0.05)
    raw = _read_raw(fname)
    annot, pd_ch_names, beh2 = _load_data(raw)
    raw.set_annotations(annot)
    events4, event_id = mne.events_from_annotations(raw)
    np.testing.assert_array_equal(events4[events4[:, 2] == 1, 0],
                                  events2[:, 0])
    np.testing.assert_array_equal(events4[events4[:, 2] == 2, 0],
                                  events3[:, 0])
    assert pd_ch_names == ['pd']
    np.testing.assert_array_equal(beh2['pd_parser_sample'], events2[:, 0])


def test_beh_with_nas():
    """Test that behavior with 'n/a' entries works properly."""
    out_dir = _TempDir()
    fname, behf, corrupted = make_raw(out_dir)
    beh = _read_tsv(behf)
    beh['fix_onset_time'][4] = 'n/a'
    beh['fix_onset_time'][8] = 'n/a'
    _, samples = pd_parser.parse_pd(fname, beh=beh, pd_ch_names=['pd'])
    assert samples == ['n/a', 19740, 26978, 33025, 'n/a',
                       'n/a', 53531, 59601, 'n/a', 'n/a']


def test_plotting():
    """Test that the plots show properly."""
    out_dir = _TempDir()
    fname, behf, corrupted = make_raw(out_dir)
    raw = _read_raw(fname, preload=True)
    pd = raw._data[0]
    candidates = _find_pd_candidates(
        pd, max_len=max_len, baseline=baseline,
        zscore=zscore, max_flip_i=max_flip_i, sfreq=raw.info['sfreq'])[0]
    beh = _read_tsv(behf)
    beh_events = np.array(beh['fix_onset_time']) * raw.info['sfreq']
    beh_events_adjusted, alignment, events = _find_best_alignment(
        beh_events, candidates, exclude_shift, resync, raw.info['sfreq'],
        verbose=False)
    errors = beh_events_adjusted - events + alignment
    _plot_trial_errors(beh_events_adjusted, alignment, events,
                       errors, exclude_shift, raw.info['sfreq'])
    errors[abs(errors) / raw.info['sfreq'] > 2 * exclude_shift] = np.nan
    np.testing.assert_array_almost_equal(
        plt.gca().lines[0].get_ydata(), errors)
    section_data = [(0, 'test', np.random.random(10))]
    _plot_excluded_events(section_data, 2)
    assert plt.gca().title.get_text() == 'test'
    np.testing.assert_array_equal(plt.gca().lines[0].get_ydata(),
                                  section_data[0][2])


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_parse_pd(_bids_validate):
    # load in data
    behf = op.join(basepath, 'pd_beh.tsv')
    events = _read_tsv(op.join(basepath, 'pd_events.tsv'))
    events_relative = _read_tsv(op.join(basepath, 'pd_relative_events.tsv'))
    raw_tmp = mne.io.read_raw_fif(op.join(basepath, 'pd_data-raw.fif'),
                                  preload=True)
    raw_tmp.info['dig'] = None
    raw_tmp.info['line_freq'] = 60
    out_dir = _TempDir()
    fname = op.join(out_dir, 'pd_data-raw.fif')
    raw_tmp.save(fname)
    # this needs to be tested with user interaction, this
    # just tests that it launches
    pd_parser.find_pd_params(fname, pd_ch_names=['pd'])
    plt.close('all')
    # test core functionality
    annot, samples = pd_parser.parse_pd(fname, beh=behf, pd_ch_names=['pd'],
                                        zscore=20, resync=0.125)
    plt.close('all')
    raw = mne.io.read_raw_fif(fname)
    raw.set_annotations(annot)
    events2, event_id = mne.events_from_annotations(raw)
    np.testing.assert_array_equal(
        events2[:, 0], [e for e in events['pd_parser_sample'] if e != 'n/a'])
    assert samples == events['pd_parser_sample']
    # test add_pd_off_events
    annot = pd_parser.add_pd_off_events(fname, off_event_name=off_event_name,
                                        zscore=20)
    raw.set_annotations(annot)
    assert off_event_name in annot.description
    events2, event_id = mne.events_from_annotations(raw)
    off_events = events2[events2[:, 2] == event_id[off_event_name]]
    np.testing.assert_array_equal(
        off_events[:, 0], [e for e in events['off_sample'] if e != 'n/a'])
    '''
    df = dict(trial=range(300), pd_parser_sample=samples, off_sample=list())
    i = 0
    for s in samples:
        df['off_sample'].append('n/a' if s == 'n/a' else off_events[i, 0])
        i += s != 'n/a'
    '''
    # test add_pd_relative_events
    pd_parser.add_relative_events(
        raw, behf,
        relative_event_keys=['fix_duration', 'go_time', 'response_time'],
        relative_event_names=['ISI Onset', 'Go Cue', 'Response'])
    annot, pd_ch_names, beh = _load_data(raw)
    raw.set_annotations(annot)
    events2, event_id = mne.events_from_annotations(raw)
    np.testing.assert_array_equal(events2[:, 0], events_relative['sample'])
    assert pd_ch_names == ['pd']
    np.testing.assert_array_equal(
        events2[:, 2], [event_id[tt] for tt in events_relative['trial_type']])
    # test add_pd_events_to_raw
    raw2 = pd_parser.add_events_to_raw(raw, keep_pd_channels=True)
    events3, event_id2 = mne.events_from_annotations(raw2)
    np.testing.assert_array_equal(events3, events2)
    assert event_id2 == event_id
    # test pd_parser_save_to_bids
    bids_dir = op.join(out_dir, 'bids_dir')
    pd_parser.save_to_bids(bids_dir, fname, '1', 'test', verbose=False)
    _bids_validate(bids_dir)


def test_long_events():
    out_dir = _TempDir()
    raw = mne.io.read_raw_fif(op.join(basepath, 'pd_data2-raw.fif'),
                              preload=True)
    fname = op.join(out_dir, 'pd_data-raw.fif')
    raw.save(fname)
    behf = op.join(basepath, 'pd_events2.tsv')
    _, samples = pd_parser.parse_pd(
        fname, beh=behf, beh_key='event', pd_ch_names=['pd'],
        zscore=20, max_len=4, exclude_shift=1.5, resync=2)
    assert samples == [47900, 55953, 73458, 81293, 99415,
                       107467, 125972, 134108, 152030, 160482]


def test_parse_audio():
    out_dir = _TempDir()
    max_len = 0.25
    zscore = 10
    audio_fname = op.join(basepath, 'test_video.wav')
    fs, data = wavfile.read(audio_fname)
    data = data.mean(axis=1)  # stereo audio but only need one source
    info = mne.create_info(['audio'], fs, ['stim'])
    raw = mne.io.RawArray(data[np.newaxis], info)
    fname = op.join(out_dir, 'test_video-raw.fif')
    raw.save(fname, overwrite=True)
    raw = _read_raw(fname, preload=True)
    audio = raw._data[0]
    candidates = _find_audio_candidates(
        audio=audio, sfreq=raw.info['sfreq'], max_len=max_len,
        zscore=zscore, verbose=verbose)
    np.testing.assert_array_equal(candidates, np.array(
        [914454, 1915824, 2210042, 2970516, 4010037, 5011899,
         6051706, 7082591, 7651608, 8093410, 9099765, 10145123,
         12010012, 13040741, 14022720, 15038656, 16021487]))
    behf = op.join(basepath, 'test_video_beh.tsv')
    pd_parser.parse_audio(raw, beh=behf, audio_ch_names=['audio'],
                          zscore=10)
    annot, audio_ch_names, beh = _load_data(raw)
    np.testing.assert_array_almost_equal(annot.onset, np.array(
        [19.05112457, 39.9129982, 61.88574982, 83.54243469,
         104.41456604, 126.07720947, 147.5539856, 168.61270142,
         189.57843018, 211.35673523, 250.20858765, 271.68209839,
         292.14001465, 313.30532837, 333.78097534]))
    assert audio_ch_names == ['audio']
    assert beh['pd_parser_sample'] == \
        [914454, 1915824, 2970516, 4010037, 5011899, 6051706, 7082591,
         8093410, 9099765, 10145123, 12010012, 13040741, 14022720,
         15038656, 16021487]
    # test cli
    if platform.system() != 'Windows':
        assert call([f'parse_audio {fname} --beh {behf} '
                     '--audio_ch_names audio --zscore 10 -o'],
                    shell=True, env=os.environ) == 0


def test_cli():
    if platform.system() == 'Windows':
        return
    out_dir = _TempDir()
    fname, behf, _ = make_raw(out_dir)
    # can't test with a live plot, but if this should be called by hand
    # call([f'find_pd_params {fname} --pd_ch_names pd'], shell=True,
    #      env=os.environ)
    assert call([f'parse_pd {fname} --beh {behf} --pd_ch_names pd'],
                shell=True, env=os.environ) == 0
    assert call([f'add_pd_off_events {fname} --zscore 14'],
                shell=True, env=os.environ) == 0
    assert call([f'add_relative_events {fname} --beh {behf} '
                 '--relative_event_keys fix_duration go_time response_time '
                 '--relative_event_names "ISI Onset" "Go Cue" "Response"'],
                shell=True, env=os.environ) == 0
    assert call([f'add_events_to_raw {fname} --keep_pd_channels -o'],
                shell=True, env=os.environ) == 0
    bids_dir = op.join(out_dir, 'bids_dir')
    assert call([f'pd_parser_save_to_bids {bids_dir} {fname} 1 test'],
                shell=True, env=os.environ) == 0


def test_examples():
    # mac and windows tests run into issues with interactive elements
    if platform.system() != 'Linux':
        return
    examples_dir = op.join(op.dirname(op.dirname(pd_parser.__file__)),
                           'examples')
    examples = [op.join(examples_dir, f) for f in os.listdir(examples_dir)
                if op.splitext(f)[-1] == '.py']
    for example in examples:
        assert call([f'python {example}'], shell=True, env=os.environ) == 0
        plt.close('all')
