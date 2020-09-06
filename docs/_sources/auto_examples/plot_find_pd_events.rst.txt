.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_plot_find_pd_events.py>`     to download the full example code
    .. rst-class:: sphx-glr-example-title

    .. _sphx_glr_auto_examples_plot_find_pd_events.py:


==========================
01. Find Photodiode Events
==========================
In this example, we use pd-parser to find photodiode events and
align them to behavior. Then, save the data to BIDS format.


.. code-block:: default


    # Authors: Alex Rockhill <aprockhill@mailbox.org>
    #
    # License: BSD (3-clause)








Import data and use it to make a raw object:

We'll make an mne.io.Raw object so that we can save out some random
data with a photodiode event channel in it in fif format (a standard
electrophysiology format)


.. code-block:: default

    import os.path as op
    import numpy as np

    import mne
    from mne.utils import _TempDir

    import pd_parser
    from pd_parser.parse_pd import _to_tsv

    out_dir = _TempDir()

    # simulate photodiode data
    raw, events = pd_parser.simulate_pd_data(n_events=320)
    # make some errent photodiode signals
    raw2 = pd_parser.simulate_pd_data(n_events=10, iti=31.,
                                      iti_jitter=15.,
                                      n_sec_on=2.5)[0]
    raw._data[0, :raw2._data.size] += raw2._data[0]
    # take only the last 300 events to test alignment
    events = events[20:]

    # make fake electrophysiology data
    info = mne.create_info(['ch1', 'ch2', 'ch3'], raw.info['sfreq'],
                           ['seeg'] * 3)
    raw3 = mne.io.RawArray(np.random.random((3, raw.times.size)) * 1e-6, info)
    raw3.info['lowpass'] = raw.info['lowpass']  # these must match to combine
    raw.add_channels([raw3])
    # bids needs these data fields
    raw.info['dig'] = None
    raw.info['line_freq'] = 60


    fname = op.join(out_dir, 'sub-1_task-mytask_raw.fif')
    raw.save(fname)

    # make behavior data
    np.random.seed(12)
    beh_events = events[:, 0].astype(float) / raw.info['sfreq']
    offsets = np.random.random(len(beh_events)) * 0.035 - 0.0125
    beh_events += offsets
    fix_duration = np.repeat(0.7, beh_events.size)
    go_time = np.random.random(beh_events.size) + 2
    response_time = go_time + np.random.random(beh_events.size) + 1.5
    # put in dictionary to be converted to tsv file
    beh_df = dict(trial=np.arange(beh_events.size),
                  fix_onset_time=beh_events, fix_duration=fix_duration,
                  go_time=go_time, response_time=response_time)
    behf = op.join(out_dir, 'sub-1_task-mytask_beh.tsv')
    # save behavior file out
    _to_tsv(behf, beh_df)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Creating RawArray with float64 data, n_channels=1, n_times=2178734
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Creating RawArray with float64 data, n_channels=1, n_times=471792
        Range : 0 ... 471791 =      0.000 ...   471.791 secs
    Ready.
    Creating RawArray with float64 data, n_channels=3, n_times=2178734
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif [done]




Use the interactive graphical user interface (GUI) to find parameters:

On the webpage, this is example is not interactive, but if you copy this
code into a python console, you can see how to interact with the photo-
diode data to pick reasonable parameters by following the instructions.


.. code-block:: default


    pd_parser.find_pd_params(fname, pd_ch_names=['pd'])




.. image:: /auto_examples/images/sphx_glr_plot_find_pd_events_001.png
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Reading 0 ... 2178733  =      0.000 ...  2178.733 secs...
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:526: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()




Find the photodiode events relative to the behavioral timing of interest:

This function will use the default parameters or the parameters you
found from :func:`pd_parser.find_pd_parameters` to find and align the
photodiode events, excluding events that were off because the commuter
hung up on computation for instance. That data is save in the same folder
as the raw file which can be used directly or accessed via
:func:`pd_parser.pd_parser_save_to_bids`.


.. code-block:: default


    pd_parser.parse_pd(fname, behf=behf, pd_ch_names=['pd'])




.. rst-class:: sphx-glr-horizontal


    *

      .. image:: /auto_examples/images/sphx_glr_plot_find_pd_events_002.png
            :class: sphx-glr-multi-img

    *

      .. image:: /auto_examples/images/sphx_glr_plot_find_pd_events_003.png
            :class: sphx-glr-multi-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Reading 0 ... 2178733  =      0.000 ...  2178.733 secs...
    Finding photodiode events
      0%|          | 0/8703 [00:00<?, ?it/s]      6%|6         | 537/8703 [00:00<00:01, 5365.60it/s]     12%|#2        | 1085/8703 [00:00<00:01, 5397.26it/s]     19%|#8        | 1632/8703 [00:00<00:01, 5417.24it/s]     25%|##5       | 2188/8703 [00:00<00:01, 5456.83it/s]     32%|###2      | 2799/8703 [00:00<00:01, 5636.16it/s]     39%|###8      | 3374/8703 [00:00<00:00, 5667.66it/s]     45%|####4     | 3879/8703 [00:00<00:00, 5452.84it/s]     50%|#####     | 4383/8703 [00:00<00:00, 5288.25it/s]     56%|#####6    | 4884/8703 [00:00<00:00, 5199.70it/s]     62%|######1   | 5385/8703 [00:01<00:00, 5061.06it/s]     69%|######8   | 5962/8703 [00:01<00:00, 5253.00it/s]     74%|#######4  | 6481/8703 [00:01<00:00, 5006.31it/s]     80%|########  | 6980/8703 [00:01<00:00, 4575.44it/s]     86%|########6 | 7485/8703 [00:01<00:00, 4707.56it/s]     91%|#########1| 7961/8703 [00:01<00:00, 4410.27it/s]     97%|#########6| 8410/8703 [00:01<00:00, 4426.42it/s]    100%|##########| 8703/8703 [00:01<00:00, 5016.03it/s]
    298 photodiode candidate events found
    Checking best behavior-photodiode difference alignments
      0%|          | 0/267 [00:00<?, ?it/s]      1%|1         | 4/267 [00:00<00:07, 37.28it/s]      3%|2         | 7/267 [00:00<00:07, 32.92it/s]      4%|4         | 11/267 [00:00<00:07, 32.25it/s]      5%|5         | 14/267 [00:00<00:09, 27.96it/s]      7%|6         | 18/267 [00:00<00:08, 30.72it/s]      8%|7         | 21/267 [00:00<00:09, 26.73it/s]      9%|9         | 25/267 [00:00<00:08, 29.04it/s]     11%|#         | 29/267 [00:00<00:08, 29.27it/s]     12%|#2        | 33/267 [00:01<00:07, 31.44it/s]     14%|#3        | 37/267 [00:01<00:07, 32.44it/s]     15%|#5        | 41/267 [00:01<00:08, 26.51it/s]     16%|#6        | 44/267 [00:01<00:08, 25.41it/s]     18%|#7        | 48/267 [00:01<00:08, 26.23it/s]     19%|#9        | 52/267 [00:01<00:07, 28.57it/s]     21%|##        | 55/267 [00:01<00:07, 27.79it/s]     22%|##1       | 58/267 [00:02<00:08, 24.53it/s]     23%|##2       | 61/267 [00:02<00:08, 23.59it/s]     24%|##3       | 64/267 [00:02<00:08, 22.58it/s]     25%|##5       | 68/267 [00:02<00:07, 25.61it/s]     27%|##6       | 71/267 [00:02<00:07, 25.18it/s]     28%|##7       | 74/267 [00:02<00:07, 25.19it/s]     29%|##8       | 77/267 [00:02<00:07, 24.38it/s]     30%|##9       | 80/267 [00:02<00:07, 24.15it/s]     31%|###1      | 83/267 [00:03<00:08, 22.77it/s]     33%|###2      | 87/267 [00:03<00:07, 24.36it/s]     34%|###3      | 90/267 [00:03<00:06, 25.31it/s]     35%|###5      | 94/267 [00:03<00:06, 26.34it/s]     37%|###6      | 98/267 [00:03<00:06, 26.98it/s]     38%|###7      | 101/267 [00:03<00:06, 25.89it/s]     39%|###9      | 105/267 [00:03<00:05, 27.86it/s]     40%|####      | 108/267 [00:03<00:05, 27.11it/s]     42%|####1     | 112/267 [00:04<00:05, 26.93it/s]     43%|####3     | 115/267 [00:04<00:05, 27.24it/s]     44%|####4     | 118/267 [00:04<00:05, 27.44it/s]     46%|####5     | 122/267 [00:04<00:05, 27.31it/s]     47%|####6     | 125/267 [00:04<00:06, 23.04it/s]     48%|####7     | 128/267 [00:04<00:05, 23.42it/s]     49%|####9     | 131/267 [00:04<00:05, 24.45it/s]     50%|#####     | 134/267 [00:05<00:05, 25.39it/s]     52%|#####2    | 139/267 [00:05<00:04, 28.30it/s]     53%|#####3    | 142/267 [00:05<00:04, 27.30it/s]     54%|#####4    | 145/267 [00:05<00:04, 27.36it/s]     55%|#####5    | 148/267 [00:05<00:04, 24.19it/s]     57%|#####6    | 152/267 [00:05<00:04, 26.19it/s]     58%|#####8    | 156/267 [00:05<00:04, 27.63it/s]     60%|#####9    | 159/267 [00:05<00:04, 26.15it/s]     61%|######1   | 163/267 [00:06<00:03, 28.81it/s]     63%|######2   | 167/267 [00:06<00:03, 27.98it/s]     64%|######3   | 170/267 [00:06<00:03, 26.29it/s]     65%|######4   | 173/267 [00:06<00:03, 26.41it/s]     66%|######6   | 177/267 [00:06<00:03, 27.85it/s]     68%|######7   | 181/267 [00:06<00:02, 29.80it/s]     69%|######9   | 185/267 [00:06<00:03, 26.91it/s]     70%|#######   | 188/267 [00:07<00:03, 23.41it/s]     72%|#######1  | 191/267 [00:07<00:03, 22.36it/s]     73%|#######2  | 194/267 [00:07<00:03, 23.39it/s]     74%|#######3  | 197/267 [00:07<00:02, 23.56it/s]     75%|#######5  | 201/267 [00:07<00:02, 25.58it/s]     76%|#######6  | 204/267 [00:07<00:02, 25.72it/s]     78%|#######7  | 207/267 [00:07<00:02, 23.69it/s]     79%|#######9  | 211/267 [00:07<00:02, 26.96it/s]     81%|########  | 216/267 [00:08<00:01, 28.40it/s]     82%|########2 | 220/267 [00:08<00:01, 29.13it/s]     84%|########3 | 224/267 [00:08<00:01, 29.48it/s]     85%|########5 | 228/267 [00:08<00:01, 31.86it/s]     87%|########6 | 232/267 [00:08<00:01, 30.41it/s]     88%|########8 | 236/267 [00:08<00:01, 29.56it/s]     90%|########9 | 240/267 [00:08<00:00, 28.92it/s]     91%|#########1| 243/267 [00:08<00:00, 29.16it/s]     92%|#########2| 246/267 [00:09<00:00, 28.16it/s]     94%|#########3| 250/267 [00:09<00:00, 27.75it/s]     95%|#########4| 253/267 [00:09<00:00, 26.54it/s]     96%|#########6| 257/267 [00:09<00:00, 27.23it/s]     97%|#########7| 260/267 [00:09<00:00, 20.99it/s]     99%|#########8| 263/267 [00:09<00:00, 16.89it/s]     99%|#########9| 265/267 [00:10<00:00, 13.50it/s]    100%|##########| 267/267 [00:10<00:00, 14.77it/s]    100%|##########| 267/267 [00:10<00:00, 25.99it/s]
    Best alignment with the photodiode shifted 160 ms relative to the first behavior event errors: min -32, q1 -9, med 0, q3 12, max 75
    Excluding events that have zero close events or more than one photodiode event within `chunk` time
    Excluding event 3, no event found
    Excluding event 5, off by 31.0 ms
    Excluding event 7, off by -31.0 ms
    Excluding event 8, off by 33.0 ms
    Excluding event 14, off by -30.0 ms
    Excluding event 16, no event found
    Excluding event 17, no event found
    Excluding event 18, no event found
    Excluding event 19, no event found
    Excluding event 20, no event found
    Excluding event 21, no event found
    Excluding event 24, no event found
    Excluding event 76, off by -30.0 ms
    Excluding event 96, off by 32.0 ms
    Excluding event 98, off by -32.0 ms
    Excluding event 202, off by -30.0 ms
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:308: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:315: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()




Add events relative to the photodiode events:

The photodiode is usually sychronized to one event (usually the fixation
so that if the deflections caused by the photodiode are large enough
to influence other channels through amplifier interactions it doesn't
cause issues with the analysis) so often the events of interest are
relative to the photodiode event. In the task a timer can be started at the
photodiode event and pulled for time at each of the following events.
These events are then passed in tsv file to be added to the events.
Note: if more than one photodiode event is used, the parser can be
used for each event separately using the keyword `add_event=True`.


.. code-block:: default


    pd_parser.add_pd_relative_events(
        fname, behf,
        relative_event_cols=['fix_duration', 'go_time', 'response_time'],
        relative_event_names=['ISI Onset', 'Go Cue', 'Response'])






.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Reading 0 ... 2178733  =      0.000 ...  2178.733 secs...




Save data to BIDS format:

This saves our data to BIDS format so that it's ready to be analyzed in a
reproducible way will all the necessary files. See
https://bids.neuroimaging.io/ and https://mne.tools/mne-bids/ for more
information about BIDS.


.. code-block:: default


    pd_parser.pd_parser_save_to_bids(op.join(out_dir, 'bids_dir'), fname,
                                     sub='1', task='mytask')




.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Used Annotations descriptions: ['Fixation', 'Go Cue', 'ISI Onset', 'Response']
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:818: RuntimeWarning: The unit for channel(s) pd has changed from V to NA.
      raw.set_channel_types({ch: 'stim' for ch in pd_channels
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Creating folder: /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/bids_dir/sub-1/ieeg

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/bids_dir/README'...

    References
    ----------
    Appelhoff, S., Sanderson, M., Brooks, T., Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Höchenberger, R., Welke, D., Brunner, C., Rockhill, A., Larson, E., Gramfort, A. and Jas, M. (2019). MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. Journal of Open Source Software 4: (1896). https://doi.org/10.21105/joss.01896

    Holdgraf, C., Appelhoff, S., Bickel, S., Bouchard, K., D'Ambrosio, S., David, O., … Hermes, D. (2019). iEEG-BIDS, extending the Brain Imaging Data Structure specification to human intracranial electrophysiology. Scientific Data, 6, 102. https://doi.org/10.1038/s41597-019-0105-7


    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/bids_dir/participants.tsv'...

    participant_id  age     sex     hand
    sub-1   n/a     n/a     n/a

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/bids_dir/participants.json'...

    {
        "participant_id": {
            "Description": "Unique participant identifier"
        },
        "age": {
            "Description": "Age of the participant at time of testing",
            "Units": "years"
        },
        "sex": {
            "Description": "Biological sex of the participant",
            "Levels": {
                "F": "female",
                "M": "male"
            }
        },
        "hand": {
            "Description": "Handedness of the participant",
            "Levels": {
                "R": "right",
                "L": "left",
                "A": "ambidextrous"
            }
        }
    }

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/bids_dir/sub-1/ieeg/sub-1_task-mytask_events.tsv'...

    onset   duration        trial_type      value   sample
    159.76  0.0     Fixation        1       159760
    160.46  0.0     ISI Onset       3       160460
    161.999 0.0     Go Cue  2       161999
    163.58  0.0     Response        4       163580
    166.238 0.0     Fixation        1       166238

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/bids_dir/dataset_description.json'...

    {
        "Name": " ",
        "BIDSVersion": "1.4.0",
        "DatasetType": "raw",
        "Authors": [
            "Please cite MNE-BIDS in your publication before removing this (citations in README)"
        ]
    }

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/bids_dir/sub-1/ieeg/sub-1_task-mytask_ieeg.json'...

    {
        "TaskName": "mytask",
        "Manufacturer": "Elekta",
        "PowerLineFrequency": 60.0,
        "SamplingFrequency": 1000.0,
        "SoftwareFilters": "n/a",
        "RecordingDuration": 2178.733,
        "RecordingType": "continuous",
        "iEEGReference": "n/a",
        "ECOGChannelCount": 0,
        "SEEGChannelCount": 3,
        "EEGChannelCount": 0,
        "EOGChannelCount": 0,
        "ECGChannelCount": 0,
        "EMGChannelCount": 0,
        "MiscChannelCount": 0,
        "TriggerChannelCount": 1
    }

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/bids_dir/sub-1/ieeg/sub-1_task-mytask_channels.tsv'...

    name    type    units   low_cutoff      high_cutoff     description     sampling_frequency      status  status_description
    pd      TRIG    n/a     0.0     500.0   Trigger 1000.0  good    n/a
    ch1     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch2     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch3     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    /Users/alexrockhill/software/mne-bids/mne_bids/write.py:1115: RuntimeWarning: Converting data files to BrainVision format
      warn('Converting data files to BrainVision format')

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/bids_dir/sub-1/sub-1_scans.tsv'...

    filename        acq_time
    ieeg/sub-1_task-mytask_ieeg.vhdr        n/a
    Wrote /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir__j4d4vez/bids_dir/sub-1/sub-1_scans.tsv entry with ieeg/sub-1_task-mytask_ieeg.vhdr.





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  22.736 seconds)


.. _sphx_glr_download_auto_examples_plot_find_pd_events.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: plot_find_pd_events.py <plot_find_pd_events.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: plot_find_pd_events.ipynb <plot_find_pd_events.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
