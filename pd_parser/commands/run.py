"""Command Line Interface for photodiode parsing."""
# Authors: Alex Rockhill <aprockhill@mailbox.org>
#
# License: BSD (3-clause)
import argparse

import pd_parser


def find_pd_params():
    """Plot the photodiode channel to find parameters for the parser."""
    import matplotlib.pyplot as plt
    parser = argparse.ArgumentParser()
    parser.add_argument('raw', type=str,
                        help='The electrophysiology raw object or filepath')
    parser.add_argument('--pd_ch_names', type=str, nargs='*', required=False,
                        default=None, help='The name(s) of the channels '
                        'with the photodiode data. Can be one channel '
                        'for common referenced recording or two for '
                        'a bipolar recording. If not provided, the data '
                        'will be plotted for the user to pick')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Whether to print function progress.')
    args = parser.parse_args()
    pd_parser.find_pd_params(args.raw, pd_ch_names=args.pd_ch_names,
                             verbose=args.verbose)
    plt.show(block=True)


def parse_pd():
    """Run parse_pd command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('raw', type=str,
                        help='The electrophysiology raw object or filepath')
    parser.add_argument('--pd_event_name', type=str, required=False,
                        default='Fixation',
                        help='The name of the photodiode event')
    parser.add_argument('--beh', type=str, required=False,
                        help='The behavioral dictionary or tsv filepath')
    parser.add_argument('--beh_key', type=str, required=False,
                        default='fix_onset_time',
                        help='The name of the behavioral key (column) '
                        'corresponding to the photodiode event timing')
    parser.add_argument('--pd_ch_names', type=str, nargs='*', required=False,
                        default=None, help='The name(s) of the channels '
                        'with the photodiode data. Can be one channel '
                        'for common referenced recording or two for '
                        'a bipolar recording. If not provided, the data '
                        'will be plotted for the user to pick')
    parser.add_argument('--exclude_shift', type=float, required=False,
                        default=0.05, help='How many seconds off to exclude a '
                        'photodiode-behavioral event difference')
    parser.add_argument('--resync', type=float, required=False,
                        default=0.075, help='How large of a difference '
                        'to use to resynchronize events. This is for when '
                        'events are off but not by much and so they should '
                        'be excluded but are still needed to fit an alignment.'
                        'Increase if the alignment is failing because too '
                        'many events are being excluded, decrease to speed up '
                        'execution.')
    parser.add_argument('--max_len', type=float, required=False,
                        default=1, help='The length of the longest '
                        'photodiode event')
    parser.add_argument('--zscore', type=float, required=False,
                        default=10, help='How many standard deviations '
                        'larger than the baseline the photodiode event is. '
                        'Decrease if too many events are being found '
                        'and increase if too few. Use `find_pd_params` '
                        'to determine if unsure.')
    parser.add_argument('--max_flip_i', type=int, required=False,
                        default=40, help='The maximum number of samples '
                        'the photodiode event takes to transition. Increase '
                        'if the transitions are not being found, decrease for '
                        'fewer false positives.')
    parser.add_argument('--baseline', type=float, required=False,
                        default=0.25, help='How much relative to the max_len'
                        'to use to idenify the time before the '
                        'photodiode event. Probably don\'t change but '
                        'increasing will reduce false-positives and '
                        'decreasing will reduce false-negatives.')
    parser.add_argument('--add_events', action='store_true',
                        help='Whether to run the parser '
                        'a second time to add more events from '
                        'deflections corresponding to multiple events '
                        'on the same channel')
    parser.add_argument('--recover', action='store_true',
                        help='Whether to recover corrupted events manually.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Whether to print function progress.')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Pass this flag to overwrite an existing file')
    args = parser.parse_args()
    pd_parser.parse_pd(
        args.raw, pd_event_name=args.pd_event_name, beh=args.beh,
        beh_key=args.beh_key, pd_ch_names=args.pd_ch_names,
        max_len=args.max_len, exclude_shift=args.exclude_shift,
        resync=args.resync, zscore=args.zscore, max_flip_i=args.max_flip_i,
        baseline=args.baseline, add_events=args.add_events,
        recover=args.recover, verbose=args.verbose, overwrite=args.overwrite)


def parse_audio():
    """Run parse_audio command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('raw', type=str,
                        help='TThe electrophysiology raw object or filepath')
    parser.add_argument('--audio_event_name', type=str, required=False,
                        default='Tone', help='The name of the audio event')
    parser.add_argument('--beh', type=str, required=False,
                        help='The behavioral dictionary or tsv filepath')
    parser.add_argument('--beh_key', type=str, required=False,
                        default='tone_onset_time',
                        help='The name of the behavioral key (column) '
                        'corresponding to the audio event timing')
    parser.add_argument('--audio_ch_names', type=str, nargs='*',
                        required=False, default=None,
                        help='The name(s) of the channels '
                        'with the audio data. Note that they will be if there'
                        'are two channels they will be bipolar referenced')
    parser.add_argument('--exclude_shift', type=float, required=False,
                        default=0.03, help='How many seconds off to exclude '
                        'an audio-behavioral event difference')
    parser.add_argument('--resync', type=float, required=False,
                        default=0.075, help='How large of a difference '
                        'to use to resynchronize events. '
                        'See `pd_parser.parse_pd` for more information')
    parser.add_argument('--max_len', type=float, required=False,
                        default=0.25, help='The length of the longest '
                        'audio event')
    parser.add_argument('--zscore', type=float, required=False,
                        default=None, help='How many standard deviations '
                        'larger than the baseline the correlation of the '
                        'audio is. If None, zscore is found interactively.')
    parser.add_argument('--add_events', action='store_true',
                        help='Whether to run the parser '
                        'a second time to add more events from '
                        'deflections corresponding to multiple events '
                        'on the same channel')
    parser.add_argument('--recover', action='store_true',
                        help='Whether to recover corrupted events manually.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Whether to print function progress.')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Pass this flag to overwrite an existing file')
    args = parser.parse_args()
    pd_parser.parse_audio(
        args.raw, audio_event_name=args.audio_event_name, beh=args.beh,
        beh_key=args.beh_key, audio_ch_names=args.audio_ch_names,
        exclude_shift=args.exclude_shift, resync=args.resync,
        max_len=args.max_len, zscore=args.zscore, add_events=args.add_events,
        recover=args.recover, verbose=args.verbose, overwrite=args.overwrite)


