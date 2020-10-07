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
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_0w1yc41c/sub-1_task-mytask_raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_0w1yc41c/sub-1_task-mytask_raw.fif [done]




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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_0w1yc41c/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_0w1yc41c/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    Finding photodiode events
      0%|          | 0/16341 [00:00<?, ?it/s]      1%|          | 162/16341 [00:00<00:10, 1494.11it/s]      2%|1         | 295/16341 [00:00<00:11, 1439.04it/s]      2%|2         | 367/16341 [00:00<00:17, 897.43it/s]       3%|2         | 459/16341 [00:00<00:17, 900.76it/s]      3%|3         | 532/16341 [00:00<00:22, 696.03it/s]      4%|3         | 600/16341 [00:00<00:22, 691.04it/s]      4%|4         | 714/16341 [00:00<00:20, 760.26it/s]      5%|4         | 797/16341 [00:00<00:19, 777.53it/s]      5%|5         | 887/16341 [00:01<00:19, 810.49it/s]      6%|6         | 1026/16341 [00:01<00:16, 923.82it/s]      7%|6         | 1133/16341 [00:01<00:15, 960.88it/s]      8%|7         | 1234/16341 [00:01<00:17, 856.53it/s]      9%|8         | 1467/16341 [00:01<00:14, 1057.00it/s]     10%|#         | 1674/16341 [00:01<00:11, 1238.69it/s]     12%|#1        | 1903/16341 [00:01<00:10, 1436.12it/s]     13%|#3        | 2127/16341 [00:01<00:08, 1608.97it/s]     15%|#4        | 2386/16341 [00:01<00:07, 1814.65it/s]     16%|#6        | 2633/16341 [00:01<00:06, 1971.55it/s]     17%|#7        | 2856/16341 [00:02<00:06, 2007.43it/s]     19%|#9        | 3117/16341 [00:02<00:06, 2156.18it/s]     20%|##        | 3349/16341 [00:02<00:06, 2101.97it/s]     22%|##2       | 3617/16341 [00:02<00:05, 2245.22it/s]     24%|##3       | 3853/16341 [00:02<00:05, 2125.28it/s]     25%|##4       | 4075/16341 [00:02<00:05, 2137.49it/s]     26%|##6       | 4299/16341 [00:02<00:05, 2165.31it/s]     28%|##7       | 4520/16341 [00:02<00:05, 2175.56it/s]     29%|##9       | 4775/16341 [00:02<00:05, 2274.63it/s]     31%|###       | 5057/16341 [00:03<00:04, 2413.49it/s]     32%|###2      | 5308/16341 [00:03<00:04, 2437.08it/s]     34%|###4      | 5569/16341 [00:03<00:04, 2479.88it/s]     36%|###5      | 5831/16341 [00:03<00:04, 2519.92it/s]     37%|###7      | 6085/16341 [00:03<00:04, 2384.18it/s]     39%|###8      | 6327/16341 [00:03<00:04, 2220.74it/s]     40%|####      | 6558/16341 [00:03<00:04, 2246.39it/s]     42%|####1     | 6816/16341 [00:03<00:04, 2336.84it/s]     43%|####3     | 7053/16341 [00:03<00:04, 2308.82it/s]     45%|####4     | 7344/16341 [00:03<00:03, 2460.54it/s]     47%|####6     | 7638/16341 [00:04<00:03, 2585.20it/s]     49%|####8     | 7926/16341 [00:04<00:03, 2666.09it/s]     50%|#####     | 8219/16341 [00:04<00:02, 2738.52it/s]     52%|#####1    | 8497/16341 [00:04<00:03, 2572.85it/s]     54%|#####3    | 8760/16341 [00:04<00:02, 2588.40it/s]     55%|#####5    | 9022/16341 [00:04<00:03, 2374.28it/s]     57%|#####6    | 9269/16341 [00:04<00:02, 2399.17it/s]     58%|#####8    | 9533/16341 [00:04<00:02, 2466.49it/s]     60%|######    | 9820/16341 [00:04<00:02, 2572.51it/s]     62%|######1   | 10081/16341 [00:05<00:02, 2512.50it/s]     63%|######3   | 10376/16341 [00:05<00:02, 2629.42it/s]     65%|######5   | 10643/16341 [00:05<00:02, 2429.10it/s]     67%|######6   | 10892/16341 [00:05<00:02, 2433.46it/s]     68%|######8   | 11140/16341 [00:05<00:02, 2184.34it/s]     70%|######9   | 11398/16341 [00:05<00:02, 2263.46it/s]     71%|#######1  | 11631/16341 [00:05<00:02, 2215.94it/s]     73%|#######2  | 11874/16341 [00:05<00:01, 2275.64it/s]     74%|#######4  | 12131/16341 [00:05<00:01, 2356.31it/s]     76%|#######5  | 12370/16341 [00:06<00:01, 2353.94it/s]     77%|#######7  | 12608/16341 [00:06<00:01, 2322.44it/s]     79%|#######8  | 12842/16341 [00:06<00:01, 2286.14it/s]     80%|########  | 13150/16341 [00:06<00:01, 2477.65it/s]     82%|########2 | 13424/16341 [00:06<00:01, 2550.91it/s]     84%|########3 | 13721/16341 [00:06<00:00, 2663.16it/s]     86%|########5 | 14024/16341 [00:06<00:00, 2762.47it/s]     88%|########7 | 14305/16341 [00:06<00:00, 2651.57it/s]     89%|########9 | 14574/16341 [00:06<00:00, 2510.15it/s]     91%|######### | 14830/16341 [00:07<00:00, 2329.45it/s]     92%|#########2| 15070/16341 [00:07<00:00, 2347.62it/s]     94%|#########3| 15309/16341 [00:07<00:00, 2332.23it/s]     95%|#########5| 15573/16341 [00:07<00:00, 2415.01it/s]     97%|#########7| 15852/16341 [00:07<00:00, 2515.83it/s]     99%|#########8| 16110/16341 [00:07<00:00, 2533.63it/s]    100%|##########| 16341/16341 [00:07<00:00, 2147.49it/s]
    300 up-deflection photodiode candidate events found
    Checking best behavior-photodiode difference alignments
      0%|          | 0/299 [00:00<?, ?it/s]      1%|1         | 3/299 [00:00<00:13, 21.57it/s]      3%|2         | 8/299 [00:00<00:11, 25.86it/s]      4%|3         | 11/299 [00:00<00:10, 26.71it/s]      5%|4         | 14/299 [00:00<00:11, 24.25it/s]      6%|6         | 18/299 [00:00<00:10, 26.94it/s]      7%|7         | 22/299 [00:00<00:09, 28.65it/s]      9%|8         | 26/299 [00:00<00:09, 27.90it/s]     10%|#         | 30/299 [00:01<00:09, 28.39it/s]     11%|#1        | 33/299 [00:01<00:09, 27.30it/s]     12%|#2        | 37/299 [00:01<00:09, 26.70it/s]     13%|#3        | 40/299 [00:01<00:09, 25.98it/s]     14%|#4        | 43/299 [00:01<00:12, 21.18it/s]     16%|#5        | 47/299 [00:01<00:10, 23.00it/s]     17%|#6        | 50/299 [00:01<00:11, 21.86it/s]     18%|#7        | 53/299 [00:02<00:10, 22.99it/s]     19%|#8        | 56/299 [00:02<00:11, 21.07it/s]     20%|#9        | 59/299 [00:02<00:10, 22.39it/s]     21%|##        | 62/299 [00:02<00:11, 19.91it/s]     22%|##1       | 65/299 [00:02<00:11, 19.96it/s]     23%|##2       | 68/299 [00:02<00:12, 18.93it/s]     24%|##3       | 71/299 [00:02<00:11, 19.02it/s]     24%|##4       | 73/299 [00:03<00:12, 18.68it/s]     25%|##5       | 75/299 [00:03<00:11, 18.72it/s]     26%|##6       | 78/299 [00:03<00:11, 19.28it/s]     27%|##7       | 81/299 [00:03<00:10, 19.91it/s]     28%|##8       | 84/299 [00:03<00:10, 20.30it/s]     29%|##9       | 87/299 [00:03<00:10, 20.16it/s]     30%|###       | 90/299 [00:03<00:10, 20.80it/s]     31%|###1      | 93/299 [00:04<00:09, 20.94it/s]     32%|###2      | 96/299 [00:04<00:09, 20.35it/s]     33%|###3      | 99/299 [00:04<00:10, 19.23it/s]     34%|###4      | 102/299 [00:04<00:09, 20.88it/s]     35%|###5      | 105/299 [00:04<00:09, 21.50it/s]     36%|###6      | 108/299 [00:04<00:10, 17.95it/s]     37%|###6      | 110/299 [00:05<00:13, 13.91it/s]     37%|###7      | 112/299 [00:05<00:12, 14.89it/s]     38%|###8      | 115/299 [00:05<00:10, 17.46it/s]     39%|###9      | 118/299 [00:05<00:09, 18.93it/s]     40%|####      | 121/299 [00:05<00:11, 16.10it/s]     41%|####1     | 124/299 [00:05<00:09, 18.02it/s]     42%|####2     | 127/299 [00:05<00:09, 18.05it/s]     43%|####3     | 129/299 [00:06<00:09, 17.05it/s]     44%|####3     | 131/299 [00:06<00:11, 15.23it/s]     45%|####4     | 134/299 [00:06<00:09, 16.57it/s]     45%|####5     | 136/299 [00:06<00:09, 17.04it/s]     46%|####6     | 139/299 [00:06<00:09, 17.23it/s]     47%|####7     | 141/299 [00:06<00:09, 16.51it/s]     48%|####7     | 143/299 [00:07<00:11, 13.39it/s]     48%|####8     | 145/299 [00:07<00:11, 13.77it/s]     50%|####9     | 149/299 [00:07<00:09, 16.48it/s]     51%|#####     | 152/299 [00:07<00:08, 18.17it/s]     52%|#####1    | 155/299 [00:07<00:07, 18.76it/s]     53%|#####2    | 158/299 [00:07<00:07, 19.11it/s]     54%|#####3    | 161/299 [00:07<00:07, 19.66it/s]     55%|#####4    | 164/299 [00:07<00:06, 21.47it/s]     56%|#####5    | 167/299 [00:08<00:06, 19.25it/s]     57%|#####6    | 170/299 [00:08<00:06, 21.39it/s]     58%|#####7    | 173/299 [00:08<00:06, 19.49it/s]     59%|#####8    | 176/299 [00:08<00:07, 16.81it/s]     60%|#####9    | 178/299 [00:08<00:07, 15.79it/s]     60%|######    | 180/299 [00:08<00:07, 16.74it/s]     61%|######1   | 183/299 [00:09<00:06, 18.48it/s]     62%|######2   | 186/299 [00:09<00:05, 20.45it/s]     63%|######3   | 189/299 [00:09<00:04, 22.59it/s]     64%|######4   | 192/299 [00:09<00:04, 21.66it/s]     65%|######5   | 195/299 [00:09<00:05, 20.27it/s]     67%|######6   | 199/299 [00:09<00:04, 22.07it/s]     68%|######7   | 202/299 [00:09<00:04, 21.32it/s]     69%|######8   | 205/299 [00:10<00:04, 22.04it/s]     70%|######9   | 208/299 [00:10<00:03, 23.91it/s]     71%|#######   | 212/299 [00:10<00:03, 24.11it/s]     72%|#######1  | 215/299 [00:10<00:04, 20.94it/s]     73%|#######2  | 218/299 [00:10<00:04, 19.65it/s]     74%|#######3  | 221/299 [00:10<00:03, 19.73it/s]     75%|#######4  | 224/299 [00:10<00:03, 21.86it/s]     76%|#######5  | 227/299 [00:11<00:03, 22.76it/s]     77%|#######6  | 230/299 [00:11<00:03, 20.77it/s]     78%|#######8  | 234/299 [00:11<00:02, 23.36it/s]     79%|#######9  | 237/299 [00:11<00:02, 22.33it/s]     80%|########  | 240/299 [00:11<00:02, 23.97it/s]     81%|########1 | 243/299 [00:11<00:02, 21.56it/s]     82%|########2 | 246/299 [00:11<00:02, 22.34it/s]     83%|########3 | 249/299 [00:11<00:02, 23.06it/s]     84%|########4 | 252/299 [00:12<00:02, 22.11it/s]     86%|########5 | 256/299 [00:12<00:01, 24.35it/s]     87%|########6 | 259/299 [00:12<00:01, 25.38it/s]     88%|########7 | 262/299 [00:12<00:01, 23.03it/s]     89%|########8 | 265/299 [00:12<00:01, 23.55it/s]     90%|########9 | 268/299 [00:12<00:01, 23.59it/s]     91%|######### | 272/299 [00:12<00:01, 25.78it/s]     92%|#########1| 275/299 [00:12<00:00, 25.89it/s]     93%|#########2| 278/299 [00:13<00:00, 24.51it/s]     94%|#########3| 281/299 [00:13<00:00, 25.18it/s]     95%|#########4| 284/299 [00:13<00:00, 25.75it/s]     96%|#########6| 288/299 [00:13<00:00, 28.03it/s]     97%|#########7| 291/299 [00:13<00:00, 28.02it/s]     99%|#########8| 295/299 [00:13<00:00, 30.75it/s]    100%|##########| 299/299 [00:13<00:00, 30.18it/s]    100%|##########| 299/299 [00:13<00:00, 21.65it/s]
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


    pd_parser.add_pd_off_events(fname, off_event_name='Stim Off')





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_0w1yc41c/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_0w1yc41c/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...




Check recovered event lengths and compare to the simulation ground truth

Let's load in the on and off events and plot their difference compared to
the ``n_secs_on`` event lengths we used to simulate.
The plot below show the differences between the simulated and recovered
deflection lengths. They completely overlap except where the photodiode was
corrupted, so it's a bit hard to see the two different lines.


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

    <matplotlib.legend.Legend object at 0x7ff984a30110>




.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  33.494 seconds)


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
