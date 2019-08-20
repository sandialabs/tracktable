# Welcome to Tracktable!

Tracktable is a set of Python and C++ libraries for the processing,
analysis, and rendering of trajectory data.  We define a trajectory as
"a sequence of points with timestamps and a unique identifier".

Tracktable's main interface is a set of Python modules.  Underneath
that, we implement the core data structures and algorithms in C++ for
speed and more efficient memory use.  While you are welcome to work
entirely in C++ if you prefer, we find it easier to use Tracktable in
Python scripts and Jupyter notebooks.

For more information, please visit us at the (Tracktable home
page)[https://tracktable.sandia.gov].

# Getting Tracktable

Our main Git repository is at [https://github.com/sandialabs/tracktable.git].  We also upload Python wheels to (PyPI)[https://pypi.org] so you can 'pip install tracktable' on most recent distributions.  

If you choose to build from source, installation instructions are in
the Git repository as part of the documentation.

# Compatibility

Our development systems typically have the (Anaconda Python distribution)[https://anaconda.com] installed.  However, there is nothing Anaconda-specific in our requirements or dependencies.  We rely on (Cartopy)[ for rendering maps in Python and 

We use Cartopy for rendering maps in Python.  

# Using Tracktable

Our documentation is hosted at [https://tracktable.readthedocs.org].  We distribute Tracktable under a 3-clause BSD license whose text is included in the source distribution as well as on (our web site)[https://tracktable.sandia.gov/license.html].
