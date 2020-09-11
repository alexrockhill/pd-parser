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
                                      n_secs_on=2.5)[0]
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
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif [done]




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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Reading 0 ... 2178733  =      0.000 ...  2178.733 secs...
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:527: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Reading 0 ... 2178733  =      0.000 ...  2178.733 secs...
    Finding photodiode events
      0%|          | 0/8703 [00:00<?, ?it/s]      7%|7         | 643/8703 [00:00<00:01, 6423.05it/s]     16%|#5        | 1373/8703 [00:00<00:01, 6661.25it/s]     23%|##3       | 2037/8703 [00:00<00:01, 6654.75it/s]     31%|###       | 2671/8703 [00:00<00:00, 6550.26it/s]     38%|###8      | 3313/8703 [00:00<00:00, 6510.17it/s]     46%|####6     | 4012/8703 [00:00<00:00, 6646.21it/s]     54%|#####3    | 4677/8703 [00:00<00:00, 6645.59it/s]     62%|######1   | 5379/8703 [00:00<00:00, 6752.83it/s]     69%|######9   | 6038/8703 [00:00<00:00, 6699.87it/s]     77%|#######6  | 6686/8703 [00:01<00:00, 6629.22it/s]     84%|########4 | 7332/8703 [00:01<00:00, 4806.02it/s]     90%|######### | 7872/8703 [00:01<00:00, 4080.58it/s]     96%|#########5| 8342/8703 [00:01<00:00, 4246.88it/s]    100%|##########| 8703/8703 [00:01<00:00, 5503.30it/s]
    298 up-deflection photodiode candidate events found
    Checking best behavior-photodiode difference alignments
      0%|          | 0/267 [00:00<?, ?it/s]      2%|1         | 5/267 [00:00<00:06, 43.00it/s]      4%|3         | 10/267 [00:00<00:05, 44.81it/s]      6%|5         | 15/267 [00:00<00:05, 45.94it/s]      8%|7         | 21/267 [00:00<00:05, 46.01it/s]     10%|#         | 27/267 [00:00<00:05, 47.73it/s]     13%|#2        | 34/267 [00:00<00:04, 52.11it/s]     15%|#4        | 39/267 [00:00<00:04, 48.15it/s]     16%|#6        | 44/267 [00:00<00:05, 44.47it/s]     19%|#8        | 50/267 [00:01<00:04, 48.02it/s]     21%|##        | 55/267 [00:01<00:04, 47.67it/s]     22%|##2       | 60/267 [00:01<00:04, 41.75it/s]     24%|##4       | 65/267 [00:01<00:05, 38.76it/s]     27%|##6       | 71/267 [00:01<00:04, 42.46it/s]     28%|##8       | 76/267 [00:01<00:04, 42.84it/s]     30%|###       | 81/267 [00:01<00:04, 40.26it/s]     32%|###2      | 86/267 [00:01<00:04, 42.07it/s]     34%|###4      | 91/267 [00:02<00:04, 42.50it/s]     36%|###5      | 96/267 [00:02<00:03, 44.00it/s]     38%|###7      | 101/267 [00:02<00:03, 44.06it/s]     40%|###9      | 106/267 [00:02<00:03, 44.77it/s]     42%|####1     | 111/267 [00:02<00:03, 46.05it/s]     43%|####3     | 116/267 [00:02<00:03, 46.40it/s]     45%|####5     | 121/267 [00:02<00:03, 43.74it/s]     47%|####7     | 126/267 [00:02<00:04, 30.78it/s]     49%|####8     | 130/267 [00:03<00:04, 29.45it/s]     50%|#####     | 134/267 [00:03<00:04, 30.92it/s]     52%|#####2    | 140/267 [00:03<00:03, 34.47it/s]     54%|#####4    | 145/267 [00:03<00:03, 37.45it/s]     56%|#####6    | 150/267 [00:03<00:03, 34.93it/s]     58%|#####8    | 156/267 [00:03<00:02, 38.33it/s]     60%|######    | 161/267 [00:03<00:02, 41.04it/s]     62%|######2   | 166/267 [00:03<00:02, 40.12it/s]     64%|######4   | 171/267 [00:04<00:02, 37.85it/s]     66%|######5   | 176/267 [00:04<00:02, 39.06it/s]     68%|######7   | 181/267 [00:04<00:02, 41.64it/s]     70%|######9   | 186/267 [00:04<00:02, 38.74it/s]     72%|#######1  | 191/267 [00:04<00:02, 35.78it/s]     73%|#######3  | 196/267 [00:04<00:01, 37.45it/s]     75%|#######5  | 201/267 [00:04<00:01, 38.42it/s]     77%|#######7  | 206/267 [00:05<00:01, 39.03it/s]     79%|#######9  | 211/267 [00:05<00:01, 41.08it/s]     81%|########  | 216/267 [00:05<00:01, 42.33it/s]     83%|########2 | 221/267 [00:05<00:01, 43.55it/s]     85%|########4 | 226/267 [00:05<00:00, 44.19it/s]     87%|########6 | 231/267 [00:05<00:00, 45.49it/s]     88%|########8 | 236/267 [00:05<00:00, 42.23it/s]     90%|######### | 241/267 [00:05<00:00, 42.98it/s]     92%|#########2| 246/267 [00:05<00:00, 42.23it/s]     94%|#########4| 251/267 [00:06<00:00, 42.50it/s]     96%|#########5| 256/267 [00:06<00:00, 42.18it/s]     98%|#########7| 261/267 [00:06<00:00, 41.88it/s]    100%|#########9| 266/267 [00:06<00:00, 41.81it/s]    100%|##########| 267/267 [00:06<00:00, 41.52it/s]
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
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:309: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:316: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif...
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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Used Annotations descriptions: ['Fixation', 'Go Cue', 'ISI Onset', 'Response']
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:829: RuntimeWarning: The unit for channel(s) pd has changed from V to NA.
      raw.set_channel_types({ch: 'stim' for ch in pd_channels
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2178733 =      0.000 ...  2178.733 secs
    Ready.
    Creating folder: /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/bids_dir/sub-1/ieeg

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/bids_dir/README'...

    References
    ----------
    Appelhoff, S., Sanderson, M., Brooks, T., Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Höchenberger, R., Welke, D., Brunner, C., Rockhill, A., Larson, E., Gramfort, A. and Jas, M. (2019). MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. Journal of Open Source Software 4: (1896). https://doi.org/10.21105/joss.01896

    Holdgraf, C., Appelhoff, S., Bickel, S., Bouchard, K., D'Ambrosio, S., David, O., … Hermes, D. (2019). iEEG-BIDS, extending the Brain Imaging Data Structure specification to human intracranial electrophysiology. Scientific Data, 6, 102. https://doi.org/10.1038/s41597-019-0105-7


    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/bids_dir/participants.tsv'...

    participant_id  age     sex     hand
    sub-1   n/a     n/a     n/a

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/bids_dir/participants.json'...

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

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/bids_dir/sub-1/ieeg/sub-1_task-mytask_events.tsv'...

    onset   duration        trial_type      value   sample
    159.76  0.0     Fixation        1       159760
    160.46  0.0     ISI Onset       3       160460
    161.999 0.0     Go Cue  2       161999
    163.58  0.0     Response        4       163580
    166.238 0.0     Fixation        1       166238

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/bids_dir/dataset_description.json'...

    {
        "Name": " ",
        "BIDSVersion": "1.4.0",
        "DatasetType": "raw",
        "Authors": [
            "Please cite MNE-BIDS in your publication before removing this (citations in README)"
        ]
    }

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/bids_dir/sub-1/ieeg/sub-1_task-mytask_ieeg.json'...

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

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/bids_dir/sub-1/ieeg/sub-1_task-mytask_channels.tsv'...

    name    type    units   low_cutoff      high_cutoff     description     sampling_frequency      status  status_description
    pd      TRIG    n/a     0.0     500.0   Trigger 1000.0  good    n/a
    ch1     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch2     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch3     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    /Users/alexrockhill/software/mne-bids/mne_bids/write.py:1115: RuntimeWarning: Converting data files to BrainVision format
      warn('Converting data files to BrainVision format')

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/bids_dir/sub-1/sub-1_scans.tsv'...

    filename        acq_time
    ieeg/sub-1_task-mytask_ieeg.vhdr        n/a
    Wrote /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_o51nsh2t/bids_dir/sub-1/sub-1_scans.tsv entry with ieeg/sub-1_task-mytask_ieeg.vhdr.





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  15.491 seconds)


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
