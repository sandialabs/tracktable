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

"""movie_from_csv.py - Example of how to render a movie of
trajectories directly from a .traj file

Note:
    Cartopy v0.18.0 is required to successfully render maps and pass
    our internal tests.

"""

import datetime
import logging
import sys

import matplotlib
import matplotlib.animation
from matplotlib import pyplot
from tracktable.feature import annotations
from tracktable.render.render_movie import render_trajectory_movie
from tracktable.script_helpers import argparse, argument_groups

matplotlib.use('Agg')

# ----------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description='Render a movie of traffic found in a delimited text file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    argument_groups.use_argument_group("delimited_text_point_reader", parser)
    argument_groups.use_argument_group("trajectory_assembly", parser)
    argument_groups.use_argument_group("trajectory_rendering", parser)
    argument_groups.use_argument_group("mapmaker", parser)
    argument_groups.use_argument_group("movie_rendering", parser)

    parser.add_argument('--trail-duration',
                        help="How long should each object's trail last? (seconds)",
                        type=int,
                        default=300)

    parser.add_argument('trajectory_data_file',
                        nargs=1,
                        help='Delimited text file containing trajectory data')

    parser.add_argument('movie_file',
                        nargs=1,
                        help='Filename for trajectory movie')

    args = parser.parse_args()
    if args.resolution is None:
        args.resolution = [ 800, 600 ]
    if args.delimiter == 'tab':
        args.delimiter = '\t'

    return args

# ----------------------------------------------------------------------

def setup_trajectory_source(filename, args):
    if args.domain == 'terrestrial':
        from tracktable.domain.terrestrial import TrajectoryReader
    else:
        from tracktable.domain.cartesian2d import TrajectoryReader

    infile = open(filename, 'rb')
    return TrajectoryReader(infile)


# ----------------------------------------------------------------------

def main():
    logger = logging.getLogger(__name__)

    # Parse the command line arguments and grab sets we will need later.
    args = parse_args()
    mapmaker_kwargs = argument_groups.extract_arguments("mapmaker", args)
    movie_kwargs = argument_groups.extract_arguments("movie_rendering", args)
    trajectory_rendering_kwargs = argument_groups.extract_arguments("trajectory_rendering", args)

    # Load all the trajectories into memory.
    logger.info("Initializing trajectory source")
    trajectory_source = setup_trajectory_source(args.trajectory_data_file[0], args)

    logger.info("Collecting all trajectories")
    trajectories = list(trajectory_source)

    # Add the 'progress' annotation to all of our trajectories so
    # we have some way to color them
    trajectories = [annotations.progress(t) for t in trajectories]

    #
    # Lights! Camera! Action!
    #
    render_trajectory_movie(
        trajectories,
        backend='ffmpeg',
        filename=args.movie_file[0],
        trail_duration=datetime.timedelta(seconds=args.trail_duration),
        **trajectory_rendering_kwargs,
        **mapmaker_kwargs,
        **movie_kwargs,
        )

    pyplot.close()

    logger.info("Movie render complete. File saved to {}".format(args.movie_file[0]))

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