def add_pd_off_events():
    """Run add_pd_off command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('raw', type=str,
                        help='The electrophysiology raw object or filepath')
    parser.add_argument('--off_event_name', type=str, required=False,
                        default='StimOff',
                        help='The name of the photodiode event')
    parser.add_argument('--max_len', type=float, required=False,
                        default=1, help='The length of the longest '
                        'photodiode event')
    parser.add_argument('--zscore', type=float, required=False,
                        default=10, help='The same zscore as used for '
                        '`parse_pd`.')
    parser.add_argument('--max_flip_i', type=int, required=False,
                        default=40, help='The same max_flip_i as used for '
                        '`parse_pd`.')
    parser.add_argument('--baseline', type=float, required=False,
                        default=0.25, help='The same baseline as used '
                        'for `parse_pd`.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Whether to print function progress.')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Pass this flag to overwrite an existing file')
    args = parser.parse_args()
    pd_parser.add_pd_off_events(
        args.raw, off_event_name=args.off_event_name,
        max_len=args.max_len, zscore=args.zscore, max_flip_i=args.max_flip_i,
        baseline=args.baseline, verbose=args.verbose, overwrite=args.overwrite)


def add_relative_events():
    """Run add_relative_events command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('raw', type=str,
                        help='The electrophysiology raw object or filepath')
    parser.add_argument('--beh', type=str, required=False,
                        help='The behavioral tsv filepath')
    parser.add_argument('--relative_event_keys', type=str, nargs='*',
                        required=False,
                        default=['fix_duration', 'go_time', 'response_time'],
                        help='A behavioral key (column) in the tsv file that '
                        'has the time relative to the photodiode events on '
                        'the same trial as in the `beh_key` event.')
    parser.add_argument('--relative_event_names', type=str, nargs='*',
                        required=False,
                        default=['ISI Onset', 'Go Cue', 'Response'],
                        help='The name of the corresponding '
                        '`relative_event_keys` events')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Whether to print function progress.')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Pass this flag to overwrite an existing file')
    args = parser.parse_args()
    pd_parser.add_relative_events(
        args.raw, beh=args.beh,
        relative_event_keys=args.relative_event_keys,
        relative_event_names=args.relative_event_names,
        verbose=args.verbose, overwrite=args.overwrite)


def add_events_to_raw():
    """Run add_relative_events command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('raw', type=str,
                        help='The electrophysiology filepath')
    parser.add_argument('--out_fname', type=str, required=False,
                        help='The name to save out the new '
                             'raw file out to')
    parser.add_argument('--keep_pd_channels', action='store_true',
                        help='Whether to keep the '
                        'channels with the photodiode data.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Whether to print function progress.')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Pass this flag to overwrite an existing file')
    args = parser.parse_args()
    raw = pd_parser.add_events_to_raw(
        args.raw, keep_pd_channels=args.keep_pd_channels,
        verbose=args.verbose)
    if args.out_fname is None:
        raw.load_data()
    raw.save(args.raw if args.out_fname is None else args.out_fname,
             overwrite=args.overwrite)


def pd_parser_save_to_bids():
    """Save the events from the photodiode data in BIDS format."""
    parser = argparse.ArgumentParser()
    parser.add_argument('bids_dir', type=str,
                        help='Filepath of the BIDS directory to save to')
    parser.add_argument('raw', type=str,
                        help='The electrophysiology raw object or filepath')
    parser.add_argument('sub', type=str, help='The subject identifier')
    parser.add_argument('task', type=str, help='The task identifier')
    parser.add_argument('--ses', type=str, help='The session identifier',
                        required=False, default=None)
    parser.add_argument('--run', type=str, help='The run identifier',
                        required=False, default=None)
    parser.add_argument('--data_type', type=str,
                        required=False, default=None,
                        help='The type of data if not set correctly already '
                             '(ieeg is often set as eeg for instance)')
    parser.add_argument('--eogs', type=str, nargs='*',
                        required=False, default=None,
                        help='The eogs if not set correctly already')
    parser.add_argument('--ecgs', type=str, nargs='*',
                        required=False, default=None,
                        help='The ecgs if not set correctly already')
    parser.add_argument('--emgs', type=str, nargs='*',
                        required=False, default=None,
                        help='The emgs if not set correctly already')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Whether to print function progress.')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Pass this flag to overwrite an existing file')
    args = parser.parse_args()
    pd_parser.save_to_bids(
        args.bids_dir, args.raw, args.sub, args.task, ses=args.ses,
        run=args.run, data_type=args.data_type, eogs=args.eogs,
        ecgs=args.ecgs, emgs=args.emgs, verbose=args.verbose,
        overwrite=args.overwrite)
