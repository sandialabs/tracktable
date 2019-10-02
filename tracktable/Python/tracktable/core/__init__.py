#
# Copyright (c) 2014-2017 National Technology and Engineering
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

"""
TrailMix Trajectory Library - Core

Basic types (point, trajectory) live in this module.  They are in turn
imported from the small C extension libraries.
"""

# This will register the converters for PropertyMap and Timestamp (aka
# boost::posix_time::ptime)
from . import core_types
from .core_types import BoostPythonArgumentError, set_default_timezone
from .core_types import current_memory_use, peak_memory_use
from .timestamp import Timestamp

import os.path

def data_directory():
    """Return path to Tracktable example data files

    We bundle a few example data files inside Tracktable.  This
    function will give you the path to those.  Use it as follows:

    import os.path
    from tracktable.core import data_directory

    with open(os.path.join(data_directory(), "SampleASDI.csv")) as asdi_file:
         # Do your own stuff with the data

    Arguments:
        No arguments.

    Returns:
        Path to Tracktable example data files.
    """

    data_directory = os.path.join(os.path.dirname(__file__), '..', 'examples', 'data')
    normalized_dir = os.path.normpath(data_directory)
    return normalized_dir
