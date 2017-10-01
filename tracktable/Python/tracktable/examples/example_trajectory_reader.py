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
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
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

"""example_point_reader - Common code to configure a DelimitedText point reader
"""

from tracktable.domain import all_domains as ALL_DOMAINS
from tracktable.script_helpers.argument_groups import extract_arguments

import importlib
import itertools

# ----------------------------------------------------------------------

def configure_trajectory_reader(infile, **kwargs):
    """Set up a TrajectoryReader.

    Args:
        infile: An open file or file-like object containing the input.

    Returns:
        The ready-to-use trajectory reader.  In order to actually
        retrieve the trajectories, iterate over the contents of the
        object returned by this function.

    """

    reader_args = extract_arguments('trajectory_reader', kwargs)


    domain = reader_args['domain']
    if domain.lower() not in ALL_DOMAINS:
        raise KeyError("Domain '{}' is not in list of installed domains ({}).".format(
            domain, ', '.join(ALL_DOMAINS)))
    else:
        domain_to_import = 'tracktable.domain.{}'.format(domain.lower())
        domain_module = importlib.import_module(domain_to_import)

    reader = domain_module.TrajectoryReader()
    reader.input = infile

    return reader

# ----------------------------------------------------------------------
# Utility function for reading groups of elements from an iterable

def group(iterable, howmany, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"

    # group('ABCDEFG', 3, 'x') -> ABC DEF Gxx
    args = [ iter(iterable) ] * howmany
    return izip_longest(fillvalue=fillvalue, *args)
