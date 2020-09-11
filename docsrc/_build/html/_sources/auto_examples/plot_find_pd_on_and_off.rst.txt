.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_plot_find_pd_on_and_off.py>`     to download the full example code
    .. rst-class:: sphx-glr-example-title

    .. _sphx_glr_auto_examples_plot_find_pd_on_and_off.py:


=====================================
02. Find Photodiode On and Off Events
=====================================
In this example, we use pd-parser to find photodiode events and
align both the onset of the deflection and the cessation to
to behavior.


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






.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Creating RawArray with float64 data, n_channels=1, n_times=2044106
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Creating RawArray with float64 data, n_channels=3, n_times=2044106
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kzljuy96/sub-1_task-mytask_raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kzljuy96/sub-1_task-mytask_raw.fif [done]




Find the photodiode events relative to the behavioral timing of interest:

This function will use the default parameters to find and align the
photodiode events, excluding events that were off.
One percent of the 300 events (3) were corrupted as shown in the plots and
some were too far off from large offsets that we're going to exclude them.


.. code-block:: default


    pd_parser.parse_pd(fname, pd_event_name='Stim On', behf=behf,
                       pd_ch_names=['pd'], beh_col='time')




.. rst-class:: sphx-glr-horizontal


    *

      .. image:: /auto_examples/images/sphx_glr_plot_find_pd_on_and_off_001.png
            :class: sphx-glr-multi-img

    *

      .. image:: /auto_examples/images/sphx_glr_plot_find_pd_on_and_off_002.png
            :class: sphx-glr-multi-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kzljuy96/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kzljuy96/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    Finding photodiode events
      0%|          | 0/16341 [00:00<?, ?it/s]      3%|3         | 501/16341 [00:00<00:03, 5001.10it/s]      6%|6         | 1001/16341 [00:00<00:03, 4998.62it/s]      9%|9         | 1524/16341 [00:00<00:02, 5064.73it/s]     13%|#2        | 2059/16341 [00:00<00:02, 5145.98it/s]     15%|#5        | 2456/16341 [00:00<00:02, 4724.33it/s]     18%|#8        | 2968/16341 [00:00<00:02, 4834.73it/s]     21%|##1       | 3486/16341 [00:00<00:02, 4932.63it/s]     25%|##4       | 4021/16341 [00:00<00:02, 5050.73it/s]     28%|##7       | 4554/16341 [00:00<00:02, 5129.59it/s]     31%|###1      | 5092/16341 [00:01<00:02, 5201.15it/s]     34%|###4      | 5610/16341 [00:01<00:02, 5193.79it/s]     38%|###7      | 6134/16341 [00:01<00:01, 5206.16it/s]     41%|####      | 6671/16341 [00:01<00:01, 5252.14it/s]     44%|####4     | 7203/16341 [00:01<00:01, 5270.73it/s]     47%|####7     | 7728/16341 [00:01<00:01, 5146.64it/s]     51%|#####     | 8265/16341 [00:01<00:01, 5210.65it/s]     54%|#####3    | 8801/16341 [00:01<00:01, 5253.05it/s]     57%|#####7    | 9326/16341 [00:01<00:01, 5140.10it/s]     60%|######    | 9841/16341 [00:01<00:01, 5110.61it/s]     63%|######3   | 10353/16341 [00:02<00:01, 4922.26it/s]     66%|######6   | 10862/16341 [00:02<00:01, 4969.95it/s]     70%|######9   | 11387/16341 [00:02<00:00, 5048.30it/s]     73%|#######2  | 11896/16341 [00:02<00:00, 5059.30it/s]     76%|#######5  | 12403/16341 [00:02<00:00, 5046.88it/s]     79%|#######8  | 12909/16341 [00:02<00:00, 5049.10it/s]     82%|########2 | 13420/16341 [00:02<00:00, 5066.31it/s]     85%|########5 | 13927/16341 [00:02<00:00, 4903.99it/s]     88%|########8 | 14446/16341 [00:02<00:00, 4985.21it/s]     91%|#########1| 14947/16341 [00:02<00:00, 4989.93it/s]     95%|#########4| 15451/16341 [00:03<00:00, 5001.13it/s]     98%|#########7| 15962/16341 [00:03<00:00, 5032.21it/s]    100%|##########| 16341/16341 [00:03<00:00, 5070.65it/s]
    300 up-deflection photodiode candidate events found
    Checking best behavior-photodiode difference alignments
      0%|          | 0/299 [00:00<?, ?it/s]      1%|1         | 4/299 [00:00<00:07, 37.38it/s]      4%|3         | 11/299 [00:00<00:06, 43.29it/s]      5%|5         | 16/299 [00:00<00:06, 44.10it/s]      7%|7         | 21/299 [00:00<00:06, 45.26it/s]      9%|8         | 26/299 [00:00<00:06, 45.23it/s]     10%|#         | 31/299 [00:00<00:06, 43.89it/s]     12%|#2        | 36/299 [00:00<00:05, 43.95it/s]     14%|#3        | 41/299 [00:00<00:06, 38.27it/s]     15%|#5        | 45/299 [00:01<00:06, 37.86it/s]     16%|#6        | 49/299 [00:01<00:06, 36.18it/s]     18%|#8        | 54/299 [00:01<00:06, 37.87it/s]     20%|#9        | 59/299 [00:01<00:06, 38.47it/s]     21%|##1       | 63/299 [00:01<00:06, 35.42it/s]     22%|##2       | 67/299 [00:01<00:07, 30.72it/s]     24%|##3       | 71/299 [00:01<00:07, 29.66it/s]     25%|##5       | 75/299 [00:02<00:07, 28.40it/s]     26%|##6       | 79/299 [00:02<00:07, 30.48it/s]     28%|##7       | 83/299 [00:02<00:06, 30.90it/s]     29%|##9       | 87/299 [00:02<00:06, 31.18it/s]     30%|###       | 91/299 [00:02<00:06, 33.24it/s]     32%|###1      | 95/299 [00:02<00:06, 31.17it/s]     33%|###3      | 99/299 [00:02<00:06, 30.62it/s]     34%|###4      | 103/299 [00:02<00:06, 30.18it/s]     36%|###5      | 107/299 [00:03<00:06, 30.03it/s]     37%|###7      | 111/299 [00:03<00:06, 29.41it/s]     39%|###8      | 116/299 [00:03<00:05, 31.44it/s]     40%|####      | 120/299 [00:03<00:05, 31.77it/s]     41%|####1     | 124/299 [00:03<00:05, 33.16it/s]     43%|####2     | 128/299 [00:03<00:05, 32.12it/s]     44%|####4     | 132/299 [00:03<00:05, 33.25it/s]     45%|####5     | 136/299 [00:03<00:05, 30.80it/s]     47%|####6     | 140/299 [00:04<00:05, 31.33it/s]     48%|####8     | 144/299 [00:04<00:04, 31.07it/s]     49%|####9     | 148/299 [00:04<00:05, 25.42it/s]     51%|#####     | 151/299 [00:04<00:05, 25.89it/s]     52%|#####1    | 154/299 [00:04<00:05, 25.90it/s]     53%|#####2    | 158/299 [00:04<00:05, 27.36it/s]     55%|#####4    | 163/299 [00:04<00:04, 29.65it/s]     56%|#####5    | 167/299 [00:05<00:04, 31.19it/s]     57%|#####7    | 171/299 [00:05<00:03, 32.64it/s]     59%|#####8    | 175/299 [00:05<00:03, 32.19it/s]     60%|#####9    | 179/299 [00:05<00:03, 30.31it/s]     61%|######1   | 183/299 [00:05<00:03, 32.00it/s]     63%|######2   | 188/299 [00:05<00:03, 35.52it/s]     64%|######4   | 192/299 [00:05<00:03, 33.94it/s]     66%|######5   | 196/299 [00:05<00:03, 32.74it/s]     67%|######7   | 201/299 [00:05<00:02, 35.04it/s]     69%|######8   | 206/299 [00:06<00:02, 36.77it/s]     71%|#######   | 211/299 [00:06<00:02, 39.28it/s]     72%|#######2  | 216/299 [00:06<00:02, 33.53it/s]     74%|#######3  | 220/299 [00:06<00:02, 29.85it/s]     75%|#######4  | 224/299 [00:06<00:02, 31.94it/s]     76%|#######6  | 228/299 [00:06<00:02, 31.21it/s]     78%|#######7  | 232/299 [00:07<00:02, 28.19it/s]     79%|#######8  | 236/299 [00:07<00:02, 29.33it/s]     80%|########  | 240/299 [00:07<00:02, 24.47it/s]     81%|########1 | 243/299 [00:07<00:02, 22.83it/s]     83%|########2 | 248/299 [00:07<00:02, 24.41it/s]     84%|########3 | 251/299 [00:07<00:02, 23.02it/s]     86%|########5 | 256/299 [00:07<00:01, 26.29it/s]     87%|########7 | 261/299 [00:08<00:01, 28.93it/s]     89%|########8 | 265/299 [00:08<00:01, 31.41it/s]     90%|######### | 270/299 [00:08<00:00, 33.16it/s]     92%|#########1| 274/299 [00:08<00:00, 34.31it/s]     93%|#########3| 279/299 [00:08<00:00, 36.32it/s]     95%|#########5| 285/299 [00:08<00:00, 39.20it/s]     97%|#########7| 291/299 [00:08<00:00, 42.83it/s]     99%|#########8| 296/299 [00:08<00:00, 37.92it/s]    100%|##########| 299/299 [00:09<00:00, 33.16it/s]
    Best alignment with the photodiode shifted 12 ms relative to the first behavior event
    errors: min -42, q1 -8, med -1, q3 9, max 75
    Excluding events that have zero close events or more than one photodiode event within `max_len` time
    Excluding event 27, no event found
    Excluding event 37, off by 35 ms
    Excluding event 115, off by -34 ms
    Excluding event 116, off by 32 ms
    Excluding event 143, off by -31 ms
    Excluding event 153, off by -40 ms
    Excluding event 154, off by 40 ms
    Excluding event 167, off by -42 ms
    Excluding event 235, no event found
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:331: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:338: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()




Find cessations of the photodiode deflections

Another piece of information in the photodiode channel is the cessation of
the events. Let's find those and add them to the events.


.. code-block:: default


    pd_parser.add_pd_off_event(fname, off_event_name='Stim Off')





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kzljuy96/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kzljuy96/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...




Check recovered event lengths and compare to the simulation ground truth

Let's load in the on and off events and plot their difference compared to
the ``n_secs_on`` event lengths we used to simulate.
The plot below show the differences between the simulated and recovered
deflection lengths. They completely overlap except where the photodiode was
corrupted, so it's a bit hard to see


.. code-block:: default


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



.. image:: /auto_examples/images/sphx_glr_plot_find_pd_on_and_off_003.png
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Used Annotations descriptions: ['Stim Off', 'Stim On']

    <matplotlib.legend.Legend object at 0x7fe2949e6c90>




.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  17.672 seconds)


.. _sphx_glr_download_auto_examples_plot_find_pd_on_and_off.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: plot_find_pd_on_and_off.py <plot_find_pd_on_and_off.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: plot_find_pd_on_and_off.ipynb <plot_find_pd_on_and_off.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
