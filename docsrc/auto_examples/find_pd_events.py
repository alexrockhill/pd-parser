"""
==========================
01. Find Photodiode Events
==========================
In this example, we use pd-parser to find photodiode events and
align them to behavior. Then, save the data to BIDS format.
"""

# Authors: Alex Rockhill <aprockhill@mailbox.org>
#
# License: BSD (3-clause)

###############################################################################
# Import data and use it to make a raw object:
#
# We'll make an mne.io.Raw object so that we can save out some random
# data with a photodiode event channel in it in fif format (a standard
# electrophysiology format)
import os.path as op
import numpy as np

import mne
from mne.utils import _TempDir

import pd_parser

basepath = op.join(op.dirname(pd_parser.__file__), 'tests', 'data')
out_dir = _TempDir()

fname = op.join(out_dir, 'pd_data-raw.fif')
behf = op.join(basepath, 'pd_beh.tsv')

raw_tmp = mne.io.read_raw_fif(op.join(basepath, 'pd_data-raw.fif'),
                              preload=True)
info = mne.create_info(['ch1', 'ch2', 'ch3'], raw_tmp.info['sfreq'],
                       ['seeg'] * 3)
raw_tmp2 = mne.io.RawArray(np.random.random((3, raw_tmp.times.size)) * 1e-6,
                           info)
raw_tmp2.info['lowpass'] = raw_tmp.info['lowpass']
raw_tmp.add_channels([raw_tmp2])
raw_tmp.info['dig'] = None
raw_tmp.save(fname)

###############################################################################
# Use the interactive graphical user interface (GUI) to find parameters:
#
# On the webpage, this is example is not interactive, but if you copy this
# code into a python console, you can see how to interact with the photo-
# diode data to pick reasonable parameters by following the instructions.

pd_parser.find_pd_params(fname, pd_ch_names=['pd'])

###############################################################################
# Find the photodiode events relative to the behavioral timing of interest:
#
# This function will use the default parameters or the parameters you
# found from `pd_parser.find_pd_parameters` to find and align the
# photodiode events, excluding events that were off because the commuter
# hung up on computation for instance. That data is save in the same folder
# as the raw file which can be used directly or accessed via
# `pd_parser.pd_parser.pd_parser_save_to_bids`.

pd_parser.parse_pd(fname, behf=behf, pd_ch_names=['pd'],
                   alignment_prop=0.05)  # reduce alignment_prop -> faster

###############################################################################
# Add events relative to the photodiode events:
#
# The photodiode is usually sychronized to one event (usually the fixation
# so that if the deflections caused by the photodiode are large enough
# to influence other channels through amplifier interactions it doesn't
# cause issues with the analysis) so often the events of interest are
# relative to the photodiode event. In the task a timer can be started at the
# photodiode event and pulled for time at each of the following events.
# These events are then passed in tsv file to be added to the events.
# Note: if more than one photodiode event is used, the parser can be
# used for each event separately using the keyword `add_event=True`.

pd_parser.add_pd_relative_events(
    fname, behf,
    relative_event_cols=['fix_duration', 'go_time', 'response_time'],
    relative_event_names=['ISI Onset', 'Go Cue', 'Response'])


###############################################################################
# Save data to BIDS format:
#
# This saves our data to BIDS format so that it's ready to be analyzed in a
# reproducible way will all the necessary files. See
# https://bids.neuroimaging.io/ and https://mne.tools/mne-bids/ for more
# information about BIDS.


pd_parser.pd_parser_save_to_bids(op.join(out_dir, 'bids_dir'), fname,
                                 sub='1', task='mytask')
