#
# Copyright (c) 2014-2022 National Technology and Engineering
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
import tracktable.domain
from tracktable.applications.assemble_trajectories import \
    AssembleTrajectoryFromPoints
from tracktable.feature import annotations
from tracktable.render.render_movie import render_trajectory_movie
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

def assemble_trajectories(point_source,
                          separation_distance=1000,
                          separation_time=datetime.timedelta(hours=24),
                          minimum_length=2):
    """Assemble a sequence of points into trajectories

    This function will instantiate and configure a `tracktable.analysis.
    assemble_trajectories.AssembleTrajectoryFromPoints` to convert a sequence
    of points into a sequence of trajectories.

    You must specify an iterable of points.  You can also specify
    parameters that determine when a series of points with the
    same object ID will be cut into separate trajectories and the
    minimum number of points a trajectory must have in order to
    be worthy of consideration.

    Note:
        This function does not actually build the trajectories.  It
        only sets up the pipeline to generate them.  Assembly does
        not happen until you start to pull elements from the iterable
        that gets returned.

    Arguments:
        point_source {iterable} -- Sequence of points to assemble

    Keyword Arguments:
        separation_distance {float} -- Points with the same object ID
            that are at least this far apart will be used as the end
            of one trajectory and the beginning of the next.  Defaults
            to 1000 (km in terrestrial domain, units in cartesian2d).
        separation_time {datetime.timedelta} -- Points with the same
            object ID that have timestamps at least this far apart will
            be used as the end of one trajectory and the beginning of
            the next.  Defaults to 24 hours.
        minimum_length {integer} -- Trajectories with fewer than this
            many points will be discarded.  (default: 2)
    """

    assembler = AssembleTrajectoryFromPoints()
    assembler.input = point_source
    assembler.separation_distance = separation_distance
    assembler.separation_time = separation_time
    assembler.minimum_length = minimum_length

    return assembler

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

def trajectories_from_point_file(infile,
                                 object_id_column=0,
                                 timestamp_column=1,
                                 coordinate0_column=2,
                                 coordinate1_column=3,
                                 string_fields=None,
                                 real_fields=None,
                                 time_fields=None,
                                 comment_character='#',
                                 field_delimiter=',',
                                 separation_distance=None,
                                 separation_time=None,
                                 minimum_length=2,
                                 domain='cartesian2d'):
    """Load points from a file and assemble them into trajectories

    This function encapsulates the pipeline that loads points from a
    delimited text file, turns them into TrajectoryPoints, then
    assembles trajectories from those points.

    Note that timestamps must have the format "YYYY-mm-dd HH:MM:SS".
    For example, December 10, 2001 at 12:34:56 PM would be
    "2001-12-10 12:34:56".

    Arguments:
        infile {file-like object} -- Input source for points

    Keyword Arguments:
        object_id_column {integer} -- Column in file containing
            object ID (default: 0)
        timestamp_column {integer} -- Column in file containing
            timestamp (default: 1)
        coordinate0_column {integer} -- Column in file containing
            longitude or X coordinate (default: 2)
        coordinate1_column {integer} -- Column in file containing
            latitude or Y coordinate (default: 3)
        string_fields {dict} -- Mapping from field name to column
            number for columns containing string metadata (default: None)
        real_fields {dict} -- Mapping from field name to column
            number for columns containing numeric metadata (default: None)
        time_fields {dict} -- Mapping from field name to column number
            for columns containing timestamp metadata (default: None)
        comment_character {str} -- Lines in the input file that start
            with this character will be ignored (default: '#')
        field_delimiter {str} -- This character will be used as the
            separator between fields in a file (default: ',')
        domain {str} -- Point domain for data to be rendered.  Must be
            either 'terrestrial' or 'cartesian2d'.  (default: 'terrestrial')

    Returns:
        Iterable of trajectories.

    Raises:
        ValueError: comment character string or field delimiter string are
            not 1 character long, or domain is not 'terrestrial' or
            'cartesian2d'
    """

    if len(comment_character) != 1:
        raise ValueError(('trajectories_from_point_file: Comment character '
                          'string must be 1 character long.  You supplied'
                          '"{}".'.format(comment_character)))
    if len(field_delimiter) != 1:
        raise ValueError(('trajectories_from_point_file: Field delimiter '
                          'string must be 1 character long.  You supplied '
                          '"{}".').format(field_delimiter))
    if domain not in ['terrestrial', 'cartesian2d']:
        raise ValueError(('trajectories_from_point_file: Point domain must '
                          'be either "terrestrial" or "cartesian2d".  You '
                          'supplied "{}".').format(domain))

    point_source = trajectory_points_from_file(
                          infile,
                          object_id_column,
                          timestamp_column,
                          coordinate0_column,
                          coordinate1_column,
                          string_fields=string_fields,
                          real_fields=real_fields,
                          time_fields=time_fields,
                          comment_character=comment_character,
                          field_delimiter=field_delimiter,
                          domain=domain)

    trajectory_source = assemble_trajectories(
            point_source,
            separation_distance=separation_distance,
            separation_time=separation_time,
            minimum_length=minimum_length)

    return trajectory_source

