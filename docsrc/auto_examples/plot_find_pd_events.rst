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

    After running this example, you can find the data here: /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh
    Creating RawArray with float64 data, n_channels=1, n_times=2044106
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Creating RawArray with float64 data, n_channels=3, n_times=2044106
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif [done]




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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:653: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    Finding photodiode events
      0%|          | 0/10920 [00:00<?, ?it/s]      4%|4         | 443/10920 [00:00<00:02, 4421.91it/s]      8%|8         | 878/10920 [00:00<00:02, 4397.77it/s]     11%|#1        | 1230/10920 [00:00<00:02, 4090.03it/s]     15%|#5        | 1641/10920 [00:00<00:02, 4092.92it/s]     19%|#8        | 2060/10920 [00:00<00:02, 4118.76it/s]     23%|##2       | 2467/10920 [00:00<00:02, 4101.69it/s]     26%|##6       | 2883/10920 [00:00<00:01, 4117.61it/s]     30%|###       | 3297/10920 [00:00<00:01, 4122.54it/s]     34%|###3      | 3685/10920 [00:00<00:01, 3905.76it/s]     37%|###7      | 4084/10920 [00:01<00:01, 3929.32it/s]     41%|####      | 4467/10920 [00:01<00:01, 3803.37it/s]     45%|####4     | 4885/10920 [00:01<00:01, 3908.89it/s]     49%|####8     | 5298/10920 [00:01<00:01, 3969.09it/s]     52%|#####2    | 5710/10920 [00:01<00:01, 4012.05it/s]     56%|#####6    | 6151/10920 [00:01<00:01, 4122.87it/s]     60%|######    | 6583/10920 [00:01<00:01, 4177.55it/s]     64%|######4   | 7029/10920 [00:01<00:00, 4255.95it/s]     68%|######8   | 7476/10920 [00:01<00:00, 4317.92it/s]     73%|#######2  | 7919/10920 [00:01<00:00, 4350.12it/s]     77%|#######6  | 8363/10920 [00:02<00:00, 4376.34it/s]     81%|########  | 8806/10920 [00:02<00:00, 4392.28it/s]     85%|########4 | 9246/10920 [00:02<00:00, 4391.86it/s]     89%|########8 | 9686/10920 [00:02<00:00, 4340.85it/s]     93%|#########2| 10121/10920 [00:02<00:00, 4304.13it/s]     97%|#########6| 10552/10920 [00:02<00:00, 4230.34it/s]    100%|##########| 10920/10920 [00:02<00:00, 4050.83it/s]
    298 up-deflection photodiode candidate events found
    Checking best alignments
      0%|          | 0/299 [00:00<?, ?it/s]      1%|1         | 3/299 [00:00<00:12, 23.73it/s]      2%|1         | 5/299 [00:00<00:13, 21.94it/s]      3%|3         | 9/299 [00:00<00:11, 24.18it/s]      4%|3         | 11/299 [00:00<00:14, 20.57it/s]      5%|4         | 14/299 [00:00<00:12, 22.47it/s]      7%|6         | 20/299 [00:00<00:10, 26.57it/s]      8%|7         | 23/299 [00:00<00:10, 25.67it/s]      9%|9         | 28/299 [00:00<00:09, 28.98it/s]     11%|#1        | 34/299 [00:01<00:07, 33.69it/s]     13%|#3        | 39/299 [00:01<00:07, 36.59it/s]     15%|#4        | 44/299 [00:01<00:07, 35.37it/s]     16%|#6        | 49/299 [00:01<00:06, 36.11it/s]     18%|#8        | 54/299 [00:01<00:06, 37.36it/s]     20%|#9        | 59/299 [00:01<00:06, 39.46it/s]     21%|##1       | 64/299 [00:01<00:05, 39.82it/s]     23%|##3       | 69/299 [00:01<00:06, 38.26it/s]     25%|##4       | 74/299 [00:02<00:05, 38.04it/s]     26%|##6       | 78/299 [00:02<00:05, 37.88it/s]     28%|##7       | 83/299 [00:02<00:05, 38.26it/s]     29%|##9       | 87/299 [00:02<00:05, 37.28it/s]     31%|###1      | 93/299 [00:02<00:05, 40.06it/s]     33%|###2      | 98/299 [00:02<00:04, 40.70it/s]     34%|###4      | 103/299 [00:02<00:04, 42.55it/s]     36%|###6      | 108/299 [00:02<00:04, 39.54it/s]     38%|###7      | 113/299 [00:03<00:04, 40.77it/s]     39%|###9      | 118/299 [00:03<00:04, 37.43it/s]     41%|####      | 122/299 [00:03<00:05, 32.69it/s]     42%|####2     | 126/299 [00:03<00:05, 32.26it/s]     43%|####3     | 130/299 [00:03<00:05, 33.39it/s]     45%|####4     | 134/299 [00:03<00:04, 33.86it/s]     46%|####6     | 138/299 [00:03<00:04, 35.17it/s]     47%|####7     | 142/299 [00:03<00:04, 34.19it/s]     49%|####8     | 146/299 [00:04<00:04, 35.59it/s]     50%|#####     | 150/299 [00:04<00:04, 35.38it/s]     52%|#####1    | 154/299 [00:04<00:04, 35.18it/s]     53%|#####2    | 158/299 [00:04<00:04, 33.52it/s]     55%|#####4    | 163/299 [00:04<00:03, 35.43it/s]     56%|#####5    | 167/299 [00:04<00:03, 34.78it/s]     57%|#####7    | 171/299 [00:04<00:04, 31.93it/s]     59%|#####8    | 175/299 [00:04<00:03, 33.14it/s]     60%|#####9    | 179/299 [00:05<00:03, 32.13it/s]     61%|######1   | 183/299 [00:05<00:03, 32.36it/s]     63%|######2   | 187/299 [00:05<00:03, 29.63it/s]     64%|######3   | 191/299 [00:05<00:03, 30.71it/s]     65%|######5   | 195/299 [00:05<00:03, 30.44it/s]     67%|######6   | 199/299 [00:05<00:03, 32.11it/s]     68%|######7   | 203/299 [00:05<00:02, 32.68it/s]     69%|######9   | 207/299 [00:05<00:02, 32.65it/s]     71%|#######1  | 213/299 [00:06<00:02, 36.21it/s]     73%|#######2  | 217/299 [00:06<00:02, 36.87it/s]     74%|#######3  | 221/299 [00:06<00:02, 35.98it/s]     75%|#######5  | 225/299 [00:06<00:02, 35.19it/s]     77%|#######6  | 230/299 [00:06<00:01, 36.61it/s]     78%|#######8  | 234/299 [00:06<00:01, 37.43it/s]     80%|#######9  | 238/299 [00:06<00:01, 32.77it/s]     81%|########  | 242/299 [00:06<00:01, 32.55it/s]     82%|########2 | 246/299 [00:07<00:01, 32.86it/s]     84%|########3 | 250/299 [00:07<00:01, 32.71it/s]     85%|########4 | 254/299 [00:07<00:01, 32.95it/s]     87%|########7 | 261/299 [00:07<00:00, 38.74it/s]     89%|########9 | 267/299 [00:07<00:00, 40.69it/s]     91%|######### | 272/299 [00:07<00:00, 38.09it/s]     93%|#########3| 279/299 [00:07<00:00, 43.29it/s]     95%|#########4| 284/299 [00:07<00:00, 43.09it/s]     97%|#########6| 289/299 [00:08<00:00, 42.47it/s]     98%|#########8| 294/299 [00:08<00:00, 40.31it/s]    100%|##########| 299/299 [00:08<00:00, 42.04it/s]    100%|##########| 299/299 [00:08<00:00, 36.19it/s]
    Best alignment with the events shifted 12 ms relative to the first behavior event
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
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:436: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:443: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
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


    pd_parser.add_relative_events(
        fname, behf,
        relative_event_cols=['go_time', 'response_time'],
        relative_event_names=['Go Cue', 'Response'])






