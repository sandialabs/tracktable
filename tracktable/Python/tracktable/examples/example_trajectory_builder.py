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

"""example_trajectory_builder - Sample code to assemble points into trajectories
"""
from tracktable.domain import all_domains as ALL_DOMAINS
import importlib
import itertools
import datetime

from tracktable.source.trajectory import AssembleTrajectoryFromPoints
from tracktable.core import geomath

# ----------------------------------------------------------------------

def configure_trajectory_builder(separation_distance=100,
                                 separation_time=20,
                                 minimum_length=10):
    """Set up a trajectory builder using the specified parameters

    Instantiate and configure an AssembleTrajectoryFromPoints.  You
    will still need to set its 'input' member before it's ready to go.

    Args:
       separation_distance:  Two successive points that are at least this far apart (in KM) will be placed in separate trajectories.
       separation_time:      Two successive points with at least this many minutes between them will be placed in separate trajectories.
       minimum_length:       Trajectories with fewer than this many points will be discarded.

    Returns:
       A new instance of AssembleTrajectoryFromPoints
    """

    source = AssembleTrajectoryFromPoints()

    if separation_distance is not None:
        source.separation_distance = float(separation_distance)
    if separation_time is not None:
        source.separation_time = datetime.timedelta(minutes=separation_time)
    if minimum_length is not None:
        source.minimum_length = minimum_length

    return source

def example_trajectory_builder(inputFile=None):

    if inputFile == None:
        inputFile = './data/SampleFlight.csv';

    inFile = open(inputFile)
    domain = 'terrestrial'                 # we want to create a terrestrial point reader
    if domain.lower() not in ALL_DOMAINS:  #Format domain and make sure it is an available domain
        raise KeyError("Domain '{}' is not in list of installed domains ({}).".format(domain, ', '.join(ALL_DOMAINS)))
    else:
        domain_to_import = 'tracktable.domain.{}'.format(domain.lower())
        domain_module = importlib.import_module(domain_to_import)

    point_source = domain_module.TrajectoryPointReader()
    point_source.input = inFile
    point_source.comment_character = '#'
    point_source.field_delimiter = ','

    source = configure_trajectory_builder(separation_distance=50, separation_time=10, minimum_length=5)

    source.input = point_source
    return source.trajectories()