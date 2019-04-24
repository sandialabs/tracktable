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
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""tracktable.core.misc - Stuff that doesn't yet fit anywhere else"""

from __future__ import division, absolute_import, print_function

class IterableWrapper(object):
    """Wrap up an iterable for later use

    When assembling a data flow pipeline we would like to separate the
    actions of hooking up the pipeline and reading data from it.
    """

    def __init__(self, inner_iter):
        """Wrap another iterable

        Args:
          inner_iter (iterable): Thing to wrap
        """

        self._inner_iter = inner_iter

    def __iter__(self):
        return self

    def __next__(self):
        """Internal method

        This is how Python objects iterate.  You get things from them
        by calling __next__() over and over until they raise
        StopIteration to tell you that there's nothing left.

        NOTE: This has changed in Python 3.7.  The proper way to
        return from a generator is now 'return' instead of 'raise
        StopIteration()'.  See PEP 0479 for the details:

        https://www.python.org/dev/peps/pep-0479/

        Returns:
           Whatever the inner iterator returns

        Raises:
           StopIteration

        """

        return self._inner_iter.next()

    next = __next__
