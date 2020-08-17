:orphan:

.. _python_cli:

======================================
pd_parser Command Line Interface (CLI)
======================================

Here we list the pd_parser tools that you can use from the command line.

.. contents:: Contents
   :local:
   :depth: 1



.. _gen_add_pd_events_to_raw:

add_pd_events_to_raw
====================

.. rst-class:: callout

usage: ``add_pd_events_to_raw fname [-h] [--out_fname OUT_FNAME] [--verbose VERBOSE] [--overwrite OVERWRITE]``

positional arguments
--------------------
fname
	The electrophysiology filepath



optional arguments
------------------
-h, --help		show this help message and exit


--out_fname OUT_FNAME		The name to save out the new raw file out to


--verbose VERBOSE		Set verbose output to True or False.


--overwrite OVERWRITE		Whether to overwrite







.. _gen_add_pd_relative_events:

add_pd_relative_events
======================

.. rst-class:: callout

usage: ``add_pd_relative_events fname [-h] [--behf BEHF] [--relative_event_cols LIST_OF_RELATIVE_EVENT_COLS] [--relative_event_names LIST_OF_RELATIVE_EVENT_NAMES] [--verbose VERBOSE] [--overwrite OVERWRITE]``

positional arguments
--------------------
fname
	The electrophysiology filepath



optional arguments
------------------
-h, --help		show this help message and exit


--behf BEHF		The behavioral tsv filepath


--relative_event_cols LIST_OF_RELATIVE_EVENT_COLS		A behavioral column in the tsv file that has the time relative to the photodiode events on the same trial as in the `beh_col` event.


--relative_event_names LIST_OF_RELATIVE_EVENT_NAMES		The name of the corresponding `relative_event_cols` events


--verbose VERBOSE		Set verbose output to True or False.


--overwrite OVERWRITE		Whether to overwrite







.. _gen_find_pd_params:

find_pd_params
==============

.. rst-class:: callout

usage: ``find_pd_params fname [-h] [--pd_ch_names LIST_OF_PD_CH_NAMES] [--verbose VERBOSE]``

positional arguments
--------------------
fname
	The electrophysiology filepath



optional arguments
------------------
-h, --help		show this help message and exit


--pd_ch_names LIST_OF_PD_CH_NAMES		The name(s) of the channels with the photodiode data. Can be one channel for common referenced recording or two for a bipolar recording. If not provided, the data will be plotted for the user to pick


--verbose VERBOSE		Set verbose output to True or False.







.. _gen_parse_pd:

parse_pd
========

.. rst-class:: callout

usage: ``parse_pd fname [-h] [--pd_event_name PD_EVENT_NAME] [--behf BEHF] [--beh_col BEH_COL] [--pd_ch_names LIST_OF_PD_CH_NAMES] [--exclude_shift EXCLUDE_SHIFT] [--chunk CHUNK] [--zscore ZSCORE] [--min_i MIN_I] [--alignment_prop ALIGNMENT_PROP] [--baseline BASELINE] [--overlap OVERLAP] [--verbose VERBOSE] [--overwrite OVERWRITE]``

positional arguments
--------------------
fname
	The electrophysiology filepath



optional arguments
------------------
-h, --help		show this help message and exit


--pd_event_name PD_EVENT_NAME		The name of the photodiode event


--behf BEHF		The behavioral tsv filepath


--beh_col BEH_COL		The name of the behavioral column corresponding to the photodiode event timing


--pd_ch_names LIST_OF_PD_CH_NAMES		The name(s) of the channels with the photodiode data. Can be one channel for common referenced recording or two for a bipolar recording. If not provided, the data will be plotted for the user to pick


--exclude_shift EXCLUDE_SHIFT		How many seconds off to exclude a photodiode- behavioral event difference


--chunk CHUNK		How large to window the photodiode events, should >> 2 * longest event. but cannot contain multiple events. e.g. if the photodiode is on for 100 samples at 500 Hz sampling rate, then 2 seconds should be a good chunk, if it's on for 500 samples then 10 seconds will be better. Note: each chunk cannot contain multiple events or it won't work so the events must be at least chunk seconds away from each other. Use `find_pd_params` to determine if unsure.


--zscore ZSCORE		How many standard deviations larger than the baseline the photodiode event is. Decrease if too many events are being found and increase if too few. Use `find_pd_params` to determine if unsure.


--min_i MIN_I		The minimum number of samples to qualify as a pd event. Increase for fewer false-positives, decrease if your photodiode is on for fewer samples. Use `find_pd_params` to determine if unsure.


--alignment_prop ALIGNMENT_PROP		The proportion of events to use to align with the behavior. Increase if event alignment doesn't work, decrease to save computation time.


--baseline BASELINE		How much relative to the chunkto use to idenify the time before the photodiode event. Probably don't change but increasing will reduce false-positives and decreasing will reduce false-negatives.


--overlap OVERLAP		How much to overlap the windows of the photodiode event-finding process. Probably don't change but increasing will reduce false-negatives but longer computation time.


--verbose VERBOSE		Set verbose output to True or False.


--overwrite OVERWRITE		Whether to overwrite







.. _gen_pd_parser_save_to_bids:

pd_parser_save_to_bids
======================

.. rst-class:: callout

usage: ``pd_parser_save_to_bids bids_dir fname sub task [-h] [--ses SES] [--run RUN] [--data_type DATA_TYPE] [--eogs LIST_OF_EOGS] [--ecgs LIST_OF_ECGS] [--emgs LIST_OF_EMGS] [--verbose VERBOSE] [--overwrite OVERWRITE]``

positional arguments
--------------------
bids_dir
	Filepath of the BIDS directory to save to
fname
	The electrophysiology filepath
sub
	The subject identifier
task
	The task identifier



optional arguments
------------------
-h, --help		show this help message and exit


--ses SES		The session identifier


--run RUN		The run identifier


--data_type DATA_TYPE		The type of data if not set correctly already (ieeg is often set as eeg for instance)


--eogs LIST_OF_EOGS		The eogs if not set correctly already


--ecgs LIST_OF_ECGS		The ecgs if not set correctly already


--emgs LIST_OF_EMGS		The emgs if not set correctly already


--verbose VERBOSE		Set verbose output to True or False.


--overwrite OVERWRITE		Whether to overwrite





