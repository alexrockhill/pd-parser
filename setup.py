#! /usr/bin/env python
"""Setup pd_parser."""
import os
from setuptools import setup, find_packages

# get the version
version = None
with open(os.path.join('pd_parser', '__init__.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('\'')
            break
if version is None:
    raise RuntimeError('Could not determine version')


descr = ('pd-parser: Take a potentially corrupted photodiode channel '
         'and find the event time samples at which it turned on.')

DISTNAME = 'pd-parser'
DESCRIPTION = descr
MAINTAINER = 'Alex Rockhill'
MAINTAINER_EMAIL = 'aprockhill@mailbox.org'
URL = 'https://github.com/alexrockhill/pd-parser/'
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = 'https://github.com/alexrockhill/pd-parser.git'
VERSION = version

if __name__ == "__main__":
    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          long_description=open('README.rst').read(),
          long_description_content_type='text/x-rst',
          python_requires='~=3.5',
          classifiers=[
              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',
              'License :: OSI Approved',
              'Programming Language :: Python',
              'Topic :: Software Development',
              'Topic :: Scientific/Engineering',
              'Operating System :: Microsoft :: Windows',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Operating System :: MacOS',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3.6',
              'Programming Language :: Python :: 3.7',
          ],
          platforms='any',
          packages=find_packages(),
          entry_points={'console_scripts': [
              'find_pd_params = pd_parser.commands.run:find_pd_params',
              'parse_pd = pd_parser.commands.run:parse_pd',
              'parse_audio = pd_parser.commands.run:parse_audio',
              'add_pd_off_events = pd_parser.commands.run:add_pd_off_events',
              'add_relative_events = '
              'pd_parser.commands.run:add_relative_events',
              'add_events_to_raw = pd_parser.commands.run:add_events_to_raw',
              'pd_parser_save_to_bids = '
              'pd_parser.commands.run:pd_parser_save_to_bids'
          ]},
          project_urls={
              'Bug Reports':
                  'https://github.com/alexrockhill/pd-parser/issues',
              'Source': 'https://github.com/alexrockhill/pd-parser',
          },
          install_requires=[
              'numpy>=1.19.0',
              'mne>=0.19.1',
              'mne-bids',
              'scipy',
              'pybv',
              'matplotlib',
              'argparse',
              'tqdm'
          ]
          )
