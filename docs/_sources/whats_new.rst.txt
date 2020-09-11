:orphan:

.. _whats_new:

.. currentmodule:: pd_parser

What's new?
===========

Here we list a changelog of pd-parser.

.. contents:: Contents
   :local:
   :depth: 3

.. currentmodule:: pd_parser

.. _current:

Current
-------

Changelog
~~~~~~~~~
- Added vertical lines to plots to show the difference between expected and actual events.


Bug
~~~
- Added tests for CLI functions, fixed bugs with functions


API
~~~
- Added ``off_event`` as a parameter for :func:`pd_parser.parse_pd` to make an event when the photodiode turns off.
- Added ``n_secs_on`` as an array in :func:`pd_parser.simulate_pd_data`.
- Added ``resync`` parameter to :func:`pd_parser.parse_pd` so that events could be used to sychronize but then excluded.

Authors
~~~~~~~

People who contributed to this release (in alphabetical order):

* Alex Rockhill

.. _Alex Rockhill: http://github.com/alexrockhill
