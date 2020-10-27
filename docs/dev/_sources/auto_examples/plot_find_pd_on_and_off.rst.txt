.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_plot_find_pd_on_and_off.py>`     to download the full example code
    .. rst-class:: sphx-glr-example-title

    .. _sphx_glr_auto_examples_plot_find_pd_on_and_off.py:


=================================
Find Photodiode On and Off Events
=================================
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
    from pd_parser.parse_pd import _to_tsv, _load_data

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
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_4igi_0_w/sub-1_task-mytask_raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_4igi_0_w/sub-1_task-mytask_raw.fif [done]




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

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_4igi_0_w/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_4igi_0_w/sub-1_task-mytask_raw.fif...
    Isotrak not found
        Range : 0 ... 2044105 =      0.000 ...  2044.105 secs
    Ready.
    Reading 0 ... 2044105  =      0.000 ...  2044.105 secs...
    Finding photodiode events
      0%|          | 0/10920 [00:00<?, ?it/s]      4%|3         | 412/10920 [00:00<00:02, 4116.55it/s]      8%|7         | 864/10920 [00:00<00:02, 4227.76it/s]     12%|#1        | 1280/10920 [00:00<00:02, 4204.46it/s]     16%|#5        | 1705/10920 [00:00<00:02, 4217.32it/s]     19%|#9        | 2119/10920 [00:00<00:02, 4191.88it/s]     23%|##3       | 2547/10920 [00:00<00:01, 4216.94it/s]     27%|##7       | 2994/10920 [00:00<00:01, 4287.64it/s]     31%|###1      | 3390/10920 [00:00<00:01, 4140.87it/s]     35%|###4      | 3782/10920 [00:00<00:01, 3658.51it/s]     38%|###7      | 4143/10920 [00:01<00:02, 2924.37it/s]     41%|####      | 4456/10920 [00:01<00:02, 2901.65it/s]     45%|####4     | 4874/10920 [00:01<00:01, 3193.10it/s]     48%|####8     | 5268/10920 [00:01<00:01, 3384.73it/s]     51%|#####1    | 5623/10920 [00:01<00:01, 2970.88it/s]     54%|#####4    | 5941/10920 [00:01<00:02, 1835.99it/s]     57%|#####6    | 6193/10920 [00:02<00:02, 1978.02it/s]     59%|#####8    | 6442/10920 [00:02<00:02, 1929.53it/s]     61%|######1   | 6671/10920 [00:02<00:04, 1048.29it/s]     63%|######2   | 6866/10920 [00:02<00:03, 1216.18it/s]     65%|######4   | 7047/10920 [00:02<00:02, 1335.07it/s]     66%|######6   | 7255/10920 [00:02<00:02, 1494.31it/s]     68%|######8   | 7443/10920 [00:03<00:03, 901.69it/s]      69%|######9   | 7589/10920 [00:03<00:05, 569.18it/s]     71%|#######   | 7700/10920 [00:04<00:06, 488.69it/s]     71%|#######1  | 7789/10920 [00:04<00:06, 486.23it/s]     72%|#######2  | 7866/10920 [00:04<00:06, 479.85it/s]     73%|#######2  | 7934/10920 [00:04<00:06, 454.42it/s]     73%|#######3  | 7994/10920 [00:04<00:07, 409.29it/s]     76%|#######5  | 8285/10920 [00:04<00:04, 551.43it/s]     79%|#######8  | 8576/10920 [00:04<00:03, 728.52it/s]     81%|########1 | 8871/10920 [00:05<00:02, 941.10it/s]     83%|########3 | 9081/10920 [00:05<00:01, 1026.84it/s]     86%|########5 | 9366/10920 [00:05<00:01, 1270.43it/s]     88%|########7 | 9599/10920 [00:05<00:00, 1469.96it/s]     90%|########9 | 9825/10920 [00:05<00:00, 1620.09it/s]     92%|#########1| 10044/10920 [00:05<00:00, 1329.52it/s]     94%|#########3| 10225/10920 [00:05<00:00, 1252.42it/s]     96%|#########5| 10453/10920 [00:06<00:00, 1447.46it/s]     98%|#########7| 10660/10920 [00:06<00:00, 1590.67it/s]    100%|#########9| 10895/10920 [00:06<00:00, 1760.87it/s]    100%|##########| 10920/10920 [00:06<00:00, 1720.77it/s]
    297 up-deflection photodiode candidate events found
    Checking best alignments
      0%|          | 0/299 [00:00<?, ?it/s]      0%|          | 1/299 [00:00<01:51,  2.66it/s]      1%|1         | 3/299 [00:00<01:23,  3.56it/s]      2%|2         | 6/299 [00:00<01:01,  4.80it/s]      3%|3         | 9/299 [00:00<00:45,  6.38it/s]      4%|3         | 11/299 [00:00<00:42,  6.77it/s]      4%|4         | 13/299 [00:01<00:42,  6.68it/s]      5%|5         | 15/299 [00:01<00:36,  7.79it/s]      6%|6         | 18/299 [00:01<00:29,  9.50it/s]      7%|7         | 21/299 [00:01<00:23, 11.66it/s]      9%|8         | 26/299 [00:01<00:18, 14.76it/s]     10%|#         | 31/299 [00:01<00:14, 18.40it/s]     12%|#2        | 36/299 [00:02<00:11, 22.26it/s]     13%|#3        | 40/299 [00:02<00:11, 23.12it/s]     15%|#4        | 44/299 [00:02<00:12, 21.12it/s]     16%|#5        | 47/299 [00:02<00:11, 22.86it/s]     17%|#6        | 50/299 [00:02<00:11, 21.69it/s]     18%|#8        | 54/299 [00:02<00:09, 24.80it/s]     20%|#9        | 59/299 [00:02<00:08, 28.00it/s]     21%|##1       | 63/299 [00:03<00:08, 29.10it/s]     22%|##2       | 67/299 [00:03<00:08, 26.10it/s]     23%|##3       | 70/299 [00:03<00:11, 19.79it/s]     24%|##4       | 73/299 [00:03<00:12, 17.98it/s]     25%|##5       | 76/299 [00:03<00:12, 17.72it/s]     26%|##6       | 79/299 [00:04<00:11, 19.16it/s]     27%|##7       | 82/299 [00:04<00:10, 20.76it/s]     29%|##8       | 86/299 [00:04<00:08, 23.84it/s]     30%|###       | 90/299 [00:04<00:07, 26.67it/s]     32%|###1      | 95/299 [00:04<00:07, 29.11it/s]     33%|###3      | 99/299 [00:04<00:06, 29.52it/s]     35%|###4      | 104/299 [00:04<00:06, 31.84it/s]     36%|###6      | 108/299 [00:04<00:06, 30.58it/s]     37%|###7      | 112/299 [00:05<00:06, 30.55it/s]     39%|###8      | 116/299 [00:05<00:05, 32.13it/s]     40%|####      | 120/299 [00:05<00:05, 32.06it/s]     41%|####1     | 124/299 [00:05<00:05, 33.31it/s]     43%|####2     | 128/299 [00:05<00:05, 30.32it/s]     44%|####4     | 132/299 [00:05<00:05, 32.56it/s]     45%|####5     | 136/299 [00:05<00:05, 31.27it/s]     47%|####6     | 140/299 [00:05<00:05, 31.70it/s]     48%|####8     | 144/299 [00:06<00:04, 31.63it/s]     50%|####9     | 149/299 [00:06<00:04, 34.14it/s]     51%|#####1    | 153/299 [00:06<00:04, 35.52it/s]     53%|#####2    | 157/299 [00:06<00:04, 33.64it/s]     54%|#####3    | 161/299 [00:06<00:04, 33.54it/s]     56%|#####5    | 166/299 [00:06<00:03, 36.03it/s]     57%|#####7    | 171/299 [00:06<00:03, 36.32it/s]     59%|#####8    | 175/299 [00:06<00:03, 34.78it/s]     60%|#####9    | 179/299 [00:06<00:03, 32.88it/s]     62%|######1   | 184/299 [00:07<00:03, 34.74it/s]     63%|######3   | 189/299 [00:07<00:02, 36.86it/s]     65%|######4   | 193/299 [00:07<00:02, 35.83it/s]     66%|######5   | 197/299 [00:07<00:02, 36.66it/s]     67%|######7   | 201/299 [00:07<00:02, 37.31it/s]     69%|######8   | 206/299 [00:07<00:02, 39.67it/s]     71%|#######   | 212/299 [00:07<00:02, 41.55it/s]     73%|#######2  | 217/299 [00:07<00:02, 37.66it/s]     74%|#######3  | 221/299 [00:08<00:02, 36.31it/s]     76%|#######5  | 227/299 [00:08<00:01, 39.59it/s]     78%|#######7  | 232/299 [00:08<00:01, 38.11it/s]     79%|#######9  | 237/299 [00:08<00:01, 38.03it/s]     81%|########  | 241/299 [00:08<00:01, 36.40it/s]     82%|########1 | 245/299 [00:08<00:01, 31.32it/s]     84%|########3 | 250/299 [00:08<00:01, 33.28it/s]     86%|########5 | 256/299 [00:09<00:01, 37.46it/s]     87%|########7 | 261/299 [00:09<00:00, 38.96it/s]     89%|########8 | 266/299 [00:09<00:00, 38.85it/s]     91%|######### | 272/299 [00:09<00:00, 41.91it/s]     93%|#########2| 277/299 [00:09<00:00, 42.35it/s]     94%|#########4| 282/299 [00:09<00:00, 41.82it/s]     97%|#########6| 290/299 [00:09<00:00, 45.25it/s]     99%|#########8| 295/299 [00:09<00:00, 42.81it/s]    100%|##########| 299/299 [00:10<00:00, 29.68it/s]
    Best alignment with the events shifted 12 ms relative to the first behavior event
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
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:436: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:443: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()




Find cessations of the photodiode deflections

Another piece of information in the photodiode channel is the cessation of
the events. Let's find those and add them to the events.


.. code-block:: default


    pd_parser.add_pd_off_events(fname, off_event_name='Stim Off')





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_4igi_0_w/sub-1_task-mytask_raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_4igi_0_w/sub-1_task-mytask_raw.fif...
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


    annot, pd_ch_names, beh_df = _load_data(fname)
    raw.set_annotations(annot)
    events, event_id = mne.events_from_annotations(raw)
    on_events = events[events[:, 2] == event_id['Stim On']]
    off_events = events[events[:, 2] == event_id['Stim Off']]

    recovered = (off_events[:, 0] - on_events[:, 0]) / raw.info['sfreq']
    not_corrupted = [s != 'n/a' for s in beh_df['pd_parser_sample']]
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

   **Total running time of the script:** ( 0 minutes  22.514 seconds)


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
