"""
=====================================
02. Find Photodiode On and Off Events
=====================================
In this example, we use pd-parser to find photodiode events and
align both the onset of the deflection and the cessation to
to behavior.
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
from pd_parser.parse_pd import _to_tsv, _load_pd_data

import matplotlib.pyplot as plt

out_dir = _TempDir()

# simulate photodiode data
np.random.seed(29)
n_events = 300
# let's make our photodiode events on random uniform from 0.5 to 1 second
n_secs_on = np.random.random(n_events) * 0.5 + 0.5
prop_corrupted = 0.01
raw, beh_df, events, corrupted_indices = \
    pd_parser.simulate_pd_data(n_events=n_events, n_secs_on=n_secs_on,
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

# save to disk as required by pd-parser
fname = op.join(out_dir, 'sub-1_task-mytask_raw.fif')
raw.save(fname)
# add some offsets to the behavior so it's a bit more realistic
offsets = np.random.randn(n_events) * 0.01
beh_df['time'] = np.array(beh_df['time']) + offsets
behf = op.join(out_dir, 'sub-1_task-mytask_beh.tsv')
_to_tsv(behf, beh_df)


###############################################################################
# Find the photodiode events relative to the behavioral timing of interest:
#
# This function will use the default parameters to find and align the
# photodiode events, excluding events that were off.
# One percent of the 300 events (3) were corrupted as shown in the plots and
# some were too far off from large offsets that we're going to exclude them.

pd_parser.parse_pd(fname, pd_event_name='Stim On', behf=behf,
                   pd_ch_names=['pd'], beh_col='time')

###############################################################################
# Find cessations of the photodiode deflections
#
# Another piece of information in the photodiode channel is the cessation of
# the events. Let's find those and add them to the events.

pd_parser.add_pd_off_event(fname, off_event_name='Stim Off')

###############################################################################
# Check recovered event lengths and compare to the simulation ground truth
#
# Let's load in the on and off events and plot their difference compared to
# the ``n_secs_on`` event lengths we used to simulate.
# The plot below show the differences between the simulated and recovered
# deflection lengths. They completely overlap except where the photodiode was
# corrupted, so it's a bit hard to see

annot, pd_ch_names, beh_df = _load_pd_data(fname)
raw.set_annotations(annot)
events, event_id = mne.events_from_annotations(raw)
on_events = events[events[:, 2] == event_id['Stim On']]
off_events = events[events[:, 2] == event_id['Stim Off']]

fig, ax = plt.subplots()
ax.plot([i for i, s in enumerate(beh_df['pd_sample']) if s != 'n/a'],
        (off_events[:, 0] - on_events[:, 0]) / raw.info['sfreq'],
        alpha=0.5, color='r', label='recovered')
ax.plot(n_secs_on, alpha=0.5, color='k', label='ground truth')
ax.set_xlabel('trial')
ax.set_ylabel('deflection length (s)')
fig.legend()