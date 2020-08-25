pd-parser
---------
A tool to parse photodiode events from a possibly corrupted channel, compatible with BIDS formatting

Installation Instructions
-------------------------
1) Install the latest version of anaconda (https://www.anaconda.com/products/individual) or python (https://www.python.org/downloads/) and make sure that you add the installed packages to the path.

2) Run ``conda install pip`` in a terminal, and then ensure that when you run ``which pip`` in a terminal it points to the where the anaconda or python you just installed is.

3) Run ``pip install pd-parser`` in a terminal.

Corrupted data may look like so:

.. image:: ./figs/exclude_event.png
   :width: 800

.. image:: ./figs/event_diffs.png
   :width: 400

Alex Rockhill
Eugene, OR 2020