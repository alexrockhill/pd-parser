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
# Simulate data and use it to make a raw object:
#
# We'll make an mne.io.Raw object so that we can save out some random
# data with a photodiode event channel in it in fif format (a standard
# electrophysiology format)
import os.path as op
import numpy as np

import mne
from mne.utils import _TempDir

import pd_parser
from pd_parser.parse_pd import _to_tsv

out_dir = _TempDir()

# simulate photodiode data
n_events = 300
prop_corrupted = 0.01
raw, beh_df, events, corrupted_indices = \
    pd_parser.simulate_pd_data(n_events=n_events,
                               prop_corrupted=prop_corrupted)

# make fake electrophysiology data
info = mne.create_info(['ch1', 'ch2', 'ch3'], raw.info['sfreq'],
                       ['seeg'] * 3)
raw2 = mne.io.RawArray(np.random.random((3, raw.times.size)) * 1e-6, info)
raw2.info['lowpass'] = raw.info['lowpass']  # these must match to combine
raw.add_channels([raw2])
# bids needs these data fields
raw.info['dig'] = None
raw.info['line_freq'] = 60

fname = op.join(out_dir, 'sub-1_task-mytask_raw.fif')
raw.save(fname)

###############################################################################
# Make behavior data:
#
# We'll make a dictionary with lists for the events that are time-stamped when
# the photodiode was turned on and other events relative to those events.
# We'll add some noise to the time-stamps so that we can see how behavior
# might look in an experimental setting.
# Let's make a task where there is a fixation stimulus, then a go cue,
# and a then response as an example.

np.random.seed(12)
# add some noise to make it harder to align, use just over
# the exclusion of 0.03 to make some events excluded
offsets = np.random.random(n_events) * 0.035 - 0.0125
# in this example, the fixation would always be 700 ms
# after which point a cue would appear which is the "go time"
go_time = np.repeat(0.7, n_events)
# let's make the response time between 0.5 and 1.5 seconds uniform random
response_time = list(go_time + np.random.random(n_events) + 1.5)
for i in [10, 129, 232, 288]:
    response_time[i] = 'n/a'  # make some no responses
# put in dictionary to be converted to tsv file
beh_df['fix_onset_time'] = beh_df['time'] + offsets
beh_df['go_time'] = go_time
beh_df['response_time'] = response_time
behf = op.join(out_dir, 'sub-1_task-mytask_beh.tsv')
# save behavior file out
_to_tsv(behf, beh_df)

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
# found from :func:`pd_parser.find_pd_parameters` to find and align the
# photodiode events, excluding events that were off because the commuter
# hung up on computation for instance. That data is save in the same folder
# as the raw file which can be used directly or accessed via
# :func:`pd_parser.pd_parser_save_to_bids`.

pd_parser.parse_pd(fname, behf=behf, pd_ch_names=['pd'])

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
    relative_event_cols=['go_time', 'response_time'],
    relative_event_names=['Go Cue', 'Response'])


###############################################################################
# Save data to BIDS format:
#
# This saves our data to BIDS format so that it's ready to be analyzed in a
# reproducible way will all the necessary files. See
# https://bids.neuroimaging.io/ and https://mne.tools/mne-bids/ for more
# information about BIDS.

pd_parser.pd_parser_save_to_bids(op.join(out_dir, 'bids_dir'), fname,
                                 sub='1', task='mytask')
