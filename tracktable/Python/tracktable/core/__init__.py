#
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

"""
Tracktable Trajectory Library - Core

Basic types (point, trajectory) live in this module.  They are in turn
imported from the small C extension libraries.
"""

# This will register the converters for PropertyMap and Timestamp (aka
# boost::posix_time::ptime)
from . import core_types
from .core_types import BoostPythonArgumentError, set_default_timezone
from .core_types import current_memory_use, peak_memory_use
from .timestamp import Timestamp


def data_directory():
    """Return path to Tracktable example data files

    .. important:: This function as been superseded by the ``tracktable_data`` package's ``retrieve()`` function.

    We bundle a few example data files inside Tracktable.  This
    function will give you the path to those.  Use it as follows:

    .. code-block:: python

        import os.path
            from tracktable.core import data_directory

            with open(os.path.join(data_directory(), "SampleASDI.csv")) as asdi_file:
                # Do your own stuff with the data

    Returns:
        Path to Tracktable example data files.
    """

    # TODO (mjfadem): Remove this function in release 1.8

    import warnings

    # This just stops the source line from printing with the warning
    def format_warning(message, category, filename, lineno, file=None, line=None):
        return '%s:%s: %s:%s\n' % (filename, lineno, category.__name__, message)

    warnings.formatwarning = format_warning

    # Allow the DeprecationWarning through since it's disabled by default
    warnings.simplefilter("always", category=DeprecationWarning)

    # This will display a DeprecationWarning when the source modules are imported
    warnings.warn(" `data_directory()` has been deprecated and removed and is superseded by the `tracktable_data` package's `retrieve()` function. Use `retrieve(filename=<filename>)` to get the desired file path.", category=DeprecationWarning)

    import sys

    if sys.version_info[1] < 7:
        sys.tracebacklimit = None
    else:
        sys.tracebacklimit = 0

    raise NotImplementedError
