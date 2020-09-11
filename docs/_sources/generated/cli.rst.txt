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





