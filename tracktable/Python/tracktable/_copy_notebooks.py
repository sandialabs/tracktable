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
import filecmp
import hashlib

def copy_notebooks(source, dest):
    for thing in os.scandir(source):
        if thing.is_dir(): # This is specifically for the `demo_images` folder since we don't keep an empty folder for it in tracktable
            if not os.path.exists(os.path.join(dest, thing.name)): # If the destination sub-folder doesn't exist then create it
                os.mkdir(os.path.join(dest, thing.name))
            copy_notebooks(os.path.join(source, thing.name), os.path.join(dest, thing.name))
        else:
            if os.path.exists(os.path.join(dest, thing.name)): # If the files are already copied check if we even need to copy them
                if not filecmp.cmp(os.path.join(source, thing.name), os.path.join(dest, thing.name)):
                    shutil.copy(os.path.join(source, thing.name), dest)
            else:
                shutil.copy(os.path.join(source, thing.name), dest)

# --------------------------------------------------------------------

def clear_notebook_output(notebook_directory, nbconvert_version):
    for file in os.listdir(notebook_directory):
        if file.endswith(".ipynb"):
            # As far as I can tell just running the CLI command is way easier for doing the conversions comapred to the API
            if nbconvert_version >= 6:
                subprocess.check_output(['jupyter', 'nbconvert', '--clear-output', '--inplace', '--log-level', 'WARN', os.path.join(notebook_directory, file)])
            else:
                subprocess.check_output(['jupyter', 'nbconvert', '--ClearOutputPreprocessor.enabled=True', '--inplace', '--log-level', 'WARN', os.path.join(notebook_directory, file)])

# --------------------------------------------------------------------

def main():
    here = os.path.dirname(__file__)
    tracktable_home = os.path.join(here)
    tracktable_docs = os.path.join(here, '..', '..', '..', 'tracktable-docs')

    # Commands differ based on the version of nbconvert installed
    nbconvert_version = subprocess.check_output(['jupyter', 'nbconvert', '--version'])
    nbconvert_version = int(nbconvert_version.decode().strip()[0])

    # Copy tutorial notebooks to tracktable and clear output
    tracktable_docs_tutorial_notebook_directory = os.path.join(tracktable_docs, 'tutorial_notebooks')
    tracktable_docs_cleaned_tutorial_notebook_directory = os.path.join(tracktable_docs, "cleaned_tutorial_notebooks")
    tutorial_notebook_directory = os.path.join(tracktable_home, 'examples', 'tutorials')

    os.mkdir(tracktable_docs_cleaned_tutorial_notebook_directory)
    copy_notebooks(tracktable_docs_tutorial_notebook_directory, tracktable_docs_cleaned_tutorial_notebook_directory)
    clear_notebook_output(tracktable_docs_cleaned_tutorial_notebook_directory, nbconvert_version)
    copy_notebooks(tracktable_docs_cleaned_tutorial_notebook_directory, tutorial_notebook_directory)
    shutil.rmtree(tracktable_docs_cleaned_tutorial_notebook_directory)

    # Copy analytic demo notebooks and images to tracktable and clear output
    tracktable_docs_analytic_demo_notebook_directory = os.path.join(tracktable_docs, 'analytic_demo_notebooks')
    tracktable_docs_cleaned_analytic_demo_notebook_directory = os.path.join(tracktable_docs, "cleaned_analytic_demo_notebooks")
    analytic_demo_notebook_directory = os.path.join(tracktable_home, 'examples', 'analytic_demos')

    os.mkdir(tracktable_docs_cleaned_analytic_demo_notebook_directory)
    copy_notebooks(tracktable_docs_analytic_demo_notebook_directory, tracktable_docs_cleaned_analytic_demo_notebook_directory)
    clear_notebook_output(tracktable_docs_cleaned_analytic_demo_notebook_directory, nbconvert_version)
    copy_notebooks(tracktable_docs_cleaned_analytic_demo_notebook_directory, analytic_demo_notebook_directory)
    shutil.rmtree(tracktable_docs_cleaned_analytic_demo_notebook_directory)


if __name__=='__main__':
  main()