.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif...
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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Used Annotations descriptions: ['Fixation', 'Go Cue', 'Response']
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:1173: RuntimeWarning: The unit for channel(s) pd has changed from V to NA.
      raw.set_channel_types({ch: 'stim' for ch in pd_channels
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Creating folder: /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/bids_dir/sub-1/ieeg

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/bids_dir/README'...

    References
    ----------
    Appelhoff, S., Sanderson, M., Brooks, T., Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Höchenberger, R., Welke, D., Brunner, C., Rockhill, A., Larson, E., Gramfort, A. and Jas, M. (2019). MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. Journal of Open Source Software 4: (1896). https://doi.org/10.21105/joss.01896

    Holdgraf, C., Appelhoff, S., Bickel, S., Bouchard, K., D'Ambrosio, S., David, O., … Hermes, D. (2019). iEEG-BIDS, extending the Brain Imaging Data Structure specification to human intracranial electrophysiology. Scientific Data, 6, 102. https://doi.org/10.1038/s41597-019-0105-7


    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/bids_dir/participants.tsv'...

    participant_id  age     sex     hand
    sub-1   n/a     n/a     n/a

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/bids_dir/participants.json'...

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

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/bids_dir/sub-1/ieeg/sub-1_task-mytask_events.tsv'...

    onset   duration        trial_type      value   sample
    12.27   0.0     Fixation        1       12270
    12.97   0.0     Go Cue  2       12970
    14.996  0.0     Response        3       14996
    18.299  0.0     Fixation        1       18299
    18.999  0.0     Go Cue  2       18999

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/bids_dir/dataset_description.json'...

    {
        "Name": " ",
        "BIDSVersion": "1.4.0",
        "DatasetType": "raw",
        "Authors": [
            "Please cite MNE-BIDS in your publication before removing this (citations in README)"
        ]
    }

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/bids_dir/sub-1/ieeg/sub-1_task-mytask_ieeg.json'...

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

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/bids_dir/sub-1/ieeg/sub-1_task-mytask_channels.tsv'...

    name    type    units   low_cutoff      high_cutoff     description     sampling_frequency      status  status_description
    pd      TRIG    n/a     0.0     500.0   Trigger 1000.0  good    n/a
    ch1     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch2     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch3     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    /Users/alexrockhill/software/mne-bids/mne_bids/write.py:1115: RuntimeWarning: Converting data files to BrainVision format
      warn('Converting data files to BrainVision format')

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/bids_dir/sub-1/sub-1_scans.tsv'...

    filename        acq_time
    ieeg/sub-1_task-mytask_ieeg.vhdr        n/a
    Wrote /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_zczb3reh/bids_dir/sub-1/sub-1_scans.tsv entry with ieeg/sub-1_task-mytask_ieeg.vhdr.





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  17.287 seconds)


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
