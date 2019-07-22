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

import codecs
import os
import re

from setuptools import setup, find_packages
from setuptools.dist import Distribution


###################################################################

NAME = "tracktable"
PACKAGES = find_packages(where="tracktable/Python")
META_PATH = os.path.join("tracktable", "Python", "tracktable", "__init__.py")

KEYWORDS = ["trajectory", "analysis", "visualization"]

CLASSIFIERS = [
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

###################################################################

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


META_FILE = read(META_PATH)

PYTHON_DEPENDENCIES=[
    'basemap',
    'matplotlib',
    'pytz',
    'pyshp'
    ]


def find_metadata_property(filename, property_name):
    """Extract a named property from a Python file.

    Suppose that you have a Python file (or, indeed, any text file)
    bunch of metadata properties with filenames like '__property1__',
    '__foo__', and '__bar__' in a file.  The lines in question look
    like:

    __foo__ = 'value of property Foo'
    __bar__ = "value of property Bar"

    This function will find those properties and return their values.
    """

    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=property_name),
        filename, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string in file {filename}.".format(
        meta=property_name,
        filename=filename))

# ----------------------------------------------------------------------


if __name__ == "__main__":
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("url"),
        version=find_meta("version"),
        author=find_meta("author"),
        maintainer=find_meta("author"),
        keywords=KEYWORDS,
#        long_description=read("README.rst"),
#        long_description_content_type="text/x-rst",
        packages=PACKAGES,
        package_dir={"": "tracktable/Python"},
        include_package_data=True,
#        package_data={ 'tracktable': BINARY_MODULES },
#        python_requires='>=3.4',
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=PYTHON_DEPENDENCIES,
        distclass=BinaryDistribution
    )
