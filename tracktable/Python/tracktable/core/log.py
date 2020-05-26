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

from __future__ import print_function, division, absolute_import

from tracktable.lib import _logging as cpp_logging

import logging
import warnings

# The logging module doesn't have loglevel TRACE by default.  I think
# it should.

logging.TRACE = 5


def set_log_level(level):
    """Set the global log level for both C++ and Python code

    In Release 1.3, Tracktable uses separate loggers for its
    C++ and Python code.  This function will set the log level
    on both of them at once.

    NOTE: There is not yet a way to redirect log messages generated
    in C++ to any sink other than standard error.  Expect this
    to be fixed by release 1.4.

    Arguments:
        level {integer} -- desired minimum log level.  This will
            usually be one of the constants defined in the `logging`
            module: `NOTSET`, `DEBUG`, `INFO`, `WARNING`, `ERROR`,
            or `FATAL`.

    Returns:
        No return value.
    """
    logging.getLogger().setLevel(level)
    cpp_logging.set_cpp_log_level(level)


def log_level():
    """Retrieve the global log level

    This is a convenience function provided for symmetry with
    `set_log_level`.  It retrieves the current log level and
    returns it as an integer.  You could just as easily call
    logging.getLogger().getEffectiveLevel().

    Arguments:
        No arguments.

    Returns:
        Current log level as an integer.
    """
    return logging.getLogger().getEffectiveLevel()


def warn_deprecated(message):
    """Warn the caller that a function is deprecated

    This function prints a message and possibly raises an exception when
    a deprecated function is called.  It must be used in the body of the
    function itself.

    Arguments:
        message: {string} What to print on the console

    Returns:
        No return value.

    """
    warnings.warn(message, DeprecationWarning, stacklevel=2)

