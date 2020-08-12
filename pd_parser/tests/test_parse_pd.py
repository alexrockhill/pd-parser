# -*- coding: utf-8 -*-
"""Test the pd_parsing.

For each supported file format, implement a test.
"""
# Authors: Alex Rockhill <aprockhill@mailbox.org>
#
# License: BSD (3-clause)

import os.path as op
import numpy as np
from mne.utils import _TempDir

import pd_parser

basepath = op.join(op.dirname(pd_parser.__file__), 'tests', 'data')

pd_data = np.genfromtxt(op.join(basepath, 'pd_data.tsv'), delimiter='\t')
events = np.genfromtxt(op.join(basepath, 'events.tsv'), delimiter='\t')


def test_parse_pd():
    out_dir = _TempDir()
    print(out_dir)
