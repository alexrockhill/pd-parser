.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_auto_examples_plot_find_audio_events.py>`     to download the full example code
    .. rst-class:: sphx-glr-example-title

    .. _sphx_glr_auto_examples_plot_find_audio_events.py:


=============================
Use Audio to Align Video Data
=============================
In this example, we use ``pd-parser`` to find audio events using the same
algorithm for matching with time-stamps and rejecting misaligned
audio, but applied using correlation with a .wav file instead of detecting
photodiode events based on their square wave shape.


.. code-block:: default


    # Authors: Alex Rockhill <aprockhill@mailbox.org>
    #
    # License: BSD (3-clause)








Load in a video with audio:

In this example, we'll use audio and instead of aligning electrophysiology
data, we'll align a video. This example data is from a task where movements
are played on a monitor for the participant to mirror and the video recording
is synchronized by playing a pre-recorded clap. This clap sound, or a similar
sound, is recommended for synchronizing audio because the onset is clear and
allows good precision in synchronizing events.

Note that the commands that require ffmpeg are pre-computed and commented
out because ffmpeg must be installed to use them and it is not required by
``pd-parser``.


.. code-block:: default

    import os.path as op
    import numpy as np
    from scipy.io import wavfile
    # from subprocess import run, PIPE, STDOUT
    # import datetime

    import mne
    from mne.utils import _TempDir

    import pd_parser
    from pd_parser.parse_pd import _load_data

    examples_dir = op.join(op.dirname(op.dirname(pd_parser.__file__)), 'examples')
    out_dir = _TempDir()

    # navigate to the example video
    video_fname = op.join(examples_dir, 'data', 'test_video.mp4')

    audio_fname = video_fname.replace('mp4', 'wav')  # pre-computed
    # extract audio (requires ffmpeg)
    # run(['ffmpeg', '-i', video_fname, audio_fname])

    fs, data = wavfile.read(audio_fname)
    data = data.mean(axis=1)  # stereo audio but only need one source
    info = mne.create_info(['audio'], fs, ['stim'])
    raw = mne.io.RawArray(data[np.newaxis], info)

    # save out data file
    fname = op.join(out_dir, 'test_video-raw.fif')
    raw.save(fname, overwrite=True)

    # find audio-visual time offset
    offset = 0  # pre-computed value for this video
    '''
    result = run(['ffprobe', '-show_entries', 'stream=codec_type,start_time',
                  '-v', '0', '-of', 'compact=p=1:nk=0', video_fname],
                 stdout=PIPE, stderr=STDOUT)
    output = result.stdout.decode('utf-8').split('\n')
    offset = float(output[0].strip('stream|codec_type=video|start_time')) - \
        float(output[1].strip('stream|codec_type=audio|start_time'))
    '''

    # navigate to corresponding behavior
    behf = op.join(examples_dir, 'data', 'test_video_beh.tsv')





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Creating RawArray with float64 data, n_channels=1, n_times=16464896
        Range : 0 ... 16464895 =      0.000 ...   343.019 secs
    Ready.
    Writing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_84p42qs4/test_video-raw.fif
    Closing /private/var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_84p42qs4/test_video-raw.fif [done]




Run the parser:

Now we'll call the main function to automatically parse the audio events.


.. code-block:: default

    pd_parser.parse_audio(fname, behf=behf, beh_col='tone_onset_time',
                          audio_ch_names=['audio'], zscore=10)




.. image:: /auto_examples/images/sphx_glr_plot_find_audio_events_001.png
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Reading in /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_84p42qs4/test_video-raw.fif
    Opening raw data file /var/folders/s4/y1vlkn8d70jfw7s8s03m9p540000gn/T/tmp_mne_tempdir_84p42qs4/test_video-raw.fif...
    Isotrak not found
        Range : 0 ... 16464895 =      0.000 ...   343.019 secs
    Ready.
    Reading 0 ... 16464895  =      0.000 ...   343.019 secs...
    Finding points where the audio is above `zscore` threshold...
    17 audio candidate events found
    Checking best alignments
      0%|          | 0/14 [00:00<?, ?it/s]     43%|####2     | 6/14 [00:00<00:00, 42.26it/s]     86%|########5 | 12/14 [00:00<00:00, 44.60it/s]    100%|##########| 14/14 [00:00<00:00, 50.35it/s]
    Best alignment with the events shifted 19 ms relative to the first behavior event
    errors: min -517, q1 -388, med -35, q3 246, max 485
    Excluding events that have zero close events or more than one photodiode event within `max_len` time
    /Users/alexrockhill/projects/pd-parser/pd_parser/parse_pd.py:443: UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
      fig.show()




Load the results:

Finally, we'll load the events and use them to crop the video although it
requires ffmpeg so it is commented out.


.. code-block:: default

    annot, _, beh_df = _load_data(fname)
    print('Here are the event times: ', annot.onset)

    # Crop the videos with ffmpeg
    '''
    for i in range(annot.onset.size):  # skip the first video
        action_time = (beh_df['tone_onset'][i] - beh_df['action_onset'][i]) / 1000
        run(['ffmpeg', '-i', f'{video_fname}', '-ss',
             str(datetime.timedelta(
                 seconds=annot.onset[i] - action_time - offset)),
             '-to', str(datetime.timedelta(seconds=annot.onset[i] - offset)),
             op.join(out_dir, 'movement-{}+action_type-{}.mp4'.format(
                 beh_df['movement'][i], beh_df['action_type'][i]))])
    '''




.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Here are the event times:  [ 19.05112457  39.9129982   61.88574982  83.54243469 104.41456604
     126.07720947 147.5539856  168.61270142 189.57843018 211.35673523
     250.20858765 271.68209839 292.14001465 313.30532837 333.78097534]

    "\nfor i in range(annot.onset.size):  # skip the first video\n    action_time = (beh_df['tone_onset'][i] - beh_df['action_onset'][i]) / 1000\n    run(['ffmpeg', '-i', f'{video_fname}', '-ss',\n         str(datetime.timedelta(\n             seconds=annot.onset[i] - action_time - offset)),\n         '-to', str(datetime.timedelta(seconds=annot.onset[i] - offset)),\n         op.join(out_dir, 'movement-{}+action_type-{}.mp4'.format(\n             beh_df['movement'][i], beh_df['action_type'][i]))])\n"




.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  3.722 seconds)


.. _sphx_glr_download_auto_examples_plot_find_audio_events.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: plot_find_audio_events.py <plot_find_audio_events.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: plot_find_audio_events.ipynb <plot_find_audio_events.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
