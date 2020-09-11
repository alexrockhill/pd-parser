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
    parser.add_argument('fname', type=str,
                        help='The electrophysiology filepath')
    parser.add_argument('--pd_ch_names', type=str, nargs='*', required=False,
                        default=None, help='The name(s) of the channels '
                        'with the photodiode data. Can be one channel '
                        'for common referenced recording or two for '
                        'a bipolar recording. If not provided, the data '
                        'will be plotted for the user to pick')
    parser.add_argument('--verbose', default=True, type=bool,
                        required=False,
                        help='Set verbose output to True or False.')
    args = parser.parse_args()
    pd_parser.find_pd_params(args.fname, pd_ch_names=args.pd_ch_names,
                             verbose=args.verbose)
    plt.show()


def parse_pd():
    """Run parse_pd command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', type=str,
                        help='The electrophysiology filepath')
    parser.add_argument('--pd_event_name', type=str, required=False,
                        default='Fixation',
                        help='The name of the photodiode event')
    parser.add_argument('--behf', type=str, required=False,
                        help='The behavioral tsv filepath')
    parser.add_argument('--beh_col', type=str, required=False,
                        default='fix_onset_time',
                        help='The name of the behavioral column '
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
                        default=100, help='How many standard deviations '
                        'larger than the baseline the photodiode event is. '
                        'Decrease if too many events are being found '
                        'and increase if too few. Use `find_pd_params` '
                        'to determine if unsure.')
    parser.add_argument('--min_i', type=int, required=False,
                        default=10, help='The minimum number of samples '
                        'to qualify as a pd event. Increase for fewer '
                        'false-positives, decrease if your photodiode '
                        'is on for fewer samples.')
    parser.add_argument('--baseline', type=float, required=False,
                        default=0.25, help='How much relative to the max_len'
                        'to use to idenify the time before the '
                        'photodiode event. Probably don\'t change but '
                        'increasing will reduce false-positives and '
                        'decreasing will reduce false-negatives.')
    parser.add_argument('--add_events', type=bool, required=False,
                        default=False, help='Whether to run the parser '
                        'a second time to add more events from '
                        'deflections corresponding to multiple events '
                        'on the same channel')
    parser.add_argument('--verbose', default=True, type=bool,
                        required=False,
                        help='Set verbose output to True or False.')
    parser.add_argument('--overwrite', default=False, type=bool,
                        required=False, help='Whether to overwrite')
    args = parser.parse_args()
    pd_parser.parse_pd(
        args.fname, pd_event_name=args.pd_event_name, behf=args.behf,
        beh_col=args.beh_col, pd_ch_names=args.pd_ch_names,
        max_len=args.max_len, exclude_shift=args.exclude_shift,
        resync=args.resync, zscore=args.zscore, min_i=args.min_i,
        baseline=args.baseline, add_events=args.add_events,
        verbose=args.verbose, overwrite=args.overwrite)


def add_pd_off_events():
    """Run add_pd_off command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', type=str,
                        help='The electrophysiology filepath')
    parser.add_argument('--off_event_name', type=str, required=False,
                        default='StimOff',
                        help='The name of the photodiode event')
    parser.add_argument('--max_len', type=float, required=False,
                        default=1, help='The length of the longest '
                        'photodiode event')
    parser.add_argument('--zscore', type=float, required=False,
                        default=100, help='The same zscore as used for '
                        '`parse_pd`.')
    parser.add_argument('--min_i', type=int, required=False,
                        default=10, help='The same min_i as used for '
                        '`parse_pd`.')
    parser.add_argument('--baseline', type=float, required=False,
                        default=0.25, help='The same baseline as used '
                        'for `parse_pd`.')
    parser.add_argument('--verbose', default=True, type=bool,
                        required=False,
                        help='Set verbose output to True or False.')
    parser.add_argument('--overwrite', default=False, type=bool,
                        required=False, help='Whether to overwrite')
    args = parser.parse_args()
    pd_parser.add_pd_off_event(
        args.fname, off_event_name=args.off_event_name,
        max_len=args.max_len, zscore=args.zscore, min_i=args.min_i,
        baseline=args.baseline, verbose=args.verbose, overwrite=args.overwrite)


def add_pd_relative_events():
    """Run add_relative_events command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', type=str,
                        help='The electrophysiology filepath')
    parser.add_argument('--behf', type=str, required=False,
                        help='The behavioral tsv filepath')
    parser.add_argument('--relative_event_cols', type=str, nargs='*',
                        required=False,
                        default=['fix_duration', 'go_time', 'response_time'],
                        help='A behavioral column in the tsv file that has '
                        'the time relative to the photodiode events on the '
                        'same trial as in the `beh_col` event.')
    parser.add_argument('--relative_event_names', type=str, nargs='*',
                        required=False,
                        default=['ISI Onset', 'Go Cue', 'Response'],
                        help='The name of the corresponding '
                        '`relative_event_cols` events')
    parser.add_argument('--verbose', default=True, type=bool,
                        required=False,
                        help='Set verbose output to True or False.')
    parser.add_argument('--overwrite', default=False, type=bool,
                        required=False, help='Whether to overwrite')
    args = parser.parse_args()
    pd_parser.add_pd_relative_events(
        args.fname, behf=args.behf,
        relative_event_cols=args.relative_event_cols,
        relative_event_names=args.relative_event_names,
        verbose=args.verbose, overwrite=args.overwrite)


def add_pd_events_to_raw():
    """Run add_relative_events command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', type=str,
                        help='The electrophysiology filepath')
    parser.add_argument('--out_fname', type=str, required=False,
                        help='The name to save out the new '
                             'raw file out to')
    parser.add_argument('--drop_pd_channels', type=bool, required=False,
                        default=True, help='Whether to drop the '
                        'channels with the photodiode data.')
    parser.add_argument('--verbose', default=True, type=bool,
                        required=False,
                        help='Set verbose output to True or False.')
    parser.add_argument('--overwrite', default=False, type=bool,
                        required=False, help='Whether to overwrite')
    args = parser.parse_args()
    pd_parser.add_pd_events_to_raw(
        args.fname, out_fname=args.out_fname,
        drop_pd_channels=args.drop_pd_channels,
        verbose=args.verbose, overwrite=args.overwrite)


def pd_parser_save_to_bids():
    """Save the events from the photodiode data in BIDS format."""
    parser = argparse.ArgumentParser()
    parser.add_argument('bids_dir', type=str,
                        help='Filepath of the BIDS directory to save to')
    parser.add_argument('fname', type=str,
                        help='The electrophysiology filepath')
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
    parser.add_argument('--verbose', default=True, type=bool,
                        required=False,
                        help='Set verbose output to True or False.')
    parser.add_argument('--overwrite', default=False, type=bool,
                        required=False, help='Whether to overwrite')
    args = parser.parse_args()
    pd_parser.pd_parser_save_to_bids(
        args.bids_dir, args.fname, args.sub, args.task, ses=args.ses,
        run=args.run, data_type=args.data_type, eogs=args.eogs,
        ecgs=args.ecgs, emgs=args.emgs, verbose=args.verbose,
        overwrite=args.overwrite)
