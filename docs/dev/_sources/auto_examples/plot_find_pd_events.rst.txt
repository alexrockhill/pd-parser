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








Simulate data and use it to make a raw object:

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

    Creating RawArray with float64 data, n_channels=1, n_times=2044106
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Creating RawArray with float64 data, n_channels=3, n_times=2044106
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif [done]




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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:531: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    Finding photodiode events
      0%|          | 0/16341 [00:00<?, ?it/s]      3%|2         | 474/16341 [00:00<00:03, 4727.90it/s]      6%|5         | 906/16341 [00:00<00:03, 4596.36it/s]      9%|8         | 1398/16341 [00:00<00:03, 4688.84it/s]     11%|#1        | 1858/16341 [00:00<00:03, 4659.56it/s]     14%|#4        | 2330/16341 [00:00<00:02, 4672.23it/s]     18%|#7        | 2863/16341 [00:00<00:02, 4850.75it/s]     21%|##        | 3350/16341 [00:00<00:02, 4855.96it/s]     23%|##3       | 3839/16341 [00:00<00:02, 4865.78it/s]     26%|##6       | 4329/16341 [00:00<00:02, 4874.36it/s]     29%|##9       | 4811/16341 [00:01<00:02, 4856.09it/s]     32%|###2      | 5298/16341 [00:01<00:02, 4857.47it/s]     35%|###5      | 5791/16341 [00:01<00:02, 4876.24it/s]     38%|###8      | 6273/16341 [00:01<00:02, 4827.01it/s]     41%|####1     | 6755/16341 [00:01<00:01, 4821.52it/s]     44%|####4     | 7241/16341 [00:01<00:01, 4830.99it/s]     47%|####7     | 7757/16341 [00:01<00:01, 4924.26it/s]     51%|#####     | 8256/16341 [00:01<00:01, 4811.15it/s]     53%|#####3    | 8737/16341 [00:01<00:01, 4580.58it/s]     56%|#####6    | 9198/16341 [00:01<00:01, 4421.78it/s]     59%|#####9    | 9643/16341 [00:02<00:01, 4399.82it/s]     62%|######2   | 10145/16341 [00:02<00:01, 4567.56it/s]     65%|######5   | 10648/16341 [00:02<00:01, 4696.29it/s]     68%|######8   | 11121/16341 [00:02<00:01, 4637.49it/s]     71%|#######   | 11588/16341 [00:02<00:01, 4642.62it/s]     74%|#######3  | 12068/16341 [00:02<00:00, 4687.23it/s]     77%|#######6  | 12566/16341 [00:02<00:00, 4768.11it/s]     80%|#######9  | 13045/16341 [00:02<00:00, 4738.14it/s]     83%|########2 | 13559/16341 [00:02<00:00, 4848.34it/s]     86%|########5 | 14046/16341 [00:02<00:00, 4775.43it/s]     89%|########9 | 14553/16341 [00:03<00:00, 4858.73it/s]     92%|#########2| 15041/16341 [00:03<00:00, 4600.92it/s]     95%|#########5| 15562/16341 [00:03<00:00, 4766.82it/s]     98%|#########8| 16069/16341 [00:03<00:00, 4851.57it/s]    100%|##########| 16341/16341 [00:03<00:00, 4760.43it/s]
    299 up-deflection photodiode candidate events found
    Checking best behavior-photodiode difference alignments
      0%|          | 0/299 [00:00<?, ?it/s]      1%|1         | 4/299 [00:00<00:07, 37.49it/s]      3%|3         | 10/299 [00:00<00:07, 40.88it/s]      5%|4         | 14/299 [00:00<00:07, 40.18it/s]      7%|7         | 21/299 [00:00<00:06, 42.81it/s]      8%|8         | 25/299 [00:00<00:06, 41.18it/s]     10%|9         | 29/299 [00:00<00:06, 38.78it/s]     11%|#1        | 34/299 [00:00<00:06, 40.81it/s]     13%|#2        | 38/299 [00:00<00:06, 38.16it/s]     14%|#4        | 42/299 [00:01<00:13, 19.57it/s]     15%|#5        | 45/299 [00:01<00:13, 18.45it/s]     16%|#6        | 48/299 [00:01<00:15, 15.74it/s]     17%|#7        | 51/299 [00:02<00:16, 15.21it/s]     18%|#7        | 53/299 [00:02<00:21, 11.60it/s]     18%|#8        | 55/299 [00:02<00:18, 13.09it/s]     20%|#9        | 59/299 [00:02<00:15, 15.75it/s]     21%|##1       | 64/299 [00:02<00:12, 19.30it/s]     23%|##2       | 68/299 [00:02<00:10, 22.50it/s]     24%|##3       | 71/299 [00:02<00:12, 18.72it/s]     25%|##4       | 74/299 [00:03<00:11, 19.13it/s]     26%|##5       | 77/299 [00:03<00:10, 21.03it/s]     27%|##7       | 81/299 [00:03<00:09, 23.96it/s]     29%|##8       | 86/299 [00:03<00:08, 25.99it/s]     30%|##9       | 89/299 [00:03<00:08, 25.56it/s]     31%|###1      | 93/299 [00:03<00:08, 25.52it/s]     32%|###2      | 96/299 [00:03<00:07, 26.61it/s]     33%|###3      | 100/299 [00:03<00:07, 28.05it/s]     35%|###5      | 105/299 [00:04<00:06, 30.97it/s]     36%|###6      | 109/299 [00:04<00:07, 24.43it/s]     38%|###7      | 113/299 [00:04<00:07, 26.18it/s]     39%|###9      | 117/299 [00:04<00:06, 27.29it/s]     40%|####      | 120/299 [00:04<00:06, 27.02it/s]     41%|####1     | 123/299 [00:04<00:06, 27.62it/s]     42%|####2     | 126/299 [00:04<00:06, 27.79it/s]     43%|####3     | 129/299 [00:05<00:09, 18.43it/s]     44%|####4     | 132/299 [00:05<00:08, 20.38it/s]     45%|####5     | 135/299 [00:05<00:09, 17.17it/s]     46%|####6     | 138/299 [00:05<00:09, 17.56it/s]     47%|####7     | 141/299 [00:05<00:08, 19.11it/s]     49%|####8     | 146/299 [00:05<00:06, 23.14it/s]     50%|#####     | 150/299 [00:06<00:05, 25.97it/s]     52%|#####1    | 154/299 [00:06<00:05, 28.40it/s]     53%|#####2    | 158/299 [00:06<00:04, 28.31it/s]     54%|#####4    | 162/299 [00:06<00:04, 29.36it/s]     56%|#####5    | 166/299 [00:06<00:04, 26.66it/s]     57%|#####6    | 169/299 [00:06<00:06, 20.83it/s]     58%|#####7    | 172/299 [00:07<00:06, 19.50it/s]     59%|#####8    | 176/299 [00:07<00:05, 22.49it/s]     61%|######    | 181/299 [00:07<00:04, 26.70it/s]     62%|######1   | 185/299 [00:07<00:04, 28.13it/s]     63%|######3   | 189/299 [00:07<00:03, 30.32it/s]     65%|######4   | 193/299 [00:07<00:03, 30.16it/s]     66%|######5   | 197/299 [00:07<00:03, 30.70it/s]     68%|######7   | 202/299 [00:07<00:02, 32.59it/s]     69%|######8   | 206/299 [00:08<00:03, 28.86it/s]     70%|#######   | 210/299 [00:08<00:03, 28.47it/s]     71%|#######1  | 213/299 [00:08<00:03, 28.05it/s]     72%|#######2  | 216/299 [00:08<00:04, 19.71it/s]     73%|#######3  | 219/299 [00:08<00:04, 19.76it/s]     75%|#######4  | 223/299 [00:08<00:03, 21.67it/s]     76%|#######5  | 226/299 [00:08<00:03, 23.20it/s]     77%|#######6  | 229/299 [00:09<00:03, 21.60it/s]     78%|#######7  | 232/299 [00:09<00:03, 21.72it/s]     79%|#######8  | 235/299 [00:09<00:03, 18.64it/s]     80%|#######9  | 238/299 [00:09<00:03, 19.34it/s]     81%|########  | 241/299 [00:09<00:03, 17.62it/s]     82%|########1 | 245/299 [00:09<00:02, 20.45it/s]     83%|########3 | 249/299 [00:10<00:02, 22.40it/s]     85%|########4 | 254/299 [00:10<00:01, 25.77it/s]     88%|########7 | 262/299 [00:10<00:01, 30.72it/s]     90%|########9 | 268/299 [00:10<00:00, 33.80it/s]     91%|######### | 272/299 [00:10<00:00, 33.53it/s]     93%|#########3| 279/299 [00:10<00:00, 37.87it/s]     95%|#########4| 284/299 [00:10<00:00, 35.67it/s]     97%|#########6| 289/299 [00:11<00:00, 38.86it/s]     98%|#########8| 294/299 [00:11<00:00, 38.00it/s]    100%|##########| 299/299 [00:11<00:00, 40.45it/s]    100%|##########| 299/299 [00:11<00:00, 26.55it/s]
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
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:331: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:338: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
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
        relative_event_cols=['go_time', 'response_time'],
        relative_event_names=['Go Cue', 'Response'])






