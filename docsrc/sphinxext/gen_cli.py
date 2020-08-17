"""Custom sphinx extension to generate docs for the command line interace.

Inspired by MNE-Python's `gen_commands.py`
see: github.com/mne-tools/mne-python/blob/master/doc/sphinxext/gen_commands.py
"""
# Authors: Alex Rockhill <aprockhill@mailbox.org>
#
# License: BSD (3-clause)
import os
import os.path as op
import subprocess

import pd_parser as mod


def setup(app):
    """Set up the app."""
    app.connect('builder-inited', generate_cli_rst)


# Header markings go:
# 1. =/= : Page title
# 2. =   : Command name
# 3. -/- : Command description
# 4. -   : Command sections (Examples, Notes)

header = """\
:orphan:

.. _python_cli:

==============================={}
{} Command Line Interface (CLI)
==============================={}

Here we list the {} tools that you can use from the command line.

.. contents:: Contents
   :local:
   :depth: 1

"""

command_rst = """

.. _gen_{}:

{}

.. rst-class:: callout

{}

"""


def generate_cli_rst(app=None):
    """Generate the command line interface docs."""
    out_dir = op.abspath(op.join(op.dirname(__file__), '..', 'generated'))
    if not op.isdir(out_dir):
        os.mkdir(out_dir)
    out_fname = op.join(out_dir, 'cli.rst')

    fnames = sorted([name for name in mod.__dict__
                     if not name.startswith('__')])
    with open(out_fname, 'w') as f:
        f.write(header.format('=' * (len(mod.__name__) - 2), mod.__name__,
                              '=' * (len(mod.__name__) - 2), mod.__name__))
        for fname in fnames:
            output = subprocess.check_output(f'{fname} -h', shell=True)
            output = [line2.rstrip().strip() for line in output.splitlines()
                      for line2 in line.decode('ascii').split('   ') if line2]
            # put usage on one line
            while output[1] != 'positional arguments:':
                output[0] += ' ' + output.pop(1)
            # move positionals to the front
            output_args = output[0].split(' ')
            while '[' not in output_args[-1] and ']' not in output_args[-1]:
                output_args.insert(2, output_args.pop(-1))
            output[0] = ' '.join(output_args)
            # newline for positionals
            i = output.index('positional arguments:') + 1
            while output[i] != 'optional arguments:':
                output[i + 1] = '\t' + output[i + 1]
                i += 2
            # end with blank
            output.insert(i, '\n')
            # fix indentation
            i += 2
            while i + 1 < len(output):
                # reformat lists
                cmd = output[i].split(' ')[0][2:]
                list_entry = f'[{cmd.upper()} [{cmd.upper()} ...]]'
                if list_entry in output[i]:
                    output[i] = output[i].replace(
                        list_entry, f'LIST_OF_{cmd.upper()}')
                    output[0] = output[0].replace(
                        list_entry, f'LIST_OF_{cmd.upper()}')
                if output[i + 1][0] != '-':
                    output[i] += '\t\t' + output.pop(i + 1)
                    # fix too long line issue
                    while i + 1 < len(output) and output[i + 1][0] != '-':
                        output[i] += ' ' + output.pop(i + 1)
                output.insert(i + 1, '\n')
                i += 2
            # end with blank
            output.insert(-1, '\n')
            # make headers
            for name in ('positional arguments:', 'optional arguments:'):
                output[output.index(name)] = \
                    '\n' + name[:-1] + '\n' + '-' * (len(name) - 1)
            title = fname + '\n' + '=' * len(fname)
            output = '\n'.join([item for item in output if item])
            f.write(command_rst.format(fname, title, output))

    print('[Done]')


# This is useful for testing/iterating to see what the result looks like
if __name__ == '__main__':
    generate_cli_rst()
