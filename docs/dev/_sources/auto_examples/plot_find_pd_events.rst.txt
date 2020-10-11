.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_plot_find_pd_events.py>`     to download the full example code
    .. rst-class:: sphx-glr-example-title

    .. _sphx_glr_auto_examples_plot_find_pd_events.py:


======================
Find Photodiode Events
======================
In this example, we use ``pd-parser`` to find photodiode events and
align them to behavior. Then, we save the data to BIDS format.


.. code-block:: default


    # Authors: Alex Rockhill <aprockhill@mailbox.org>
    #
    # License: BSD (3-clause)








Simulate data and use it to make a raw object:

We'll make an `mne.io.Raw object` so that we can save out some random
data with a photodiode event channel in it in `fif` format (a commonly used
electrophysiology data format).


.. code-block:: default

    import os.path as op
    import numpy as np

    import mne
    from mne.utils import _TempDir

    import pd_parser
    from pd_parser.parse_pd import _to_tsv

    out_dir = _TempDir()
    print(f'After running this example, you can find the data here: {out_dir}')

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





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    After running this example, you can find the data here: /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06
    Creating RawArray with float64 data, n_channels=1, n_times=2044106
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Creating RawArray with float64 data, n_channels=3, n_times=2044106
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif [done]




Make behavior data:

We'll make a dictionary with lists for the events that are time-stamped when
the photodiode was turned on and other events relative to those events.
We'll add some noise to the time-stamps so that we can see how behavior
might look in an experimental setting.
Let's make a task where there is a fixation stimulus, then a go cue,
and a then response as an example.


.. code-block:: default


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








Use the interactive graphical user interface (GUI) to find parameters:

On the documentation webpage, this is example is not interactive,
but if you download it as a jupyter notebook and run it or copy the code
into a console running python (ipython recommended), you can see how to
interact with the photodiode data to pick reasonable parameters by
following the instructions.


.. code-block:: default


    pd_parser.find_pd_params(fname, pd_ch_names=['pd'])




.. image:: /auto_examples/images/sphx_glr_plot_find_pd_events_001.png
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:581: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()




Find the photodiode events relative to the behavioral timing of interest:

This function will use the default parameters or the parameters you
found from :func:`pd_parser.find_pd_parameters` to find and align the
photodiode events, excluding events that were off because the commuter
hung up on computation, for instance. That data is saved in the same folder
as the raw file (in this case, a temperary directory generated by
:func:`_TempDir`). The data can be used directly, or it can be accessed via
:func:`pd_parser.pd_parser_save_to_bids` to store it in the brain imagine
data structure (BIDS) standardized format before using it.


.. code-block:: default


    pd_parser.parse_pd(fname, behf=behf, pd_ch_names=['pd'], max_len=1.5)




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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    Finding photodiode events
      0%|          | 0/10920 [00:00<?, ?it/s]      2%|2         | 227/10920 [00:00<00:04, 2243.73it/s]      3%|3         | 366/10920 [00:00<00:05, 1891.78it/s]      5%|5         | 579/10920 [00:00<00:05, 1946.99it/s]      7%|6         | 713/10920 [00:00<00:05, 1702.17it/s]      9%|8         | 978/10920 [00:00<00:05, 1906.31it/s]     12%|#2        | 1332/10920 [00:00<00:04, 2202.26it/s]     15%|#5        | 1644/10920 [00:00<00:03, 2415.02it/s]     19%|#8        | 2055/10920 [00:00<00:03, 2755.64it/s]     22%|##1       | 2377/10920 [00:00<00:02, 2876.68it/s]     25%|##4       | 2682/10920 [00:01<00:03, 2501.52it/s]     27%|##7       | 2953/10920 [00:01<00:04, 1802.36it/s]     31%|###       | 3348/10920 [00:01<00:03, 2153.29it/s]     35%|###4      | 3804/10920 [00:01<00:02, 2558.15it/s]     39%|###9      | 4261/10920 [00:01<00:02, 2946.53it/s]     43%|####3     | 4714/10920 [00:01<00:01, 3290.44it/s]     47%|####7     | 5178/10920 [00:01<00:01, 3604.28it/s]     52%|#####1    | 5643/10920 [00:01<00:01, 3863.39it/s]     56%|#####5    | 6093/10920 [00:02<00:01, 4032.86it/s]     60%|#####9    | 6542/10920 [00:02<00:01, 4159.48it/s]     64%|######4   | 7003/10920 [00:02<00:00, 4284.31it/s]     68%|######8   | 7449/10920 [00:02<00:00, 4265.60it/s]     72%|#######2  | 7888/10920 [00:02<00:00, 4139.06it/s]     76%|#######6  | 8312/10920 [00:02<00:00, 4123.64it/s]     80%|########  | 8749/10920 [00:02<00:00, 4194.54it/s]     84%|########4 | 9208/10920 [00:02<00:00, 4304.71it/s]     88%|########8 | 9643/10920 [00:02<00:00, 4261.88it/s]     92%|#########2| 10073/10920 [00:02<00:00, 4219.85it/s]     96%|#########6| 10498/10920 [00:03<00:00, 4200.05it/s]    100%|##########| 10920/10920 [00:03<00:00, 4145.68it/s]    100%|##########| 10920/10920 [00:03<00:00, 3459.96it/s]
    298 up-deflection photodiode candidate events found
    Checking best behavior-photodiode difference alignments
      0%|          | 0/299 [00:00<?, ?it/s]      1%|1         | 4/299 [00:00<00:08, 34.15it/s]      3%|3         | 10/299 [00:00<00:07, 37.01it/s]      5%|5         | 15/299 [00:00<00:07, 39.16it/s]      7%|7         | 21/299 [00:00<00:07, 39.60it/s]      9%|8         | 26/299 [00:00<00:06, 39.90it/s]     10%|#         | 30/299 [00:00<00:07, 38.41it/s]     12%|#1        | 35/299 [00:00<00:07, 37.51it/s]     13%|#3        | 40/299 [00:01<00:06, 38.59it/s]     15%|#4        | 44/299 [00:01<00:07, 34.61it/s]     16%|#6        | 49/299 [00:01<00:07, 35.26it/s]     18%|#8        | 54/299 [00:01<00:06, 36.07it/s]     20%|#9        | 59/299 [00:01<00:06, 37.39it/s]     21%|##1       | 63/299 [00:01<00:06, 35.35it/s]     22%|##2       | 67/299 [00:01<00:06, 34.36it/s]     24%|##3       | 71/299 [00:01<00:07, 32.19it/s]     25%|##5       | 75/299 [00:02<00:06, 33.81it/s]     26%|##6       | 79/299 [00:02<00:06, 33.29it/s]     28%|##7       | 83/299 [00:02<00:06, 33.62it/s]     29%|##9       | 87/299 [00:02<00:06, 33.58it/s]     31%|###1      | 93/299 [00:02<00:05, 36.98it/s]     33%|###2      | 98/299 [00:02<00:05, 37.31it/s]     34%|###4      | 102/299 [00:02<00:05, 37.26it/s]     35%|###5      | 106/299 [00:02<00:05, 35.24it/s]     37%|###6      | 110/299 [00:02<00:05, 35.99it/s]     38%|###8      | 114/299 [00:03<00:05, 36.96it/s]     39%|###9      | 118/299 [00:03<00:05, 35.96it/s]     41%|####      | 122/299 [00:03<00:05, 32.35it/s]     42%|####2     | 126/299 [00:03<00:05, 30.69it/s]     43%|####3     | 130/299 [00:03<00:05, 32.23it/s]     45%|####4     | 134/299 [00:03<00:05, 32.80it/s]     46%|####6     | 138/299 [00:03<00:04, 34.18it/s]     47%|####7     | 142/299 [00:03<00:04, 32.98it/s]     49%|####8     | 146/299 [00:04<00:04, 34.01it/s]     50%|#####     | 150/299 [00:04<00:04, 33.83it/s]     52%|#####1    | 154/299 [00:04<00:04, 33.94it/s]     53%|#####2    | 158/299 [00:04<00:04, 32.65it/s]     55%|#####4    | 163/299 [00:04<00:03, 34.40it/s]     56%|#####5    | 167/299 [00:04<00:04, 32.25it/s]     57%|#####7    | 171/299 [00:04<00:04, 29.14it/s]     59%|#####8    | 175/299 [00:05<00:04, 30.60it/s]     60%|#####9    | 179/299 [00:05<00:03, 30.74it/s]     61%|######1   | 183/299 [00:05<00:03, 31.37it/s]     63%|######2   | 187/299 [00:05<00:03, 31.96it/s]     64%|######3   | 191/299 [00:05<00:03, 32.75it/s]     65%|######5   | 195/299 [00:05<00:03, 31.92it/s]     67%|######6   | 199/299 [00:05<00:03, 33.02it/s]     68%|######7   | 203/299 [00:05<00:02, 33.17it/s]     69%|######9   | 207/299 [00:05<00:02, 32.72it/s]     71%|#######1  | 213/299 [00:06<00:02, 35.90it/s]     73%|#######2  | 217/299 [00:06<00:02, 36.21it/s]     74%|#######3  | 221/299 [00:06<00:02, 36.06it/s]     75%|#######5  | 225/299 [00:06<00:02, 35.36it/s]     77%|#######6  | 230/299 [00:06<00:01, 37.17it/s]     79%|#######8  | 235/299 [00:06<00:01, 36.85it/s]     80%|#######9  | 239/299 [00:06<00:01, 34.30it/s]     81%|########1 | 243/299 [00:06<00:01, 34.95it/s]     83%|########2 | 247/299 [00:07<00:01, 31.66it/s]     84%|########3 | 251/299 [00:07<00:01, 31.98it/s]     86%|########5 | 257/299 [00:07<00:01, 34.57it/s]     88%|########8 | 264/299 [00:07<00:00, 40.09it/s]     90%|########9 | 269/299 [00:07<00:00, 41.83it/s]     92%|#########1| 274/299 [00:07<00:00, 42.10it/s]     94%|#########3| 281/299 [00:07<00:00, 47.25it/s]     96%|#########5| 287/299 [00:07<00:00, 44.97it/s]     98%|#########7| 292/299 [00:08<00:00, 42.86it/s]     99%|#########9| 297/299 [00:08<00:00, 41.72it/s]    100%|##########| 299/299 [00:08<00:00, 36.31it/s]
    Best alignment with the photodiode shifted 12 ms relative to the first behavior event
    errors: min -32, q1 -10, med 0, q3 10, max 75
    Excluding events that have zero close events or more than one photodiode event within `max_len` time
    Excluding event 5, off by 32 ms
    Excluding event 7, off by -30 ms
    Excluding event 8, off by 32 ms
    Excluding event 9, no event found
    Excluding event 14, off by -30 ms
    Excluding event 27, no event found
    Excluding event 76, off by -31 ms
    Excluding event 96, off by 31 ms
    Excluding event 98, off by -32 ms
    Excluding event 235, no event found
    Excluding event 279, off by 31 ms
    Excluding event 289, off by -30 ms
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:364: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:371: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()




Add events relative to the photodiode events:

The photodiode is usually sychronized to one event (e.g. the fixation
so that if the deflections caused by the photodiode are large enough
to influence other channels through amplifier interactions it doesn't
cause issues with the analysis) so often the events of interest are
relative to the photodiode event. In the task a timer can be started at the
photodiode event and checked each time a subsequent event occurs.
These events should then be recorded in tsv file, which can be passed to
``pd-parser`` in order to add the events.
Note: if more than one photodiode event is used, the parser can be
used for each event separately using the keyword `add_event=True`.


.. code-block:: default


    pd_parser.add_pd_relative_events(
        fname, behf,
        relative_event_cols=['go_time', 'response_time'],
        relative_event_names=['Go Cue', 'Response'])






.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...




Save data to BIDS format:

This saves our data to BIDS format so that it's ready to be analyzed in a
reproducible way; BIDS requires all the files the BIDS community has deemed
necessary for analysis, so you should have everything you need to continue
on with an analysis at this point. See https://bids.neuroimaging.io/ and
https://mne.tools/mne-bids/ for more information about BIDS.


.. code-block:: default


    pd_parser.pd_parser_save_to_bids(op.join(out_dir, 'bids_dir'), fname,
                                     sub='1', task='mytask')




.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Used Annotations descriptions: ['Fixation', 'Go Cue', 'Response']
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:981: RuntimeWarning: The unit for channel(s) pd has changed from V to NA.
      raw.set_channel_types({ch: 'stim' for ch in pd_channels
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Creating folder: /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/bids_dir/sub-1/ieeg

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/bids_dir/README'...

    References
    ----------
    Appelhoff, S., Sanderson, M., Brooks, T., Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Höchenberger, R., Welke, D., Brunner, C., Rockhill, A., Larson, E., Gramfort, A. and Jas, M. (2019). MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. Journal of Open Source Software 4: (1896). https://doi.org/10.21105/joss.01896

    Holdgraf, C., Appelhoff, S., Bickel, S., Bouchard, K., D'Ambrosio, S., David, O., … Hermes, D. (2019). iEEG-BIDS, extending the Brain Imaging Data Structure specification to human intracranial electrophysiology. Scientific Data, 6, 102. https://doi.org/10.1038/s41597-019-0105-7


    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/bids_dir/participants.tsv'...

    participant_id  age     sex     hand
    sub-1   n/a     n/a     n/a

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/bids_dir/participants.json'...

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

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/bids_dir/sub-1/ieeg/sub-1_task-mytask_events.tsv'...

    onset   duration        trial_type      value   sample
    12.27   0.0     Fixation        1       12270
    12.97   0.0     Go Cue  2       12970
    14.996  0.0     Response        3       14996
    18.299  0.0     Fixation        1       18299
    18.999  0.0     Go Cue  2       18999

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/bids_dir/dataset_description.json'...

    {
        "Name": " ",
        "BIDSVersion": "1.4.0",
        "DatasetType": "raw",
        "Authors": [
            "Please cite MNE-BIDS in your publication before removing this (citations in README)"
        ]
    }

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/bids_dir/sub-1/ieeg/sub-1_task-mytask_ieeg.json'...

    {
        "TaskName": "mytask",
        "Manufacturer": "Elekta",
        "PowerLineFrequency": 60.0,
        "SamplingFrequency": 1000.0,
        "SoftwareFilters": "n/a",
        "RecordingDuration": 2044.105,
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

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/bids_dir/sub-1/ieeg/sub-1_task-mytask_channels.tsv'...

    name    type    units   low_cutoff      high_cutoff     description     sampling_frequency      status  status_description
    pd      TRIG    n/a     0.0     500.0   Trigger 1000.0  good    n/a
    ch1     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch2     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch3     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    /Users/alexrockhill/software/mne-bids/mne_bids/write.py:1115: RuntimeWarning: Converting data files to BrainVision format
      warn('Converting data files to BrainVision format')

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/bids_dir/sub-1/sub-1_scans.tsv'...

    filename        acq_time
    ieeg/sub-1_task-mytask_ieeg.vhdr        n/a
    Wrote /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_87musw06/bids_dir/sub-1/sub-1_scans.tsv entry with ieeg/sub-1_task-mytask_ieeg.vhdr.





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  20.175 seconds)


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
