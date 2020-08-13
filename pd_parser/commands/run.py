"""Command Line Interface for photodiode parsing."""
# Authors: Alex Rockhill <aprockhill@mailbox.org>
#
# License: BSD (3-clause)
import argparse

import pd_parser


def parse_pd():
    """Run parse_pd command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', type=str, required=True,
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
    parser.add_argument('--chunk', type=float, required=False,
                        default=2, help='How large to window the '
                        'photodiode events, should >> 2 * longest event. '
                        'e.g. if the photodiode is on for 100 samples at '
                        '500 Hz sampling rate, then 2 seconds should be '
                        'a good chunk, if it\'s on for 500 samples then '
                        '10 seconds will be better. Note: each chunk '
                        'cannot contain multiple events or it won\'t work '
                        'so the events must be at least chunk seconds '
                        'away from each other')
    parser.add_argument('--baseline', type=float, required=False,
                        default=0.25, help='How much relative to the chunk'
                        'to use to idenify the time before the '
                        'photodiode event. Increase for fewer '
                        'false-positives, decrease for fewer false-negatives.')
    parser.add_argument('--overlap', type=float, required=False,
                        default=0.25, help='How much to overlap the '
                        'windows of the photodiode event-finding '
                        'process. Increase for fewer false-negatives '
                        'but longer computation time.')
    parser.add_argument('--exclude_shift', type=float, required=False,
                        default=0.1, help='How many seconds off to exclude a '
                        'photodiode-behavioral event difference')
    parser.add_argument('--zscore', type=float, required=False,
                        default=10, help='How many standard deviations '
                        'larger than the baseline the photodiode event is. '
                        'Decrease if too many events are being found '
                        'and increase if too few.')
    parser.add_argument('--min_i', type=int, required=False,
                        default=10, help='The minimum number of samples '
                        'to qualify as a pd event. Increase for fewer '
                        'false-positives, decrease if your photodiode '
                        'is on for fewer samples')
    parser.add_argument('--alignment_prop', type=float, required=False,
                        default=0.2, help='The proportion of events to use to '
                        'align with the behavior. Increase if event '
                        'alignment doesn\'t work, decrease to save '
                        'computation time')
    parser.add_argument('--out_fname', default=False, type=str,
                        required=False, help='Where to save the '
                        'modified raw file, if False not saved')
    parser.add_argument('--verbose', default=True, type=bool,
                        required=False,
                        help='Set verbose output to True or False.')
    parser.add_argument('--overwrite', default=False, type=bool,
                        required=False, help='Whether to overwrite')
    args = parser.parse_args()
    pd_parser.parse_pd(args.fname, pd_event_name=args.pd_event_name,
                       behf=args.behf, beh_col=args.beh_col,
                       chunk=args.chunk, baseline=args.baseline,
                       overlap=args.overlap, exclude_shift=args.exclude_shift,
                       zscore=args.zscore,
                       first_alignment_n=args.first_alignment_n,
                       verbose=args.verbose,
                       overwrite=args.overwrite)


def add_relative_events():
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
                        'same trial as in the `--beh_col event.')
    parser.add_argument('--relative_event_names', type=str, nargs='*',
                        required=False,
                        default=['ISI Onset', 'Go Cue', 'Response'],
                        help='The name of the corresponding '
                        '`--relative_event_cols` events')
    parser.add_argument('--verbose', default=True, type=bool,
                        required=False,
                        help='Set verbose output to True or False.')
    parser.add_argument('--overwrite', default=False, type=bool,
                        required=False, help='Whether to overwrite')
    args = parser.parse_args()
    pd_parser.add_relative_events(args.filename, out_fname=args.out_fname,
                                  verbose=args.verbose,
                                  overwrite=args.overwrite)


def add_events_to_raw():
    """Run add_relative_events command."""
    parser = argparse.ArgumentParser()
    parser.add_argument('fname', type=str,
                        help='The electrophysiology filepath')
    parser.add_argument('--out_fname', type=str, required=False,
                        help='The name to save out the new '
                             'raw file out to')
    parser.add_argument('--verbose', default=True, type=bool,
                        required=False,
                        help='Set verbose output to True or False.')
    parser.add_argument('--overwrite', default=False, type=bool,
                        required=False, help='Whether to overwrite')
    args = parser.parse_args()
    pd_parser.add_events_to_raw(args.fname, out_fname=args.out_fname,
                                verbose=args.verbose, overwrite=args.overwrite)
