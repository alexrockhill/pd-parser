.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_plot_find_pd_events.py>`     to download the full example code
    .. rst-class:: sphx-glr-example-title

    .. _sphx_glr_auto_examples_plot_find_pd_events.py:


==========================
01. Find Photodiode Events
==========================
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

    After running this example, you can find the data here: /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl
    Creating RawArray with float64 data, n_channels=1, n_times=2044106
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Creating RawArray with float64 data, n_channels=3, n_times=2044106
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif [done]




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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:548: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    Finding photodiode events
      0%|          | 0/10920 [00:00<?, ?it/s]      2%|1         | 204/10920 [00:00<00:05, 2039.02it/s]      4%|4         | 438/10920 [00:00<00:04, 2120.16it/s]      6%|5         | 633/10920 [00:00<00:05, 1932.90it/s]      7%|6         | 761/10920 [00:00<00:08, 1226.96it/s]      8%|8         | 921/10920 [00:00<00:07, 1305.84it/s]     10%|#         | 1146/10920 [00:00<00:06, 1493.33it/s]     12%|#2        | 1326/10920 [00:00<00:06, 1572.68it/s]     14%|#3        | 1491/10920 [00:00<00:05, 1593.64it/s]     15%|#5        | 1654/10920 [00:01<00:06, 1468.35it/s]     18%|#8        | 1975/10920 [00:01<00:05, 1751.96it/s]     21%|##1       | 2304/10920 [00:01<00:04, 2037.66it/s]     23%|##3       | 2548/10920 [00:01<00:03, 2143.31it/s]     26%|##5       | 2789/10920 [00:01<00:05, 1443.22it/s]     27%|##7       | 2983/10920 [00:01<00:05, 1427.82it/s]     29%|##9       | 3176/10920 [00:01<00:05, 1539.85it/s]     31%|###       | 3357/10920 [00:02<00:06, 1171.26it/s]     33%|###2      | 3597/10920 [00:02<00:05, 1383.73it/s]     36%|###5      | 3890/10920 [00:02<00:04, 1643.98it/s]     38%|###7      | 4102/10920 [00:02<00:04, 1644.08it/s]     39%|###9      | 4300/10920 [00:02<00:05, 1235.40it/s]     41%|####      | 4462/10920 [00:02<00:04, 1293.33it/s]     42%|####2     | 4624/10920 [00:02<00:04, 1375.97it/s]     44%|####3     | 4783/10920 [00:03<00:05, 1051.46it/s]     45%|####5     | 4915/10920 [00:03<00:05, 1010.35it/s]     47%|####6     | 5092/10920 [00:03<00:05, 1143.91it/s]     48%|####7     | 5226/10920 [00:03<00:04, 1149.49it/s]     49%|####9     | 5367/10920 [00:03<00:04, 1216.85it/s]     50%|#####     | 5500/10920 [00:03<00:04, 1199.62it/s]     52%|#####1    | 5628/10920 [00:03<00:04, 1136.54it/s]     53%|#####2    | 5748/10920 [00:03<00:04, 1117.24it/s]     54%|#####3    | 5864/10920 [00:04<00:04, 1090.39it/s]     56%|#####5    | 6068/10920 [00:04<00:03, 1258.72it/s]     57%|#####7    | 6233/10920 [00:04<00:03, 1353.71it/s]     59%|#####8    | 6432/10920 [00:04<00:02, 1496.95it/s]     60%|######    | 6594/10920 [00:04<00:02, 1493.53it/s]     62%|######1   | 6752/10920 [00:04<00:03, 1140.30it/s]     64%|######3   | 6978/10920 [00:04<00:02, 1338.85it/s]     66%|######5   | 7202/10920 [00:04<00:02, 1522.56it/s]     68%|######8   | 7432/10920 [00:05<00:02, 1693.85it/s]     70%|######9   | 7627/10920 [00:05<00:02, 1217.16it/s]     71%|#######1  | 7786/10920 [00:05<00:03, 977.11it/s]      72%|#######2  | 7917/10920 [00:05<00:03, 778.31it/s]     73%|#######3  | 8025/10920 [00:05<00:03, 786.30it/s]     74%|#######4  | 8125/10920 [00:06<00:03, 745.26it/s]     75%|#######5  | 8223/10920 [00:06<00:03, 791.75it/s]     76%|#######6  | 8314/10920 [00:06<00:03, 782.50it/s]     77%|#######6  | 8401/10920 [00:06<00:03, 761.50it/s]     78%|#######8  | 8525/10920 [00:06<00:02, 860.80it/s]     79%|#######8  | 8620/10920 [00:06<00:02, 846.19it/s]     80%|########  | 8774/10920 [00:06<00:02, 978.24it/s]     82%|########2 | 8982/10920 [00:06<00:01, 1162.86it/s]     84%|########4 | 9206/10920 [00:06<00:01, 1357.60it/s]     86%|########6 | 9419/10920 [00:07<00:00, 1515.82it/s]     88%|########8 | 9614/10920 [00:07<00:00, 1623.67it/s]     91%|######### | 9908/10920 [00:07<00:00, 1875.50it/s]     93%|#########2| 10124/10920 [00:07<00:00, 1350.32it/s]     94%|#########4| 10300/10920 [00:07<00:00, 1092.82it/s]     96%|#########5| 10446/10920 [00:07<00:00, 994.01it/s]      97%|#########6| 10577/10920 [00:07<00:00, 1068.75it/s]     98%|#########8| 10705/10920 [00:08<00:00, 940.04it/s]      99%|#########9| 10853/10920 [00:08<00:00, 1055.12it/s]    100%|##########| 10920/10920 [00:08<00:00, 1308.67it/s]
    298 up-deflection photodiode candidate events found
    Checking best behavior-photodiode difference alignments
      0%|          | 0/299 [00:00<?, ?it/s]      1%|1         | 3/299 [00:00<00:13, 21.89it/s]      1%|1         | 4/299 [00:00<00:20, 14.23it/s]      2%|2         | 6/299 [00:00<00:19, 15.21it/s]      3%|2         | 8/299 [00:00<00:20, 13.92it/s]      3%|3         | 10/299 [00:00<00:24, 11.58it/s]      4%|3         | 11/299 [00:00<00:30,  9.40it/s]      4%|4         | 12/299 [00:01<00:32,  8.85it/s]      5%|4         | 14/299 [00:01<00:28, 10.08it/s]      6%|5         | 17/299 [00:01<00:22, 12.31it/s]      7%|6         | 20/299 [00:01<00:19, 14.24it/s]      7%|7         | 22/299 [00:01<00:18, 14.88it/s]      8%|8         | 24/299 [00:01<00:17, 15.82it/s]      9%|8         | 26/299 [00:01<00:22, 11.90it/s]     10%|9         | 29/299 [00:02<00:19, 13.70it/s]     11%|#1        | 33/299 [00:02<00:16, 15.83it/s]     12%|#1        | 35/299 [00:02<00:30,  8.63it/s]     12%|#2        | 37/299 [00:02<00:27,  9.67it/s]     13%|#3        | 40/299 [00:03<00:22, 11.60it/s]     14%|#4        | 42/299 [00:03<00:19, 12.99it/s]     15%|#4        | 44/299 [00:03<00:20, 12.25it/s]     16%|#5        | 47/299 [00:03<00:17, 14.25it/s]     16%|#6        | 49/299 [00:03<00:19, 12.52it/s]     17%|#7        | 52/299 [00:03<00:22, 10.99it/s]     18%|#8        | 54/299 [00:04<00:26,  9.18it/s]     19%|#8        | 56/299 [00:04<00:26,  9.34it/s]     19%|#9        | 58/299 [00:04<00:26,  9.09it/s]     20%|##        | 60/299 [00:05<00:29,  8.22it/s]     21%|##1       | 63/299 [00:05<00:24,  9.73it/s]     22%|##1       | 65/299 [00:05<00:22, 10.31it/s]     23%|##2       | 68/299 [00:05<00:21, 10.90it/s]     23%|##3       | 70/299 [00:05<00:18, 12.56it/s]     24%|##4       | 72/299 [00:05<00:18, 11.96it/s]     25%|##4       | 74/299 [00:06<00:22, 10.03it/s]     26%|##5       | 77/299 [00:06<00:18, 11.98it/s]     26%|##6       | 79/299 [00:06<00:16, 13.45it/s]     27%|##7       | 82/299 [00:06<00:13, 15.54it/s]     28%|##8       | 84/299 [00:06<00:14, 14.48it/s]     29%|##8       | 86/299 [00:06<00:18, 11.52it/s]     29%|##9       | 88/299 [00:07<00:19, 10.97it/s]     30%|###       | 91/299 [00:07<00:16, 12.90it/s]     31%|###1      | 93/299 [00:07<00:16, 12.50it/s]     32%|###2      | 96/299 [00:07<00:13, 14.55it/s]     33%|###2      | 98/299 [00:07<00:13, 15.36it/s]     33%|###3      | 100/299 [00:07<00:12, 16.20it/s]     34%|###4      | 103/299 [00:07<00:11, 16.96it/s]     35%|###5      | 105/299 [00:08<00:17, 10.81it/s]     36%|###5      | 107/299 [00:08<00:17, 10.83it/s]     37%|###6      | 110/299 [00:08<00:16, 11.15it/s]     37%|###7      | 112/299 [00:08<00:15, 12.06it/s]     38%|###8      | 114/299 [00:09<00:14, 12.98it/s]     39%|###9      | 117/299 [00:09<00:12, 14.62it/s]     40%|###9      | 119/299 [00:09<00:11, 15.24it/s]     40%|####      | 121/299 [00:09<00:12, 13.87it/s]     41%|####1     | 123/299 [00:09<00:13, 12.59it/s]     42%|####1     | 125/299 [00:09<00:13, 12.94it/s]     42%|####2     | 127/299 [00:09<00:12, 13.92it/s]     43%|####3     | 130/299 [00:10<00:10, 16.46it/s]     44%|####4     | 133/299 [00:10<00:08, 18.65it/s]     45%|####5     | 136/299 [00:10<00:07, 20.46it/s]     46%|####6     | 139/299 [00:10<00:14, 11.00it/s]     47%|####7     | 141/299 [00:11<00:21,  7.49it/s]     48%|####7     | 143/299 [00:11<00:18,  8.60it/s]     48%|####8     | 145/299 [00:11<00:17,  8.66it/s]     49%|####9     | 148/299 [00:11<00:14, 10.25it/s]     50%|#####     | 150/299 [00:11<00:14, 10.54it/s]     51%|#####1    | 153/299 [00:12<00:11, 12.57it/s]     52%|#####1    | 155/299 [00:12<00:10, 13.91it/s]     53%|#####2    | 157/299 [00:12<00:09, 14.99it/s]     54%|#####3    | 160/299 [00:12<00:08, 15.99it/s]     54%|#####4    | 162/299 [00:12<00:09, 15.19it/s]     55%|#####4    | 164/299 [00:12<00:12, 10.65it/s]     56%|#####5    | 166/299 [00:13<00:12, 10.93it/s]     56%|#####6    | 168/299 [00:13<00:12, 10.74it/s]     57%|#####6    | 170/299 [00:13<00:13,  9.73it/s]     58%|#####7    | 172/299 [00:13<00:13,  9.43it/s]     58%|#####8    | 174/299 [00:13<00:11, 10.50it/s]     59%|#####8    | 176/299 [00:14<00:13,  9.02it/s]     60%|#####9    | 178/299 [00:14<00:14,  8.33it/s]     61%|######    | 181/299 [00:14<00:11, 10.22it/s]     61%|######1   | 183/299 [00:14<00:12,  9.16it/s]     62%|######1   | 185/299 [00:15<00:11,  9.64it/s]     63%|######2   | 187/299 [00:15<00:13,  8.53it/s]     63%|######2   | 188/299 [00:15<00:15,  7.22it/s]     64%|######3   | 190/299 [00:15<00:14,  7.69it/s]     64%|######3   | 191/299 [00:16<00:17,  6.07it/s]     64%|######4   | 192/299 [00:16<00:18,  5.82it/s]     65%|######4   | 193/299 [00:16<00:17,  6.08it/s]     65%|######4   | 194/299 [00:16<00:16,  6.45it/s]     65%|######5   | 195/299 [00:16<00:15,  6.52it/s]     66%|######5   | 196/299 [00:16<00:15,  6.61it/s]     66%|######6   | 198/299 [00:16<00:12,  8.18it/s]     67%|######6   | 200/299 [00:17<00:11,  8.46it/s]     68%|######7   | 202/299 [00:17<00:10,  9.05it/s]     68%|######8   | 204/299 [00:17<00:09, 10.34it/s]     69%|######8   | 206/299 [00:17<00:08, 11.47it/s]     70%|######9   | 209/299 [00:17<00:07, 11.83it/s]     71%|#######   | 212/299 [00:17<00:06, 13.40it/s]     72%|#######1  | 215/299 [00:18<00:05, 15.35it/s]     73%|#######2  | 217/299 [00:18<00:06, 13.30it/s]     74%|#######3  | 220/299 [00:18<00:05, 14.44it/s]     74%|#######4  | 222/299 [00:18<00:06, 11.78it/s]     75%|#######4  | 224/299 [00:18<00:06, 11.56it/s]     76%|#######5  | 226/299 [00:19<00:05, 12.96it/s]     77%|#######6  | 229/299 [00:19<00:04, 15.03it/s]     77%|#######7  | 231/299 [00:19<00:05, 13.04it/s]     78%|#######7  | 233/299 [00:19<00:04, 14.41it/s]     79%|#######8  | 235/299 [00:19<00:05, 12.69it/s]     79%|#######9  | 237/299 [00:19<00:04, 12.72it/s]     80%|#######9  | 239/299 [00:19<00:04, 13.76it/s]     81%|########  | 242/299 [00:20<00:03, 15.43it/s]     82%|########1 | 245/299 [00:20<00:03, 17.50it/s]     83%|########2 | 247/299 [00:20<00:03, 13.76it/s]     83%|########3 | 249/299 [00:20<00:03, 14.14it/s]     84%|########3 | 251/299 [00:20<00:03, 13.17it/s]     85%|########4 | 253/299 [00:20<00:03, 12.71it/s]     86%|########5 | 257/299 [00:21<00:02, 14.30it/s]     87%|########6 | 259/299 [00:21<00:02, 14.65it/s]     88%|########7 | 262/299 [00:21<00:02, 15.17it/s]     89%|########8 | 266/299 [00:21<00:01, 18.37it/s]     90%|########9 | 269/299 [00:21<00:01, 18.57it/s]     91%|######### | 272/299 [00:21<00:01, 20.15it/s]     92%|#########1| 275/299 [00:21<00:01, 19.46it/s]     93%|#########2| 278/299 [00:22<00:01, 20.86it/s]     94%|#########3| 281/299 [00:22<00:00, 22.83it/s]     95%|#########4| 284/299 [00:22<00:00, 22.30it/s]     96%|#########5| 287/299 [00:22<00:00, 19.94it/s]     97%|#########6| 290/299 [00:22<00:00, 18.48it/s]     98%|#########7| 292/299 [00:22<00:00, 17.08it/s]     98%|#########8| 294/299 [00:22<00:00, 17.61it/s]     99%|#########8| 296/299 [00:23<00:00, 14.23it/s]    100%|#########9| 298/299 [00:23<00:00, 15.47it/s]    100%|##########| 299/299 [00:23<00:00, 12.85it/s]
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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif...
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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Used Annotations descriptions: ['Fixation', 'Go Cue', 'Response']
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:896: RuntimeWarning: The unit for channel(s) pd has changed from V to NA.
      raw.set_channel_types({ch: 'stim' for ch in pd_channels
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Creating folder: /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/bids_dir/sub-1/ieeg

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/bids_dir/README'...

    References
    ----------
    Appelhoff, S., Sanderson, M., Brooks, T., Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Höchenberger, R., Welke, D., Brunner, C., Rockhill, A., Larson, E., Gramfort, A. and Jas, M. (2019). MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. Journal of Open Source Software 4: (1896). https://doi.org/10.21105/joss.01896

    Holdgraf, C., Appelhoff, S., Bickel, S., Bouchard, K., D'Ambrosio, S., David, O., … Hermes, D. (2019). iEEG-BIDS, extending the Brain Imaging Data Structure specification to human intracranial electrophysiology. Scientific Data, 6, 102. https://doi.org/10.1038/s41597-019-0105-7


    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/bids_dir/participants.tsv'...

    participant_id  age     sex     hand
    sub-1   n/a     n/a     n/a

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/bids_dir/participants.json'...

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

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/bids_dir/sub-1/ieeg/sub-1_task-mytask_events.tsv'...

    onset   duration        trial_type      value   sample
    12.27   0.0     Fixation        1       12270
    12.97   0.0     Go Cue  2       12970
    14.996  0.0     Response        3       14996
    18.299  0.0     Fixation        1       18299
    18.999  0.0     Go Cue  2       18999

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/bids_dir/dataset_description.json'...

    {
        "Name": " ",
        "BIDSVersion": "1.4.0",
        "DatasetType": "raw",
        "Authors": [
            "Please cite MNE-BIDS in your publication before removing this (citations in README)"
        ]
    }

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/bids_dir/sub-1/ieeg/sub-1_task-mytask_ieeg.json'...

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

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/bids_dir/sub-1/ieeg/sub-1_task-mytask_channels.tsv'...

    name    type    units   low_cutoff      high_cutoff     description     sampling_frequency      status  status_description
    pd      TRIG    n/a     0.0     500.0   Trigger 1000.0  good    n/a
    ch1     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch2     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    ch3     SEEG    V       0.0     500.0   StereoEEG       1000.0  good    n/a
    /Users/alexrockhill/software/mne-bids/mne_bids/write.py:1115: RuntimeWarning: Converting data files to BrainVision format
      warn('Converting data files to BrainVision format')

    Writing '/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/bids_dir/sub-1/sub-1_scans.tsv'...

    filename        acq_time
    ieeg/sub-1_task-mytask_ieeg.vhdr        n/a
    Wrote /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_eo5srhbl/bids_dir/sub-1/sub-1_scans.tsv entry with ieeg/sub-1_task-mytask_ieeg.vhdr.





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  43.053 seconds)


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
