### THIS FILE IS NOT READY FOR PRODUCTION.

# Copyright (c) 2014-2019 National Technology and Engineering
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


import argparse
import codecs
import glob
import os
import os.path
import re
import sys

from setuptools import setup, find_packages
from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False

HERE = os.path.abspath(os.path.dirname(__file__))



def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))

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

    property_regex = r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=property_name)

    meta_match = re.search(property_regex, text, re.M)

    if meta_match:
        return meta_match.group(1)
    else:
        raise RuntimeError(
            "Unable to find __{meta}__ string in text.".format(meta=property_name)
            )

# ----------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tracktable-build',
                        default='tracktable',
                        help='Root of Tracktable install that will be used to build wheel')
    parser.add_argument('--output-dir',
                        help='Directory where wheel should be written',
                        default='.')

    return parser.parse_known_args()

# --------------------------------------------------------------------

def main():
    (known_args, unrecognized_args) = parse_args()

    metadata_from_init = {}

    if 'bdist_wheel' not in known_args:
        raise RuntimeError('This script can only be used to build wheels.')

    if known_args.tracktable_build is None:
        raise RuntimeError('To build a wheel, you must supply the path to an installed Tracktable with "--tracktable-build".')


    init_filename = os.path.join(known_args.tracktable_build,
                                 'Python',
                                 'tracktable',
                                 '__init__.py')

    init_file_text = read(init_filename)
    # Parse the following properties out of the top-level __init__.py
    # so that they are always current.
    properties_in_init = [
        'author', 'description', 'license', 'maintainer', 'url', 'version'
    ]
    for key in properties_in_init:
        metadata_from_init[key] = find_metadata_property(init_file_text, key)


    # --------------------

    # Computed properties here

    tracktable_path = os.path.join(known_args.tracktable_build, 'Python')
    package_directory = { '': tracktable_path }
    tracktable_contents = find_packages(where=tracktable_path)
    # XXX this line will have to change for Windows
    binary_extensions = glob.glob(os.path.join(
        tracktable_path, 'tracktable', '*', '*.so'
        ))

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
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: C++",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization"
    ]

    dependencies = [
        'basemap',
        'matplotlib',
        'pyshp',
        'pytz'
    ]

    package_name = 'tracktable'

    version_required = '>=3.4'

    # --------------------

    setup(
        script_args=unrecognized_args,

        # Static properties
        name=package_name,
        classifiers=classifiers,
        install_requires=dependencies,
        keywords=keywords,
        python_requires=version_required,
        **metadata_from_init,

        # Computed properties
        package_dir=package_directory,
        packages=tracktable_contents,
        package_data={ 'tracktable': binary_extensions },

        # Assembly information and system parameters
        distclass=BinaryDistribution,
        zip_safe=False

        # long_description=read('README.rst'),
        # long_description_content_type='text/x-rst',


    )

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())

