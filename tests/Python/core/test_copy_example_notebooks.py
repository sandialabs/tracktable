#
# Copyright (c) 2014-2023 National Technology and Engineering Solutions of
# Sandia, LLC. Under the terms of Contract DE-NA0003525 with National
# Technology and Engineering Solutions of Sandia, LLC, the
# U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# Test case for tracktable.examples.copy_example_notebooks()

import tracktable.examples

import glob
import logging
import os
import os.path
import sys
import tempfile

logger = logging.getLogger(__name__)

def test_copy_example_notebooks(destdir):

    # Get a list of all the example notebooks
    here = os.path.dirname(__file__)
    tutorial_notebook_dir = os.path.normpath(
        os.path.join(here, '..', '..', 'examples', 'tutorials')
        )
    tutorial_notebook_files = glob.glob('{}/*.ipynb'.format(tutorial_notebook_dir))

    analytic_demo_notebook_dir = os.path.normpath(
        os.path.join(here, '..', '..', 'examples', 'analytic_demos')
        )
    analytic_demo_notebook_files = glob.glob('{}/*.ipynb'.format(analytic_demo_notebook_dir))

    tracktable.examples.copy_example_notebooks(destdir)

    # For each notebook: make sure it's present, readable, and has
    # the same size

    error_count = 0
    for notebook in tutorial_notebook_files:
        filename_only = os.path.split(notebook)[1]
        copied_filename = os.path.join(destdir, filename_only)

        if not os.path.exists(copied_filename):
            logger.error('Notebook {} was not copied from {}'.format(
                filename_only, tutorial_notebook_dir))
            error_count += 1
        else:
            # It was copied - is it plausibly the same thing?
            original_stat = os.stat(notebook)
            new_stat = os.stat(copied_filename)
            if original_stat.st_size != new_stat.st_size:
                logger.error(('Notebook {} has incorrect size after copy. '
                       'Original size was {} and copied size is {}.').format(
                       original_stat.st_size, new_stat.st_size))
                error_count += 1

    for notebook in analytic_demo_notebook_files:
        filename_only = os.path.split(notebook)[1]
        copied_filename = os.path.join(destdir, filename_only)

        if not os.path.exists(copied_filename):
            logger.error('Notebook {} was not copied from {}'.format(
                filename_only, analytic_demo_notebook_dir))
            error_count += 1
        else:
            # It was copied - is it plausibly the same thing?
            original_stat = os.stat(notebook)
            new_stat = os.stat(copied_filename)
            if original_stat.st_size != new_stat.st_size:
                logger.error(('Notebook {} has incorrect size after copy. '
                       'Original size was {} and copied size is {}.').format(
                       original_stat.st_size, new_stat.st_size))
                error_count += 1

    return error_count


def main():
    if len(sys.argv) != 2:
        print('usage: {} test_output_directory'.format(sys.argv[0]))
        return 1

    test_output_dir = sys.argv[1]
    if not os.path.exists(test_output_dir):
        raise OSError('Destination {} does not exist or is not a directory.')

    notebook_outdir = tempfile.mkdtemp(prefix=test_output_dir)
    error_count = 0
    #Test with pre made directory
    error_count += test_copy_example_notebooks(notebook_outdir)
    #Test without pre made directory
    error_count += test_copy_example_notebooks(notebook_outdir+"XYZ")

    return error_count


if __name__ == '__main__':
    sys.exit(main())