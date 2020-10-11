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
# Simulate data and use it to make a raw object:
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
from pd_parser.parse_pd import _to_tsv

import matplotlib.pyplot as plt

out_dir = _TempDir()

# simulate photodiode data
np.random.seed(29)
n_events = 300
# let's make our photodiode events on random uniform from 0.25 to 0.75 seconds
n_secs_on = np.random.random(n_events) * 0.5 + 0.25
raw, beh_df, events, _ = \
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
        raw._data[0, i - sfreq // 3: i - sfreq // 4] = -amount
    elif j == 1:
        raw._data[0, i + sfreq // 4: i + sfreq // 3] = -amount
    else:
        raw._data[0, i + 2 * sfreq // 3: i + 4 * sfreq // 4] = amount
    axes[j].plot(np.linspace(-1, 2, 3 * sfreq),
                 raw._data[0, i - sfreq: i + sfreq * 2])
    axes[j].set_xlabel('time (s)')


# make fake electrophysiology data
info = mne.create_info(['ch1', 'ch2', 'ch3'], raw.info['sfreq'],
                       ['seeg'] * 3)
raw2 = mne.io.RawArray(np.random.random((3, raw.times.size)) * 1e-6, info)
raw2.info['lowpass'] = raw.info['lowpass']  # these must match to combine
raw.add_channels([raw2])
# bids needs these data fields
raw.info['dig'] = None
raw.info['line_freq'] = 60

# save to disk as required by ``pd-parser``
fname = op.join(out_dir, 'sub-1_task-mytask_raw.fif')
raw.save(fname)
# add some offsets to the behavior so it's a bit more realistic
offsets = np.random.randn(n_events) * 0.001
beh_df['time'] = np.array(beh_df['time']) + offsets
behf = op.join(out_dir, 'sub-1_task-mytask_beh.tsv')
_to_tsv(behf, beh_df)


###############################################################################
# Find the photodiode events relative to the behavioral timing of interest:
#
# This function will use the default parameters to find and align the
# photodiode events, recovering the events that we just corrupted.
#
# Note that the mock function mocks user input so when you run the example,
# you want to delete that line and unindent the next line, and then provide
# your own input depending on whether you want to keep the events or not.

with mock.patch('builtins.input', return_value='y'):
    pd_parser.parse_pd(fname, pd_event_name='Stim On', behf=behf,
                       pd_ch_names=['pd'], beh_col='time', recover=True)

###############################################################################
# Find cessations of the photodiode deflections
#
# Since we manually intervened for the onsets, on those same trials, we'll
# have to manually intervene for the offsets.
#
# On the documentation webpage, this is example is not interactive,
# but if you download it as a jupyter notebook and run it or copy the code
# into a console running python (ipython recommended), you can see how to
# interact with the photodiode data to pick reasonable parameters by
# following the instructions.

pd_parser.add_pd_off_events(fname, off_event_name='Stim Off')
