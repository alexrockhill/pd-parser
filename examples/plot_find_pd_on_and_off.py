"""
=================================
Find Photodiode On and Off Events
=================================
In this example, we use ``pd-parser`` to find photodiode events and
align both the onset of the deflection and the cessation to
to behavior.
"""

# Authors: Alex Rockhill <aprockhill@mailbox.org>
#
# License: BSD (3-clause)

###############################################################################
# Simulate data and use it to make a raw object
#
# We'll make an `mne.io.Raw` object so that we can save out some random
# data with a photodiode event channel in it in fif format (a commonly used
# electrophysiology data format).
import os.path as op
import numpy as np

import mne
from mne.utils import _TempDir

import pd_parser
from pd_parser.parse_pd import _load_data

import matplotlib.pyplot as plt
import matplotlib.cm as cm

out_dir = _TempDir()

# simulate photodiode data
np.random.seed(29)
n_events = 300
# let's make our photodiode events on random uniform from 0.5 to 1 second
n_secs_on = np.random.random(n_events) * 0.5 + 0.5
prop_corrupted = 0.01
raw, beh, events, corrupted_indices = \
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

# add some offsets to the behavior so it's a bit more realistic
offsets = np.random.randn(n_events) * 0.01
beh['time'] = np.array(beh['time']) + offsets

# save to disk as required by ``pd-parser``
fname = op.join(out_dir, 'sub-1_task-mytask_raw.fif')
raw.save(fname)

###############################################################################
# Find the photodiode events relative to the behavioral timing of interest
#
# This function will use the default parameters to find and align the
# photodiode events, excluding events that were off.
# One percent of the 300 events (3) were corrupted as shown in the plots and
# some were too far off from large offsets that we're going to exclude them.

pd_parser.parse_pd(fname, pd_event_name='Stim On', beh=beh,
                   pd_ch_names=['pd'], beh_key='time',
                   max_len=1.5)  # none are on longer than 1.5 seconds

###############################################################################
# Find cessations of the photodiode deflections
#
# Another piece of information in the photodiode channel is the cessation of
# the events. Let's find those and add them to the events.

pd_parser.add_pd_off_events(fname, off_event_name='Stim Off', max_len=1.5)

###############################################################################
# Check recovered event lengths and compare to the simulation ground truth
#
# Let's load in the on and off events and plot their difference compared to
# the ``n_secs_on`` event lengths we used to simulate.
# The plot below show the differences between the simulated
# deflection event lengths on the x axis scattered against the
# recovered event lengths on the y axis. The identity line (the line with 1:1
# correspondance) is not shown as it would occlude the plotted data; the
# the lengths are recovered within 1 millisecond. Note that the colors are
# arbitrary and are only used to increase contrast and ease of visualization.

annot, pd_ch_names, beh = _load_data(fname)
raw.set_annotations(annot)
events, event_id = mne.events_from_annotations(raw)
on_events = events[events[:, 2] == event_id['Stim On']]
off_events = events[events[:, 2] == event_id['Stim Off']]

recovered = (off_events[:, 0] - on_events[:, 0]) / raw.info['sfreq']
not_corrupted = [s != 'n/a' for s in beh['pd_parser_sample']]
ground_truth_not_corrupted = n_secs_on[not_corrupted]

fig, ax = plt.subplots()
ax.scatter(ground_truth_not_corrupted, recovered,
           s=1, color=cm.rainbow(np.linspace(0, 1, len(recovered))))
ax.set_title('Photodiode offset eventfidelity of recovery')
ax.set_xlabel('ground truth duration (s)')
ax.set_ylabel('recovered duration (s)')

print('Mean difference in the recovered from simulated length is {:.3f} '
      'milliseconds'.format(
          1000 * abs(ground_truth_not_corrupted - recovered).mean()))
