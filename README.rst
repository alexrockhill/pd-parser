pd-parser
---------
A tool to parse photodiode events from a possibly corrupted channel, compatible with BIDS formatting

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

Corrupted data may look like so:

.. image:: ./figs/exclude_event.png
   :width: 800

.. image:: ./figs/event_diffs.png
   :width: 400

Alex Rockhill
Eugene, OR 2020