#
# Copyright (c) 2014-2020 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
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

"""tracktable.examples - Example scripts and Jupyter notebooks"""

import glob
import os.path
import shutil
import pathlib

def copy_example_notebooks(destdir, create_dir=True):
    """Copy Jupyter notebooks to a specified directory

    We bundle several example Jupyter notebooks with Tracktable.
    However, they're installed in a fairly well-hidden directory.
    This function will copy them to someplace more convenient.

    For example:
    >>> example_path = os.path.expanduser('~/tt_examples')
    >>> os.mkdir(example_path)
    >>> tracktable.examples.copy_example_notebooks(example_path)

    Arguments:
        destdir {string}: Destination directory for notebooks

    Keyword Arguments:
        create_directory {boolean]: Create directory if it doesn't
            already exist.  Defaults to True.

    Returns:
        No return value.

    Raises:
        OSError: the copy operation failed (probably because the
        destination directory doesn't exist)

    Note:
        This function relies on the __file__ special variable.
        It will probably fail if Tracktable is installed as a zip
        file.
    """

    here = os.path.dirname(__file__)
    notebook_dir = os.path.join(here, 'notebook_examples')

    if create_dir:
        pathlib.Path(destdir).mkdir(parents=True, exist_ok=True)

    all_notebooks = glob.glob('{}/*.ipynb'.format(notebook_dir))
    for notebook in all_notebooks:
        shutil.copy(notebook, destdir)

