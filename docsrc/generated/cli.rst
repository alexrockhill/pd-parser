:orphan:

.. _python_cli:

======================================
pd_parser Command Line Interface (CLI)
======================================

Here we list the pd_parser tools that you can use from the command line.

.. contents:: Contents
   :local:
   :depth: 1



.. _gen_add_events_to_raw:

add_events_to_raw
=================

.. rst-class:: callout

usage: ``add_events_to_raw raw [-h] [--out_fname OUT_FNAME] [--drop_pd_channels DROP_PD_CHANNELS] [--verbose VERBOSE] [-o]``

positional arguments
--------------------
raw
	The electrophysiology filepath



optional arguments
------------------
-h, --help		show this help message and exit


--out_fname OUT_FNAME		The name to save out the new raw file out to


--drop_pd_channels DROP_PD_CHANNELS		Whether to drop the channels with the photodiode data.


--verbose VERBOSE		Set verbose output to True or False.


-o, --overwrite		Pass this flag to overwrite an existing file







.. _gen_add_pd_off_events:

add_pd_off_events
=================

.. rst-class:: callout

usage: ``add_pd_off_events raw [-h] [--off_event_name OFF_EVENT_NAME] [--max_len MAX_LEN] [--zscore ZSCORE] [--max_flip_i MAX_FLIP_I] [--baseline BASELINE] [--verbose VERBOSE] [-o]``

positional arguments
--------------------
raw
	The electrophysiology raw object or filepath



optional arguments
------------------
-h, --help		show this help message and exit


--off_event_name OFF_EVENT_NAME		The name of the photodiode event


--max_len MAX_LEN		The length of the longest photodiode event


--zscore ZSCORE		The same zscore as used for `parse_pd`.


--max_flip_i MAX_FLIP_I		The same max_flip_i as used for `parse_pd`.


--baseline BASELINE		The same baseline as used for `parse_pd`.


--verbose VERBOSE		Set verbose output to True or False.


-o, --overwrite		Pass this flag to overwrite an existing file







.. _gen_add_relative_events:

add_relative_events
===================

.. rst-class:: callout

usage: ``add_relative_events raw [-h] [--beh BEH] [--relative_event_keys [RELATIVE_EVENT_KEYS ...]] [--relative_event_names [RELATIVE_EVENT_NAMES ...]] [--verbose VERBOSE] [-o]``

positional arguments
--------------------
raw
	The electrophysiology raw object or filepath



optional arguments
------------------
-h, --help		show this help message and exit


--beh BEH		The behavioral tsv filepath


--relative_event_keys [RELATIVE_EVENT_KEYS ...]		A behavioral key (column) in the tsv file that has the time relative to the photodiode events on the same trial as in the `beh_key` event.


--relative_event_names [RELATIVE_EVENT_NAMES ...]		The name of the corresponding `relative_event_keys` events


--verbose VERBOSE		Set verbose output to True or False.


-o, --overwrite		Pass this flag to overwrite an existing file







.. _gen_find_pd_params:

find_pd_params
==============

.. rst-class:: callout

usage: ``find_pd_params raw [-h] [--pd_ch_names [PD_CH_NAMES ...]] [--verbose VERBOSE]``

positional arguments
--------------------
raw
	The electrophysiology raw object or filepath



optional arguments
------------------
-h, --help		show this help message and exit


--pd_ch_names [PD_CH_NAMES ...]		The name(s) of the channels with the photodiode data. Can be one channel for common referenced recording or two for a bipolar recording. If not provided, the data will be plotted for the user to pick


--verbose VERBOSE		Set verbose output to True or False.







.. _gen_parse_audio:

parse_audio
===========

.. rst-class:: callout

usage: ``parse_audio raw [-h] [--audio_event_name AUDIO_EVENT_NAME] [--beh BEH] [--beh_key BEH_KEY] [--audio_ch_names [AUDIO_CH_NAMES ...]] [--exclude_shift EXCLUDE_SHIFT] [--resync RESYNC] [--max_len MAX_LEN] [--zscore ZSCORE] [--add_events] [--recover] [--verbose VERBOSE] [-o]``

positional arguments
--------------------
raw
	TThe electrophysiology raw object or filepath



optional arguments
------------------
-h, --help		show this help message and exit


