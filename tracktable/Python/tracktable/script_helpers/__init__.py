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
Tracktable Trajectory Toolkit - Helper functions for creating scripts
"""


import sys
if sys.version_info[0] == 2:
	from itertools import izip_longest
else:
	from itertools import zip_longest as izip_longest

def n_at_a_time(iterable, howmany, fillvalue=None):
    """Collect data into fixed-length chunks or blocks

    This function is an adapter for an iterable that returns
    objects N at a time instead of one at a time.  

    Example:
		>>> list(n_at_a_time(range(10), 3, -1))
		[(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, -1, -1)]

	Args:
		iterable {sequence}: Data source
		howmany {int}: How many elements to take at a time
		fillvalue {any}: Value to pad with if the iterable runs out

	Returns:
		New sequence whose elements are tuples of elements from
		the original iterable
	"""
    args = [ iter(iterable) ] * howmany
    return izip_longest(fillvalue=fillvalue, *args)


# ----------------------------------------------------------------------
