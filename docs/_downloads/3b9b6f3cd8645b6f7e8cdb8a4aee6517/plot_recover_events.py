"""
==================================================
Manually Recover Events Not Found by the Algorithm
==================================================
In this example, we use ``pd-parser`` to find photodiode events that
have corrupted pre-event baselines, photodiode plateaus or post-event
baselines but not corrupted onsets or offsets.
Note that it might be a good idea not to recover these events
as there might be noise in the data around this time.
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
import mock

import mne
from mne.utils import _TempDir

import pd_parser
from pd_parser.parse_pd import _load_data

import matplotlib.pyplot as plt

out_dir = _TempDir()

# simulate photodiode data
np.random.seed(29)
n_events = 300
# let's make our photodiode events on random uniform from 0.25 to 0.75 seconds
n_secs_on = np.random.random(n_events) * 0.5 + 0.25
raw, beh, events, _ = \
    pd_parser.simulate_pd_data(n_events=n_events, n_secs_on=n_secs_on,
                               prop_corrupted=0.0)
sfreq = np.round(raw.info['sfreq']).astype(int)

# corrupt some events
corrupted_indices = [8, 144, 234]
amount = raw._data.max()
fig, axes = plt.subplots(1, len(corrupted_indices), figsize=(8, 4))
fig.suptitle('Corrupted Events')
axes[0].set_ylabel('voltage')
for j, i in enumerate(events[corrupted_indices, 0]):
    if j == 0:
        raw._data[0, i - sfreq // 5: i - sfreq // 10] = -amount
    elif j == 1:
        raw._data[0, i + sfreq // 4: i + sfreq // 3] = -amount
    else:
        raw._data[0, i + 3 * sfreq // 4: i + 5 * sfreq // 6] = amount
    axes[j].plot(np.linspace(-1, 2, 3 * sfreq),
                 raw._data[0, i - sfreq: i + sfreq * 2])
    axes[j].set_xlabel('time (s)')


# make figure nicer
fig.tight_layout()

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
offsets = np.random.randn(n_events) * 0.001
beh['time'] = np.array(beh['time']) + offsets

# save to disk as required by ``pd-parser``, raw needs to have a filename
fname = op.join(out_dir, 'sub-1_task-mytask_raw.fif')
raw.save(fname)

###############################################################################
# Find the photodiode events relative to the behavioral timing of interest
#
# This function will use the default parameters to find and align the
# photodiode events, recovering the events that we just corrupted.
#
# Note that the mock function mocks user input so when you run the example,
# you want to delete that line and unindent the next line, and then provide
# your own input depending on whether you want to keep the events or not.

with mock.patch('builtins.input', return_value='y'):
    pd_parser.parse_pd(fname, pd_event_name='Stim On', beh=beh, max_len=1.5,
                       pd_ch_names=['pd'], beh_key='time', recover=True)

###############################################################################
# Find cessations of the photodiode deflections
#
# Since we manually intervened for the onsets, on those same trials, we'll
# have to manually intervene for the offsets.
#
# On the documentation webpage, this is example is not interactive,
# but if you download it as a jupyter notebook and run it or copy the code
# into a console running python (ipython recommended), you can see how to
# interact with the window to accept or reject the recovered events by
# following the instructions.

# reject the two false deflections in the middle of the second event
with mock.patch('builtins.input', side_effect=['n'] * 2 + ['y'] * 2):
    pd_parser.add_pd_off_events(fname, max_len=1.5, off_event_name='Stim Off')

###############################################################################
# Check the results
#
# Finally, we'll check that the recovered events and the original events match.

annot = _load_data(fname)[0]
raw.set_annotations(annot)
events2, event_id = mne.events_from_annotations(raw)
on_events = events2[events2[:, 2] == event_id['Stim On']]
print(f'Original: {events[corrupted_indices, 0]}\n'
      f'Recovered: {on_events[corrupted_indices, 0]}')

off_events = events2[events2[:, 2] == event_id['Stim Off']]
original_off = events[corrupted_indices, 0] + \
    np.round(n_secs_on[corrupted_indices] * raw.info['sfreq']).astype(int)
print(f'Original off: {original_off}\n'
      f'Recovered off: {off_events[corrupted_indices, 0]}')