--audio_event_name AUDIO_EVENT_NAME		The name of the audio event


--beh BEH		The behavioral dictionary or tsv filepath


--beh_key BEH_KEY		The name of the behavioral key (column) corresponding to the audio event timing


--audio_ch_names [AUDIO_CH_NAMES ...]		The name(s) of the channels with the audio data. Note that they will be if thereare two channels they will be bipolar referenced


--exclude_shift EXCLUDE_SHIFT		How many seconds off to exclude an audio-behavioral event difference


--resync RESYNC		How large of a difference to use to resynchronize events. See `pd_parser.parse_pd` for more information


--max_len MAX_LEN		The length of the longest audio event


--zscore ZSCORE		How many standard deviations larger than the baseline the correlation of the audio is. If None, zscore is found interactively.


--add_events		Whether to run the parser a second time to add more events from deflections corresponding to multiple events on the same channel


--recover		Whether to recover corrupted events manually.


--verbose VERBOSE		Set verbose output to True or False.


-o, --overwrite		Pass this flag to overwrite an existing file







.. _gen_parse_pd:

parse_pd
========

.. rst-class:: callout

usage: ``parse_pd raw [-h] [--pd_event_name PD_EVENT_NAME] [--beh BEH] [--beh_key BEH_KEY] [--pd_ch_names [PD_CH_NAMES ...]] [--exclude_shift EXCLUDE_SHIFT] [--resync RESYNC] [--max_len MAX_LEN] [--zscore ZSCORE] [--max_flip_i MAX_FLIP_I] [--baseline BASELINE] [--add_events] [--recover] [--verbose VERBOSE] [-o]``

positional arguments
--------------------
raw
	The electrophysiology raw object or filepath



optional arguments
------------------
-h, --help		show this help message and exit


--pd_event_name PD_EVENT_NAME		The name of the photodiode event


--beh BEH		The behavioral dictionary or tsv filepath


--beh_key BEH_KEY		The name of the behavioral key (column) corresponding to the photodiode event timing


--pd_ch_names [PD_CH_NAMES ...]		The name(s) of the channels with the photodiode data. Can be one channel for common referenced recording or two for a bipolar recording. If not provided, the data will be plotted for the user to pick


--exclude_shift EXCLUDE_SHIFT		How many seconds off to exclude a photodiode- behavioral event difference


--resync RESYNC		How large of a difference to use to resynchronize events. This is for when events are off but not by much and so they should be excluded but are still needed to fit an alignment.Increase if the alignment is failing because too many events are being excluded, decrease to speed up execution.


--max_len MAX_LEN		The length of the longest photodiode event


--zscore ZSCORE		How many standard deviations larger than the baseline the photodiode event is. Decrease if too many events are being found and increase if too few. Use `find_pd_params` to determine if unsure.


--max_flip_i MAX_FLIP_I		The maximum number of samples the photodiode event takes to transition. Increase if the transitions are not being found, decrease for fewer false positives.


--baseline BASELINE		How much relative to the max_lento use to idenify the time before the photodiode event. Probably don't change but increasing will reduce false-positives and decreasing will reduce false-negatives.


--add_events		Whether to run the parser a second time to add more events from deflections corresponding to multiple events on the same channel


--recover		Whether to recover corrupted events manually.


--verbose VERBOSE		Set verbose output to True or False.


-o, --overwrite		Pass this flag to overwrite an existing file







.. _gen_pd_parser_save_to_bids:

pd_parser_save_to_bids
======================

.. rst-class:: callout

usage: ``pd_parser_save_to_bids bids_dir raw sub task [-h] [--ses SES] [--run RUN] [--data_type DATA_TYPE] [--eogs [EOGS ...]] [--ecgs [ECGS ...]] [--emgs [EMGS ...]] [--verbose VERBOSE] [-o]``

positional arguments
--------------------
bids_dir
	Filepath of the BIDS directory to save to
raw
	The electrophysiology raw object or filepath
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


--eogs [EOGS ...]		The eogs if not set correctly already


--ecgs [ECGS ...]		The ecgs if not set correctly already


--emgs [EMGS ...]		The emgs if not set correctly already


--verbose VERBOSE		Set verbose output to True or False.


-o, --overwrite		Pass this flag to overwrite an existing file





