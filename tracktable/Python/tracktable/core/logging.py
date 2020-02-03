#
# Copyright (c) 2014-2019 National Technology and Engineering
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
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Logging infrastructure

This file contains logging infrastructure for Tracktable.  For the
most part it just delegates to the standard Python logging module.
It differs in that we add a new TRACE log level.  We also intend to
add functions to unify this with the Boost logging code used in
Tracktable's C++ libraries.
"""

from __future__ import print_function, division, absolute_import

import warnings
import logging
from logging import getLogger


def warn_deprecated(message):
    """Warn the caller that a function is deprecated

    This function prints a message and possibly raises an exception when
    a deprecated function is called.  It must be used in the body of the
    function itself.  

    Example:

    def undesirable_function():
        warn_deprecated(("Please use good_function instead of "
                         "undesirable_function."))
        return do_thing_anyway()


    Args:
        message [string] What to print on the console
    """
    warnings.warn(message, DeprecationWarning, stacklevel=2)

class PrintFunctionHandler(logging.Handler):
    """
    A handler class which calls a function to print logging records,
    appropriately formatted.  

    Members:
        log_function [callable]: Function to call with the log message.
            By default this function is 'print'.
        extra_args [list]: Positional arguments to be supplied to the log 
            function after the message.
        extra_kwargs [dict]: Keyword arguments to be supplied to the log 
            function.
        terminator [string]: String to be appended to each log message.
            Defaults to the empty string.  A line ending is a good thing
            to put here if you need one.
    """

    terminator = ''

    def __init__(self, 
                 log_function=print,
                 extra_args=list(),
                 extra_kwargs=dict(),
                 terminator=''):
        """
        Initialize the handler.

        Arguments:
            log_function [callable]: Function to call with the log message.
                By default this function is 'print'.
            extra_args [list]: Positional arguments to be supplied to the log 
                function after the message.
            extra_kwargs [dict]: Keyword arguments to be supplied to the log 
                function.
            terminator [string]: String to be appended to each log message.
                Defaults to the empty string.  A line ending is a good thing
                to put here if you need one.
        
        """
        super(Handler, self).__init__()
        self._log_function = log_function
        self._extra_args = extra_args
        self._extra_kwargs = extra_kwargs
        self._terminator = terminator

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            msg = self.format(record)
            self.log_function(
                msg + self.terminator,
                *self.extra_args,
                **self.extra_kwargs)
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            self.handleError(record)

    @property
    def log_function(self):
        return self._log_function

    @log_function.setter
    def log_function(self, new_log_function):
        if new_log_function != self._log_function:
            self.acquire()
            self._log_function = new_log_function
            self.release()

    @property
    def extra_args(self):
        return self._extra_args

    @extra_args.setter
    def extra_args(self, new_extra_args):
        if new_extra_args != self._extra_args:
            self.acquire()
            self._extra_args = list(new_extra_args)
            self.release()

    @property
    def extra_kwargs(self):
        return self._extra_kwargs

    @extra_kwargs.setter
    def extra_args(self, new_extra_kwargs):
        if new_extra_kwargs != self._extra_kwargs:
            self.acquire()
            self._extra_kwargs = dict(new_extra_kwargs)
            self.release()

    @property
    def terminator(self):
        return self._terminator
    
    @terminator.setter
    def terminator(self, new_terminator):
        if new_terminator != self._terminator:
            self.acquire()
            self._terminator = new_terminator
            self.release()

    def __repr__(self):
        level = logging.getLevelName(self.level)
        name = str(self._log_function)
        if name:
            name += ' '
        return '<%s %s(%s)>' % (self.__class__.__name__, name, level)