.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...




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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Used Annotations descriptions: ['Fixation', 'Go Cue', 'Response']
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:879: RuntimeWarning: The unit for channel(s) pd has changed from V to NA.
      raw.set_channel_types({ch: 'stim' for ch in pd_channels
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Creating folder: /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/bids_dir/sub-1/ieeg

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/bids_dir/README'...

    References
    ----------
    Appelhoff, S., Sanderson, M., Brooks, T., Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Höchenberger, R., Welke, D., Brunner, C., Rockhill, A., Larson, E., Gramfort, A. and Jas, M. (2019). MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. Journal of Open Source Software 4: (1896). https://doi.org/10.21105/joss.01896

    Holdgraf, C., Appelhoff, S., Bickel, S., Bouchard, K., D'Ambrosio, S., David, O., … Hermes, D. (2019). iEEG-BIDS, extending the Brain Imaging Data Structure specification to human intracranial electrophysiology. Scientific Data, 6, 102. https://doi.org/10.1038/s41597-019-0105-7


    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/bids_dir/participants.tsv'...

    participant_id  age     sex     hand
    sub-1   n/a     n/a     n/a

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/bids_dir/participants.json'...

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

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/bids_dir/sub-1/ieeg/sub-1_task-mytask_events.tsv'...

    onset   duration        trial_type      value   sample
    12.27   0.0     Fixation        1       12270
    12.97   0.0     Go Cue  2       12970
    14.996  0.0     Response        3       14996
    18.299  0.0     Fixation        1       18299
    18.999  0.0     Go Cue  2       18999

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/bids_dir/dataset_description.json'...

    {
        "Name": " ",
        "BIDSVersion": "1.4.0",
        "DatasetType": "raw",
        "Authors": [
            "Please cite MNE-BIDS in your publication before removing this (citations in README)"
        ]
    }

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/bids_dir/sub-1/ieeg/sub-1_task-mytask_ieeg.json'...

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

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/bids_dir/sub-1/ieeg/sub-1_task-mytask_channels.tsv'...

    name    type    units   low_cutoff      high_cutoff     description     sampling_frequency      status  status_description
    pd      TRIG    n/a     0.0     500.0   Trigger 1000.0  good    n/a
    ch1     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch2     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch3     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    /Users/alexrockhill/software/mne-bids/mne_bids/write.py:1115: RuntimeWarning: Converting data files to BrainVision format
      warn('Converting data files to BrainVision format')

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/bids_dir/sub-1/sub-1_scans.tsv'...

    filename        acq_time
    ieeg/sub-1_task-mytask_ieeg.vhdr        n/a
    Wrote /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_blyoodhh/bids_dir/sub-1/sub-1_scans.tsv entry with ieeg/sub-1_task-mytask_ieeg.vhdr.





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  21.323 seconds)


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
