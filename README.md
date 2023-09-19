# Welcome to Tracktable!

Tracktable is a set of Python and C++ libraries for the processing,
analysis, and rendering of trajectory data.  We define a trajectory as
"a sequence of points with timestamps and a unique identifier".

Tracktable's main interface is a set of Python modules.  Underneath
that, we implement the core data structures and algorithms in C++ for
speed and more efficient memory use.  While you are welcome to work
entirely in C++ if you prefer, we find it easier to use Tracktable in
Python scripts and Jupyter notebooks.

For more information, please visit us at the [Tracktable home
page](https://tracktable.sandia.gov).

# Getting Tracktable

Our main Git repository is at <https://github.com/sandialabs/tracktable.git>.
We also upload Python wheels to [PyPI](https://pypi.org) so you can
'pip install tracktable' on most recent distributions.

If you choose to build from source, installation instructions are in
the Git repository as part of the documentation.

# Compatibility

Our development systems typically have the [Anaconda Python
distribution](https://anaconda.com) installed.  However, there is
nothing Anaconda-specific in our requirements or dependencies.  We
rely on [Cartopy](https://scitools.org.uk/cartopy) for rendering maps
in Python as well as Pyshp for shapefile read/write support.



# Using Tracktable

Our documentation is hosted at <https://tracktable.readthedocs.org>.
We distribute Tracktable under a 3-clause BSD license whose text is
included in the source distribution as well as on
[our web site](https://tracktable.sandia.gov/license.html "Tracktable License").

### Copyright Notice

Copyright (c) 2014-2023 National Technology and Engineering
Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
with National Technology and Engineering Solutions of Sandia, LLC,
the U.S. Government retains certain rights in this software.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
