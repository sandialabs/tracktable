# Copyright (c) 2014-2022 National Technology and Engineering
# Solutions of Sandia, LLC . Under the terms of Contract DE-NA0003525
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

# setup-generic.py -- build Tracktable wheels for Linux, Windows, and
# Mac OS X

import codecs
import glob
import os
import os.path
import platform
import re
import sys

from setuptools import find_packages, setup
from setuptools.dist import Distribution


class BinaryDistribution(Distribution):
    def is_pure(self):
        return False

# ----------------------------------------------------------------------


def files_from_components(*components):
    return glob.glob(os.path.join(*components))

# ----------------------------------------------------------------------


def read(filename):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(filename, "rb", "utf-8") as f:
        return f.read()

# ----------------------------------------------------------------------


def find_metadata_property(text, property_name):
    """Extract a named property from a Python file.

    Suppose that you have a text file containing a bunch of metadata
    properties with filenames like '__property1__', '__foo__', and
    '__bar__' in a file.  The lines in question look like:

    __foo__ = 'value of property Foo'
    __bar__ = "value of property Bar"

    This function will find those properties and return their values.

    """

    property_regex = r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(
        meta=property_name
        )

    meta_match = re.search(property_regex, text, re.M)

    if meta_match:
        return meta_match.group(1)
    else:
        raise RuntimeError(
            "Unable to find __{meta}__ string in text.".format(
                meta=property_name
            ))

# --------------------------------------------------------------------

def main():
    here = os.getcwd()
    tracktable_home = os.path.join(here, 'Python', 'tracktable')
    init_filename = os.path.join(tracktable_home, '__init__.py')

    if not (os.path.exists(init_filename) and os.path.isfile(init_filename)):
        raise RuntimeError(
            ('This script must be run from the root of a '
             'Tracktable install tree.  Specifically, the file '
             '<here>/Python/tracktable/__init__.py must exist.'))

    init_file_text = read(init_filename)
    # Parse the following properties out of the top-level __init__.py
    # so that they are always current.
    properties_in_init = [
                        'author',
                        'description',
                        'license',
                        'maintainer',
                        'url'
                    ]

    metadata_from_init = {}
    for key in properties_in_init:
        metadata_from_init[key] = find_metadata_property(init_file_text, key)

    version = re.search(r"^TRACKTABLE VERSION ([0-9\.]*)", open(os.path.join(os.path.dirname(__file__), "..", "version.txt"), "rt").read(), re.M).group(1)
    metadata_from_init['version'] = version

    # --------------------

    # Update tracktable's version if we're doing a nightly build
    if os.getenv("NIGHTLY") == "true":
        from datetime import datetime
        today = datetime.today().strftime('%m%d%Y') # month, day, year format
        nightly_version = ".dev" + today # `dev` or `post` are the only words accepted in version strings
        metadata_from_init["version"] =  metadata_from_init["version"] + nightly_version
        print("Updating version to nightly version: {}".format(metadata_from_init["version"]))

    # Update tracktable's version if we're doing a development build
    if os.getenv("DEVELOPMENT") == "true":
        development_version = ".dev" + str(os.getenv("DEV_NUMBER")) # `dev` or `post` are the only words accepted in version strings
        metadata_from_init["version"] =  metadata_from_init["version"] + development_version
        print("Updating version to development version: {}".format(metadata_from_init["version"]))

    # --------------------

    # Computed properties here

    here = os.getcwd()
    directory_containing_tracktable = os.path.join(here, 'Python')
    package_directory = {'': directory_containing_tracktable}
    tracktable_contents = find_packages(where=directory_containing_tracktable)

    system = platform.system()

    if system == 'Linux':
        extension_suffix = 'so'
        shared_library_suffix = None
        os_classifier = 'Operating System :: POSIX :: Linux'
    elif system == 'Darwin':
        extension_suffix = 'so'
        shared_library_suffix = None
        os_classifier = 'Operating System :: MacOS :: MacOS X'
    elif system == 'Windows':
        extension_suffix = 'pyd'
        shared_library_suffix = 'dll'
        os_classifier = 'Operating System :: Microsoft :: Windows'
    else:
        raise RuntimeError('Unknown operating system: {}'.format(system))

    binary_extensions = glob.glob(
        os.path.join(here, 'Python', 'tracktable', '*',
                     '*.{}'.format(extension_suffix))
        )

    support_libraries = []
    if shared_library_suffix is not None:
        support_libraries.extend(
            glob.glob(
                os.path.join(here, 'Python', 'tracktable', '*',
                             '*.{}'.format(shared_library_suffix))
                )
        )

    tutorial_notebook_directory = os.path.join(tracktable_home, 'examples', 'tutorials')
    tutorial_notebook_files = files_from_components(tutorial_notebook_directory, '*.ipynb')

    analytic_demo_notebook_directory = os.path.join(tracktable_home, 'examples', 'analytic_demos')
    analytic_demo_notebook_files = files_from_components(analytic_demo_notebook_directory, '*.ipynb')

    analytic_demo_images_directory = os.path.join(tracktable_home, 'examples', 'analytic_demos', 'demo_images')
    analytic_demo_images_files = files_from_components(analytic_demo_images_directory, '*.png')

    response_files_directory = os.path.join(tracktable_home, 'examples', 'response_files')
    response_files_files = files_from_components(response_files_directory, '*.txt')

    license_files = [os.path.join(tracktable_home, 'LICENSE.txt')]

    # --------------------

    # Static properties here

    keywords = [
        'trajectory', 'analysis', 'visualization'
        ]

    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        os_classifier,
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: C++",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization"
    ]

    dependencies = [
        'cartopy',
        'matplotlib',
        'pyshp',
        'pytz',
        'six',
        'folium'
        'tracktable-data'
    ]

    package_name = 'tracktable'
    version_required = '>=3.6'

    # --------------------

    print(metadata_from_init)

    setup(
        # Static properties
        name=package_name,
        classifiers=classifiers,
        install_requires=dependencies,
        keywords=keywords,
        python_requires=version_required,
        long_description=read(os.path.join(tracktable_home, 'README.md')),
        long_description_content_type='text/markdown',

        # Computed properties
        package_dir=package_directory,
        packages=tracktable_contents,
        package_data={
            'tracktable':
                (binary_extensions +
                 support_libraries +
                 license_files +
                 tutorial_notebook_files +
                 analytic_demo_notebook_files +
                 analytic_demo_images_files +
                 response_files_files)
                },
        # Assembly information and system parameters
        distclass=BinaryDistribution,
        zip_safe=False,

        # All the other stuff we collected
        **metadata_from_init
    )

# ----------------------------------------------------------------------


if __name__ == '__main__':
    sys.exit(main())
