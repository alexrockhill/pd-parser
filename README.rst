pd-parser
---------
A tool to parse photodiode events from a possibly corrupted channel, compatible with BIDS formatting.

Corrupted data may look like so:

.. image:: ./figs/exclude_event.png
   :width: 800

Which may lead to some excluded events and differences between the events and the expected timing based on the behavior that look like so:

.. image:: ./figs/event_diffs.png
   :width: 400

`pd-parser` takes an electrophysiology data file with one (common reference) or two (bipolar reference) channels that recorded photodiode events and matches that with time-stamped behavior stored in a tab-separated value (tsv) file. Candidate photodiode events are found based on having a square-wave shape, then these events are aligned to the behavior events (accounting for the timing of the photodiode drifting away from the behavior), and then events are excluded where the monitor hung up or the photodiode was different compared to the behavior for any reason. Events that are timed relative to the photodiode can then be added (this method might be a good idea as the large signal from the photodiode has been observed to affect neighboring channels on the amplifier). Finally, the data can be saved to BIDS format, copying over the raw data as is and unconverted (unless it's an unsupported file type by BIDS) and supplying the necessary support files to determine behavior, events and all the other necessary information to analyze the data.

Installation Instructions
-------------------------

1) Install the latest version python using of anaconda 
	- anaconda (https://www.anaconda.com/products/individual) *or* 
	- python (https://www.python.org/downloads/)

	and **make sure that you add the installed packages to the path**.

2) *Optional* Create virtual environment to keep the particular versions of software relevant to this project from getting changed. In a terminal, run
	- ``conda create --name myenv`` and then ``conda activate myenv`` *or* 
	- ``python -m venv /path/to/env/myenv`` and then ``source /path/to/env/myenv/bin/activate``

3) Run ``conda install pip`` in a terminal, and then ensure that when you run ``which pip`` in a terminal it points to the where the anaconda or python you just installed is.

4) Run ``pip install pd-parser`` in a terminal.


Getting Started
---------------

1) Plot the examples in a Jupyter notebook
    - In the 'Examples' page, click on 'Download all examples in Jupyter notebooks'
    - Unzip the downloaded file
    - Run ``pip install jupyter``
    - Point the terminal to the folder where the files you downloaded are by running ``cd /path/to/downloads/``
    - Run ``jupyter notebook`` in the terminal, this will pop up a webpage in your default browser.
    - Don't run the first cell or change ``%matplotlib inline`` to just ``%matplotlib`` to pop the plots out interactively instead of below the cell in the notebook.
    - Run each cell, change the parameters and explore the example.
2) Try pd-parser on your photodiode data. You will likely need to modify your behavior tsv files so that they have
	- One column corresponding to the expected event in seconds, called by default ``fix_onset_time``
	- *Optionally* Other columns with relative event times in seconds.


Alex Rockhill
Eugene, OR 2020