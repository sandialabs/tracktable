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

"""parallel_movie_from_points.py - Example of how to render a movie of
trajectories built from points in a CSV file in a parallel fashion

Note:
    Cartopy v0.18.0 is required to successfully render maps and pass
    our internal tests.

"""

import datetime
import logging
import sys

import matplotlib
import matplotlib.animation
from tracktable.feature import annotations
from tracktable.render.render_movie import render_trajectory_movie
from tracktable.rw.load import load_trajectories
from tracktable.script_helpers import argparse, argument_groups, n_at_a_time

matplotlib.use('Agg')

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------

def _extract_typed_field_assignments(arguments,
                                     field_type):
    """Extract named field definitions from a dict of arguments

    When running this script, the user specifies named fields that
    the reader should process with arguments like
    '--real-field-column altitude 12'.  This will cause the reader
    to take column 12 in the data file, convert its contents to a
    floating-point number, and store the result in a property
    named "altitude" on each point.

    This function is a convenience: it extracts those declarations
    for a given field type (string, real, timestamp) from a dictionary
    or namespace of arguments, then returns the result as a dictionary
    that can be passed to trajectory_points_from_file().

    Arguments:
        arguments {dict}: Dictionary of parsed command-line arguments
        field_type {string}: What type of property to extract.  Must be
            'string', 'real' or 'time'.

    Returns:
        Dictionary containing { field_name: column_number } for the
        specified field type.  Dictionary will be empty if there are
        no assignments of that type.

    Raises:
        ValueError: invalid field type

    Note:
        Don't call this function directly unless you need the field
        assignments for one specific data type.  Instead, call
        `extract_field_assignments`.
    """

    if field_type not in ['string', 'real', 'time']:
        raise ValueError(('Field type ({}) must be one of "string", '
                          '"real", or "time".  Case matters').format(
                                field_type))

    arg_name = '{}_field_column'.format(field_type)
    field_assignments = dict()
    definition_list = arguments.get(arg_name, None)
    if definition_list is not None:
        if len(definition_list) > 0:
            for (field_name, column) in n_at_a_time(definition_list, 2):
                field_assignments[field_name] = int(column)

    return field_assignments

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
    argument_groups.use_argument_group("parallel", parser)

    parser.add_argument('--trail-duration',
                        help="How long should each object's trail last? (seconds)",
                        type=int,
                        default=300)

    parser.add_argument('point_data_file',
                        nargs=1,
                        help='Delimited text file containing point data')

    parser.add_argument('movie_file',
                        nargs=1,
                        help='Filename for trajectory movie')

    args = parser.parse_args()
    if args.resolution is None:
        args.resolution = [800, 600]
    if args.delimiter == 'tab':
        args.delimiter = '\t'
    if args.object_id_column is None:
        args.object_id_column = 0
    if args.timestamp_column is None:
        args.timestamp_column = 1
    if args.coordinate0 is None:
      args.coordinate0 = 2
    if args.coordinate1 is None:
      args.coordinate1 = 3

    return args

# --------------------------------------------------------------------

def extract_field_assignments(arg_dict):
    """Extract column->field assignments from arguments

    Field assignments are specified on the command line as arguments
    like '--real-field speed 12', meaning "take the contents
    of column 12 and add it to each point as a numeric field called
    speed".  This function iterates over the arguments and extracts
    all of those.

    Arguments:
        arg_dict {:obj:`dict`}: Command-line arguments to parse,
        specified as a :obj:`dict`.  To get a dictionary from the
        :obj:`Namespace` object returned by :code:`argparse.parse_args()`,
        call :code:`vars()` on the args object.

    Returns:
        Dictionary with three entries:
            'real': Dictionary mapping column names (strings) to
                    integer column IDs for real-valued fields
            'string': Dictionary mapping column names (strings) to
                    integer column IDs for string-valued fields
            'time': Dictionary mapping column names (strings) to
                    integer column IDs for timestamp-valued fields
    """

    return {
        'real': _extract_typed_field_assignments(arg_dict, 'real'),
        'string': _extract_typed_field_assignments(arg_dict, 'string'),
        'time': _extract_typed_field_assignments(arg_dict, 'time')
    }

# --------------------------------------------------------------------

def main():
    """Make a trajectory movie using several processes in parallel.

        We do very little actual work here: we ask for the command line
        arguments, compute the bounds for the frame batches and set up
        multiprocessing.  Apart from that everything happens in the other
        functions in this file.
    """
    args = parse_args()
    mapmaker_kwargs = argument_groups.extract_arguments("mapmaker", args)
    movie_kwargs = argument_groups.extract_arguments("movie_rendering", args)
    trajectory_rendering_kwargs = argument_groups.extract_arguments("trajectory_rendering", args)

    # Load all the trajectories into memory.
    point_filename = args.point_data_file[0]
    field_assignments = extract_field_assignments(vars(args))

    logger.info('Loading points and building trajectories.')
    trajectories = load_trajectories(point_filename,
        comment_character=args.comment_character,
        domain=args.domain,
        field_delimiter=args.delimiter,
        object_id_column=args.object_id_column,
        timestamp_column=args.timestamp_column,
        longitude_column=args.coordinate0,
        latitude_column=args.coordinate1,
        real_fields = field_assignments['real'],
        string_fields = field_assignments['string'],
        time_fields = field_assignments['time'],
        separation_distance = args.separation_distance, # km
        separation_time = args.separation_time, # minutes
        minimum_length = args.minimum_length, # points
        return_list=True
        )

    # Add the 'progress' annotation to all of our trajectories so
    # we have some way to color them
    trajectories = [annotations.progress(t) for t in trajectories]

    #
    # Lights! Camera! Action!
    #
    render_trajectory_movie(
        trajectories,
        backend='ffmpeg',
        parallel=True,
        filename=args.movie_file[0],
        trail_duration=datetime.timedelta(seconds=args.trail_duration),
        **trajectory_rendering_kwargs,
        **mapmaker_kwargs,
        **movie_kwargs,
        )

    return 0

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
