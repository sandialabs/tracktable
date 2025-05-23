# Copyright (c) 2014-2023 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Copy the jupyter notebooks from tracktable-docs to tracktable and clean them of output
"""

import os
import shutil
import subprocess
import sys

# We need different notebook-cleaning commands depending on the nbconvert version
NBCONVERT_VERSION: int = -1

def copy_and_clean_notebook(notebook_filename: str,
                            dest_path: str,
                            check_timestamp: bool=True):
    """Copy and clean a single notebook.

    This function will run a notebook through `nbconvert` to remove its output
    cells, then copy it into the destination directory.

    Arguments:
        notebook_filename (str): Filename (with full path) to notebook to clean
        dest_path (str): Where to put the cleaned notebook

    Keyword Arguments:
        check_timestamp (bool): If True, the timestamp on `destpath/notebook_filename`
            will be compared to the timestamp on the input notebook.  If the cleaned
            notebook is newer than the input, nothing will be done.

    Returns:
        None
    """

    (_, notebook_only) = os.path.split(notebook_filename)
    dest_filename = os.path.join(dest_path, notebook_only)

    if check_timestamp:
        if os.path.exists(dest_filename):
            if os.path.getmtime(dest_filename) > os.path.getmtime(notebook_filename):
                print(f"-- INFO: Output notebook {notebook_only} is newer than input.  Cleaning not needed.")
                return

    shutil.copyfile(notebook_filename, dest_path)

    if NBCONVERT_VERSION > 6:
        # Running this through the shell is much more concise than doing the
        # conversion programmatically.
        subprocess.check_output(['jupyter', 'nbconvert',
                                 '--clear-output', '--inplace',
                                 '--log-level', 'WARN',
                                 dest_filename])
    else:
        subprocess.check_output(['jupyter', 'nbconvert',
                                 '--ClearOutputPreprocessor.enabled=True', '--inplace',
                                 '--log-level', 'WARN',
                                 dest_filename])


def copy_notebook_directory(source: str, dest: str):
    """Copy a directory of demo notebooks and clean their contents.

    Also copies any auxiliary files or directories we find along the way.

    Arguments:
        source (str): Source path containing notebooks to copy
        dest (str): Destination path for cleaned notebooks

    Returns:
        None
    """
    for thing in os.scandir(source):
        if thing.is_dir():
            # This is specifically for the `demo_images` folder since
            # we don't keep an empty folder for it in tracktable
            shutil.copytree(os.path.join(source, thing.name),
                            os.path.join(dest, thing.name),
                            dirs_exist_ok=True)
        elif thing.name.endswith('.ipynb'):
            copy_and_clean_notebook(os.path.join(source, thing.name), dest)
        else:
            shutil.copy(os.path.join(source, thing.name), dest)

# --------------------------------------------------------------------

def main():
    global NBCONVERT_VERSION

    here = os.path.dirname(__file__)
    # We expect to be in $repository/src/Python/tracktable
    tracktable_docs = os.path.normpath(
        os.path.join(here, '..', '..', '..', 'tracktable-docs')
    )

    # Commands differ based on the version of nbconvert installed
    nbconvert_version_full = subprocess.check_output(['jupyter', 'nbconvert', '--version'])
    NBCONVERT_VERSION = int(nbconvert_version_full.decode().strip()[0])

    tutorial_src_path = os.path.join(tracktable_docs, 'tutorial_notebooks')
    tutorial_dest_path = os.path.join(here, 'examples', 'tutorials')

    analysis_demo_src_path = os.path.join(tracktable_docs, 'analytic_demo_notebooks')
    analysis_demo_dest_path = os.path.join(here, 'examples', 'analytic_demos')

    copy_notebook_directory(tutorial_src_path, tutorial_dest_path)
    copy_notebook_directory(analysis_demo_src_path, analysis_demo_dest_path)

    return 0


if __name__=='__main__':
  sys.exit(main())