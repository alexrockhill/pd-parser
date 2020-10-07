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

usage: ``add_pd_events_to_raw fname [-h] [--out_fname OUT_FNAME] [--drop_pd_channels DROP_PD_CHANNELS] [--verbose VERBOSE] [--overwrite OVERWRITE]``

positional arguments
--------------------
fname
	The electrophysiology filepath



optional arguments
------------------
-h, --help		show this help message and exit


--out_fname OUT_FNAME		The name to save out the new raw file out to


--drop_pd_channels DROP_PD_CHANNELS		Whether to drop the channels with the photodiode data.


--verbose VERBOSE		Set verbose output to True or False.


--overwrite OVERWRITE		Whether to overwrite







.. _gen_add_pd_off_events:

add_pd_off_events
=================

.. rst-class:: callout

usage: ``add_pd_off_events fname [-h] [--off_event_name OFF_EVENT_NAME] [--max_len MAX_LEN] [--zscore ZSCORE] [--min_i MIN_I] [--baseline BASELINE] [--verbose VERBOSE] [--overwrite OVERWRITE]``

positional arguments
--------------------
fname
	The electrophysiology filepath



optional arguments
------------------
-h, --help		show this help message and exit


--off_event_name OFF_EVENT_NAME		The name of the photodiode event


--max_len MAX_LEN		The length of the longest photodiode event


--zscore ZSCORE		The same zscore as used for `parse_pd`.


--min_i MIN_I		The same min_i as used for `parse_pd`.


--baseline BASELINE		The same baseline as used for `parse_pd`.


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

usage: ``parse_pd fname [-h] [--pd_event_name PD_EVENT_NAME] [--behf BEHF] [--beh_col BEH_COL] [--pd_ch_names LIST_OF_PD_CH_NAMES] [--exclude_shift EXCLUDE_SHIFT] [--resync RESYNC] [--max_len MAX_LEN] [--zscore ZSCORE] [--min_i MIN_I] [--baseline BASELINE] [--add_events ADD_EVENTS] [--verbose VERBOSE] [--overwrite OVERWRITE]``

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


--resync RESYNC		How large of a difference to use to resynchronize events. This is for when events are off but not by much and so they should be excluded but are still needed to fit an alignment.Increase if the alignment is failing because too many events are being excluded, decrease to speed up execution.


--max_len MAX_LEN		The length of the longest photodiode event


--zscore ZSCORE		How many standard deviations larger than the baseline the photodiode event is. Decrease if too many events are being found and increase if too few. Use `find_pd_params` to determine if unsure.


--min_i MIN_I		The minimum number of samples to qualify as a pd event. Increase for fewer false-positives, decrease if your photodiode is on for fewer samples.


--baseline BASELINE		How much relative to the max_lento use to idenify the time before the photodiode event. Probably don't change but increasing will reduce false-positives and decreasing will reduce false-negatives.


--add_events ADD_EVENTS		Whether to run the parser a second time to add more events from deflections corresponding to multiple events on the same channel


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





