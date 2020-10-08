.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_plot_find_pd_on_and_off.py>`     to download the full example code
    .. rst-class:: sphx-glr-example-title

    .. _sphx_glr_auto_examples_plot_find_pd_on_and_off.py:


=====================================
02. Find Photodiode On and Off Events
=====================================
In this example, we use ``pd-parser`` to find photodiode events and
align both the onset of the deflection and the cessation to
to behavior.


.. code-block:: default


    # Authors: Alex Rockhill <aprockhill@mailbox.org>
    #
    # License: BSD (3-clause)








Simulate data and use it to make a raw object:

We'll make an `mne.io.Raw` object so that we can save out some random
data with a photodiode event channel in it in fif format (a commonly used
electrophysiology data format).


.. code-block:: default

    import os.path as op
    import numpy as np

    import mne
    from mne.utils import _TempDir

    import pd_parser
    from pd_parser.parse_pd import _to_tsv, _load_pd_data

    import matplotlib.pyplot as plt
    import matplotlib.cm as cm

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

    # save to disk as required by ``pd-parser``
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
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kohco_ka/sub-1_task-mytask_raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kohco_ka/sub-1_task-mytask_raw.fif [done]




Find the photodiode events relative to the behavioral timing of interest:

This function will use the default parameters to find and align the
photodiode events, excluding events that were off.
One percent of the 300 events (3) were corrupted as shown in the plots and
some were too far off from large offsets that we're going to exclude them.


.. code-block:: default


    pd_parser.parse_pd(fname, pd_event_name='Stim On', behf=behf,
                       pd_ch_names=['pd'], beh_col='time',
                       max_len=1.5)  # none are on longer than 1.5 seconds




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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kohco_ka/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kohco_ka/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    Finding photodiode events
      0%|          | 0/10920 [00:00<?, ?it/s]      1%|1         | 163/10920 [00:00<00:06, 1617.50it/s]      4%|3         | 397/10920 [00:00<00:05, 1758.77it/s]      5%|4         | 498/10920 [00:00<00:13, 797.46it/s]       5%|5         | 579/10920 [00:00<00:15, 657.67it/s]      6%|5         | 650/10920 [00:00<00:16, 633.02it/s]      7%|6         | 717/10920 [00:00<00:17, 583.59it/s]      9%|8         | 950/10920 [00:01<00:13, 752.76it/s]     10%|#         | 1126/10920 [00:01<00:10, 908.43it/s]     12%|#1        | 1258/10920 [00:01<00:11, 807.27it/s]     13%|#2        | 1370/10920 [00:01<00:11, 844.27it/s]     14%|#3        | 1524/10920 [00:01<00:09, 976.44it/s]     15%|#5        | 1646/10920 [00:01<00:08, 1037.01it/s]     16%|#6        | 1767/10920 [00:01<00:12, 734.36it/s]      18%|#7        | 1927/10920 [00:02<00:10, 876.38it/s]     19%|#8        | 2044/10920 [00:02<00:09, 894.69it/s]     20%|#9        | 2154/10920 [00:02<00:09, 933.44it/s]     21%|##        | 2262/10920 [00:02<00:12, 678.93it/s]     22%|##1       | 2350/10920 [00:02<00:12, 714.11it/s]     22%|##2       | 2436/10920 [00:02<00:16, 529.17it/s]     23%|##2       | 2507/10920 [00:03<00:19, 435.91it/s]     25%|##4       | 2688/10920 [00:03<00:14, 564.32it/s]     27%|##6       | 2923/10920 [00:03<00:10, 730.18it/s]     29%|##8       | 3129/10920 [00:03<00:08, 905.41it/s]     30%|###       | 3291/10920 [00:03<00:07, 1043.01it/s]     32%|###1      | 3450/10920 [00:03<00:06, 1072.88it/s]     33%|###3      | 3651/10920 [00:03<00:05, 1247.06it/s]     35%|###5      | 3864/10920 [00:03<00:04, 1423.76it/s]     37%|###7      | 4086/10920 [00:03<00:04, 1595.15it/s]     39%|###9      | 4290/10920 [00:04<00:03, 1704.05it/s]     41%|####1     | 4525/10920 [00:04<00:03, 1854.22it/s]     43%|####3     | 4731/10920 [00:04<00:03, 1871.84it/s]     45%|####5     | 4933/10920 [00:04<00:03, 1885.14it/s]     47%|####7     | 5135/10920 [00:04<00:03, 1923.50it/s]     49%|####8     | 5335/10920 [00:04<00:04, 1224.14it/s]     50%|#####     | 5495/10920 [00:05<00:05, 912.52it/s]      52%|#####1    | 5624/10920 [00:05<00:05, 912.93it/s]     53%|#####2    | 5742/10920 [00:05<00:05, 953.46it/s]     54%|#####3    | 5857/10920 [00:05<00:05, 871.86it/s]     55%|#####4    | 5959/10920 [00:05<00:05, 864.61it/s]     55%|#####5    | 6056/10920 [00:05<00:05, 861.17it/s]     56%|#####6    | 6150/10920 [00:05<00:05, 848.09it/s]     57%|#####7    | 6240/10920 [00:05<00:05, 855.60it/s]     58%|#####7    | 6330/10920 [00:06<00:06, 741.83it/s]     59%|#####8    | 6410/10920 [00:06<00:06, 653.71it/s]     60%|#####9    | 6517/10920 [00:06<00:05, 738.64it/s]     61%|######    | 6649/10920 [00:06<00:05, 850.50it/s]     62%|######2   | 6787/10920 [00:06<00:04, 960.54it/s]     63%|######3   | 6910/10920 [00:06<00:03, 1028.09it/s]     65%|######5   | 7152/10920 [00:06<00:03, 1242.16it/s]     68%|######7   | 7401/10920 [00:06<00:02, 1461.45it/s]     70%|#######   | 7671/10920 [00:06<00:01, 1693.77it/s]     72%|#######2  | 7879/10920 [00:07<00:01, 1740.90it/s]     74%|#######3  | 8080/10920 [00:07<00:01, 1525.12it/s]     76%|#######5  | 8257/10920 [00:07<00:02, 1097.04it/s]     77%|#######6  | 8401/10920 [00:07<00:02, 909.02it/s]      79%|#######8  | 8590/10920 [00:07<00:02, 1076.19it/s]     80%|########  | 8783/10920 [00:07<00:01, 1214.80it/s]     82%|########1 | 8934/10920 [00:08<00:02, 895.64it/s]      83%|########3 | 9093/10920 [00:08<00:01, 1030.06it/s]     84%|########4 | 9226/10920 [00:08<00:01, 943.02it/s]      86%|########5 | 9343/10920 [00:08<00:01, 996.13it/s]     87%|########6 | 9475/10920 [00:08<00:01, 1074.58it/s]     89%|########9 | 9726/10920 [00:08<00:00, 1297.01it/s]     91%|#########1| 9941/10920 [00:08<00:00, 1470.69it/s]     93%|#########3| 10209/10920 [00:08<00:00, 1700.09it/s]     96%|#########5| 10453/10920 [00:09<00:00, 1864.02it/s]     98%|#########7| 10668/10920 [00:09<00:00, 1418.09it/s]     99%|#########9| 10846/10920 [00:09<00:00, 1488.53it/s]    100%|##########| 10920/10920 [00:09<00:00, 1153.99it/s]
    297 up-deflection photodiode candidate events found
    Checking best behavior-photodiode difference alignments
      0%|          | 0/299 [00:00<?, ?it/s]      0%|          | 1/299 [00:00<00:59,  4.99it/s]      1%|1         | 3/299 [00:00<00:47,  6.25it/s]      1%|1         | 4/299 [00:00<00:45,  6.50it/s]      2%|2         | 6/299 [00:00<00:36,  8.02it/s]      3%|2         | 8/299 [00:00<00:30,  9.57it/s]      3%|3         | 10/299 [00:00<00:30,  9.63it/s]      4%|4         | 12/299 [00:01<00:29,  9.57it/s]      5%|4         | 14/299 [00:01<00:31,  8.92it/s]      6%|5         | 17/299 [00:01<00:25, 11.05it/s]      6%|6         | 19/299 [00:01<00:24, 11.38it/s]      7%|7         | 21/299 [00:01<00:26, 10.36it/s]      8%|7         | 23/299 [00:02<00:26, 10.33it/s]      9%|8         | 26/299 [00:02<00:21, 12.69it/s]      9%|9         | 28/299 [00:02<00:21, 12.37it/s]     10%|#         | 30/299 [00:02<00:23, 11.34it/s]     11%|#1        | 33/299 [00:02<00:20, 13.07it/s]     12%|#2        | 36/299 [00:02<00:16, 15.54it/s]     13%|#3        | 39/299 [00:02<00:15, 17.22it/s]     14%|#4        | 42/299 [00:03<00:15, 16.77it/s]     15%|#4        | 44/299 [00:03<00:16, 15.32it/s]     16%|#5        | 47/299 [00:03<00:16, 15.74it/s]     17%|#7        | 51/299 [00:03<00:13, 17.82it/s]     19%|#8        | 56/299 [00:03<00:11, 21.15it/s]     20%|#9        | 59/299 [00:03<00:12, 19.91it/s]     21%|##        | 62/299 [00:04<00:14, 16.59it/s]     22%|##1       | 65/299 [00:04<00:13, 16.73it/s]     22%|##2       | 67/299 [00:04<00:30,  7.71it/s]     23%|##3       | 69/299 [00:05<00:26,  8.66it/s]     24%|##3       | 71/299 [00:05<00:22, 10.30it/s]     24%|##4       | 73/299 [00:05<00:22, 10.17it/s]     25%|##5       | 75/299 [00:05<00:19, 11.57it/s]     26%|##5       | 77/299 [00:06<00:31,  7.06it/s]     26%|##6       | 79/299 [00:06<00:26,  8.42it/s]     27%|##7       | 81/299 [00:06<00:25,  8.59it/s]     28%|##7       | 83/299 [00:06<00:24,  8.86it/s]     28%|##8       | 85/299 [00:06<00:25,  8.54it/s]     29%|##9       | 88/299 [00:07<00:21,  9.88it/s]     30%|###       | 90/299 [00:07<00:24,  8.60it/s]     31%|###       | 92/299 [00:07<00:21,  9.57it/s]     31%|###1      | 94/299 [00:07<00:24,  8.46it/s]     32%|###1      | 95/299 [00:08<00:27,  7.45it/s]     32%|###2      | 97/299 [00:08<00:24,  8.40it/s]     33%|###2      | 98/299 [00:08<00:24,  8.36it/s]     33%|###3      | 100/299 [00:08<00:22,  8.91it/s]     34%|###4      | 103/299 [00:08<00:18, 10.72it/s]     35%|###5      | 105/299 [00:08<00:16, 11.90it/s]     36%|###5      | 107/299 [00:08<00:16, 11.37it/s]     36%|###6      | 109/299 [00:09<00:17, 11.13it/s]     37%|###7      | 111/299 [00:09<00:17, 10.96it/s]     38%|###8      | 115/299 [00:09<00:13, 13.20it/s]     39%|###9      | 117/299 [00:09<00:12, 14.42it/s]     40%|####      | 120/299 [00:09<00:12, 14.23it/s]     41%|####      | 122/299 [00:10<00:15, 11.30it/s]     42%|####1     | 125/299 [00:10<00:13, 13.29it/s]     42%|####2     | 127/299 [00:10<00:14, 12.20it/s]     43%|####3     | 129/299 [00:10<00:16, 10.10it/s]     44%|####3     | 131/299 [00:10<00:16, 10.36it/s]     44%|####4     | 133/299 [00:11<00:14, 11.76it/s]     45%|####5     | 135/299 [00:11<00:16,  9.90it/s]     46%|####5     | 137/299 [00:11<00:16, 10.10it/s]     46%|####6     | 139/299 [00:11<00:13, 11.71it/s]     47%|####7     | 141/299 [00:11<00:12, 12.84it/s]     48%|####8     | 144/299 [00:11<00:10, 15.00it/s]     49%|####8     | 146/299 [00:12<00:11, 13.18it/s]     49%|####9     | 148/299 [00:12<00:12, 11.96it/s]     50%|#####     | 150/299 [00:12<00:13, 11.03it/s]     51%|#####     | 152/299 [00:12<00:12, 11.60it/s]     52%|#####1    | 154/299 [00:12<00:11, 12.73it/s]     53%|#####2    | 157/299 [00:12<00:11, 12.36it/s]     53%|#####3    | 159/299 [00:13<00:10, 13.11it/s]     54%|#####3    | 161/299 [00:13<00:12, 11.00it/s]     55%|#####4    | 163/299 [00:13<00:11, 11.51it/s]     55%|#####5    | 165/299 [00:13<00:15,  8.83it/s]     56%|#####5    | 167/299 [00:14<00:15,  8.64it/s]     57%|#####6    | 169/299 [00:14<00:12, 10.04it/s]     57%|#####7    | 171/299 [00:14<00:13,  9.52it/s]     58%|#####7    | 173/299 [00:14<00:13,  9.68it/s]     59%|#####8    | 175/299 [00:14<00:14,  8.70it/s]     59%|#####9    | 177/299 [00:15<00:12,  9.54it/s]     60%|#####9    | 179/299 [00:15<00:12,  9.65it/s]     61%|######    | 181/299 [00:15<00:12,  9.59it/s]     61%|######1   | 183/299 [00:15<00:11, 10.41it/s]     62%|######1   | 185/299 [00:15<00:10, 10.39it/s]     63%|######3   | 189/299 [00:16<00:08, 12.72it/s]     64%|######3   | 191/299 [00:16<00:08, 13.20it/s]     65%|######4   | 193/299 [00:16<00:08, 11.81it/s]     65%|######5   | 195/299 [00:16<00:10, 10.09it/s]     66%|######6   | 198/299 [00:16<00:09, 11.13it/s]     67%|######6   | 200/299 [00:16<00:08, 11.87it/s]     68%|######7   | 203/299 [00:17<00:06, 13.80it/s]     69%|######9   | 207/299 [00:17<00:05, 16.31it/s]     71%|#######   | 212/299 [00:17<00:04, 19.75it/s]     72%|#######1  | 215/299 [00:17<00:05, 15.38it/s]     73%|#######2  | 218/299 [00:17<00:05, 15.72it/s]     74%|#######3  | 220/299 [00:17<00:04, 15.96it/s]     74%|#######4  | 222/299 [00:18<00:04, 15.54it/s]     75%|#######4  | 224/299 [00:18<00:05, 13.80it/s]     76%|#######5  | 226/299 [00:18<00:05, 13.09it/s]     76%|#######6  | 228/299 [00:18<00:05, 12.93it/s]     77%|#######6  | 230/299 [00:18<00:05, 12.51it/s]     78%|#######7  | 233/299 [00:18<00:04, 14.81it/s]     79%|#######8  | 235/299 [00:19<00:07,  8.61it/s]     79%|#######9  | 237/299 [00:19<00:07,  7.90it/s]     80%|#######9  | 239/299 [00:19<00:06,  9.64it/s]     81%|########  | 242/299 [00:19<00:04, 11.92it/s]     82%|########1 | 244/299 [00:20<00:04, 13.04it/s]     83%|########2 | 248/299 [00:20<00:03, 14.23it/s]     84%|########3 | 250/299 [00:20<00:03, 12.40it/s]     84%|########4 | 252/299 [00:20<00:03, 13.66it/s]     85%|########4 | 254/299 [00:20<00:03, 13.93it/s]     86%|########5 | 256/299 [00:20<00:03, 12.51it/s]     86%|########6 | 258/299 [00:21<00:03, 12.87it/s]     87%|########7 | 261/299 [00:21<00:02, 14.25it/s]     88%|########8 | 264/299 [00:21<00:02, 15.49it/s]     89%|########8 | 266/299 [00:21<00:03, 10.75it/s]     90%|######### | 270/299 [00:21<00:02, 11.26it/s]     91%|######### | 272/299 [00:22<00:02, 11.31it/s]     92%|#########1| 274/299 [00:22<00:01, 12.80it/s]     93%|#########2| 277/299 [00:22<00:01, 15.28it/s]     93%|#########3| 279/299 [00:22<00:01, 14.05it/s]     94%|#########3| 281/299 [00:22<00:01, 15.02it/s]     95%|#########4| 283/299 [00:22<00:01, 13.61it/s]     95%|#########5| 285/299 [00:22<00:01, 12.95it/s]     96%|#########5| 287/299 [00:23<00:00, 12.44it/s]     97%|#########6| 290/299 [00:23<00:00, 13.29it/s]     98%|#########7| 292/299 [00:23<00:00, 14.06it/s]     98%|#########8| 294/299 [00:23<00:00, 14.33it/s]     99%|#########8| 296/299 [00:23<00:00, 10.24it/s]    100%|#########9| 298/299 [00:24<00:00, 10.19it/s]    100%|##########| 299/299 [00:24<00:00, 12.37it/s]
    Best alignment with the photodiode shifted 12 ms relative to the first behavior event
    errors: min -42, q1 -8, med -1, q3 9, max 75
    Excluding events that have zero close events or more than one photodiode event within `max_len` time
    Excluding event 9, no event found
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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kohco_ka/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_kohco_ka/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...




Check recovered event lengths and compare to the simulation ground truth

Let's load in the on and off events and plot their difference compared to
the ``n_secs_on`` event lengths we used to simulate.
The plot below show the differences between the simulated
deflection event lengths on the x axis scattered against the
recovered event lengths on the y axis. The identity line (the line with 1:1
correspondance) is not shown as it would occlude the plotted data; the
the lengths are recovered within 1 millisecond. Note that the colors are
arbitrary and are only used to increase contrast and ease of visualization.


.. code-block:: default


    annot, pd_ch_names, beh_df = _load_pd_data(fname)
    raw.set_annotations(annot)
    events, event_id = mne.events_from_annotations(raw)
    on_events = events[events[:, 2] == event_id['Stim On']]
    off_events = events[events[:, 2] == event_id['Stim Off']]

    recovered = (off_events[:, 0] - on_events[:, 0]) / raw.info['sfreq']
    not_corrupted = [s != 'n/a' for s in beh_df['pd_sample']]
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



.. image:: /auto_examples/images/sphx_glr_plot_find_pd_on_and_off_003.png
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Used Annotations descriptions: ['Stim Off', 'Stim On']
    Mean difference in the recovered from simulated length is 0.254 milliseconds





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  46.997 seconds)


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