# ---------------------------------------------------------------------

def trajectory_points_from_file(
      infile,
      object_id_column,
      timestamp_column,
      coordinate0_column,
      coordinate1_column,
      string_fields=None,
      real_fields=None,
      time_fields=None,
      comment_character='#',
      field_delimiter=',',
      domain='terrestrial'
      ):
    """points_from_file: Load a list of points from a delimited text file

    Use tracktable.domain.<domain>.BasePointReader to read points from a file.
    Results are returned as an iterable.

    Note:
        You can only iterate over the resulting point sequence once.  If you
        need to do more than that, save the points in a list:

    >>> all_points = list(points_from_file(infile, 2, 3))

    Note:
        The function 'extract_field_assignments_from_arguments' will help
        you pull out rela_fields, string_fields, and time_fields from a
        set of parsed arguments.

    Arguments:
        infile {file-like object}: Data source for points
        object_id_column {int}: Column in file containing object ID
        timestamp_column {int}: Column in file containing timestamps for points
        coordinate0_column {int}: Column in file for x/longitude
        coordinate1_column {int}: Column in file for y/latitude

    Keyword Arguments:
        string_fields {dict, string->int}: Columns in the input file that we
            want to add to points as string properties.  The keys in this
            dict should be the name of the field and the values should be the
            integer column IDs (first column is 0).
        real_fields {dict, string->int}: Columns in the input file that we
            want to add to points as real-valued properties.  The keys in this
            dict should be the name of the field and the values should be the
            integer column IDs (first column is 0).
        time_fields {dict, string->int}: Columns in the input file that we
            want to add to points as timestamp-valued properties.  The keys in
            this dict should be the name of the field and the values should be
            the integer column IDs (first column is 0).
        comment_character {single-character string}: Ignore lines in the input
            that have this as the first non-whitespace character.  Defaults to
            '#'.
        field_delimiter {single-character string}: This character is the field
            separator in the input and must be escaped inside strings.
            Defaults to ','.
        domain {(}string naming point domain}: Must be either 'terrestrial' or
            'cartesian2d' depending on whether your points are
            longitude/latitude or arbitrary Cartesian coordinates.  Defaults
            to 'terrestrial'.

    Returns:
        Iterable of tracktable.domain.<domain>.TrajectoryPoints.
    """
    domain_module = tracktable.domain.domain_module_from_name(domain)
    reader_type = getattr(domain_module, 'TrajectoryPointReader')
    reader = reader_type()
    reader.input = infile
    reader.object_id_column = object_id_column
    reader.timestamp_column = timestamp_column
    reader.coordinates[0] = coordinate0_column
    reader.coordinates[1] = coordinate1_column
    reader.comment_character = comment_character
    reader.field_delimiter = field_delimiter

    return reader

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

    with open(point_filename, 'r') as infile:

        trajectories = list(
            trajectories_from_point_file(
                infile,
                object_id_column=args.object_id_column,
                timestamp_column=args.timestamp_column,
                coordinate0_column=args.coordinate0,
                coordinate1_column=args.coordinate1,
                string_fields=field_assignments['string'],
                real_fields=field_assignments['real'],
                time_fields=field_assignments['time'],
                comment_character=args.comment_character,
                field_delimiter=args.delimiter,
                separation_distance=args.separation_distance,
                separation_time=datetime.timedelta(minutes=args.separation_time),
                minimum_length=args.minimum_length,
                domain=args.domain)
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
