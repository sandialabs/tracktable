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

"""example_point_reader - Convenience functions to configure point readers
"""

from tracktable.io.point import trajectory_point_reader, base_point_reader
from tracktable.script_helpers.argument_groups import extract_arguments
from tracktable.core import data_directory

import os.path
import sys


# ----------------------------------------------------------------------

def configure_trajectory_point_reader_from_argument_group(infile,
                                                          parsed_args,
                                                          **kwargs):
    """Configure a point reader from command-line arguments

    In the module `tracktable.script_helpers.argument_groups`, we define
    related sets of command-line arguments in blocks called *argument
    groups*.  This function takes the argument namespace returned by
    argparse.parse_args(), extracts the relevant parameters (being mindful
    of defaults), and passes them to configure_trajectory_point_reader()
    along with anything else you might want to supply.

    Arguments that you pass in will override those in the command-line
    arguments.

    NOTE: This is all boring bookkeeping code.  There's nothing interesting
    going on, just conversion from one format (command-line arguments) to 
    the dicts and parameters that our functions expect.  I wish it could
    be cleaner.

    Arguments:
        parsed_args {namespace}: Result of argparse.parse_args() call

    Keyword arguments:
        All of the arguments that configure_trajectory_point_reader()
        takes are valid here.

    Returns:
        Brand new tracktable.domain.<domain>.trajectory_point_reader
        with all of the arguments applied to its configuration.
    """


    reader_args = vars(extract_arguments('delimited_text_point_reader', parsed_args))
    user_args = dict(kwargs)

    # Rename a few things in the parsed command-line arguments so that we
    # can easily overwrite them with whatever the user passed in.  We do
    # this for all domains (terrestrial, cartesian2d, cartesian3d) without
    # checking because configure_trajectory_point_reader() will pick
    # the ones it wants.
    if reader_args['coordinate0'] is not None:
        reader_args['longitude_column'] = reader_args['coordinate0']
        reader_args['x_column'] = reader_args['coordinate0']
    if reader_args['coordinate1'] is not None:
        reader_args['latitude_column'] = reader_args['coordinate1']
        reader_args['y_column'] = reader_args['coordinate1']
    if reader_args['coordinate2'] is not None:
        reader_args['z_column'] = reader_args['coordinate2']

    del reader_args['coordinate0']
    del reader_args['coordinate1']
    del reader_args['coordinate2']

    # Filter out any remaining None entries
    copy_dict = dict()
    for (key, value) in reader_args:
        if value is not None:
            copy_dict[key] = value
    reader_args = copy_dict

    # Grab the field specifications and convert them into the map format that
    # configure_trajectory_point_reader wants
    if 'string_field_column' in reader_args:
        string_fields = dict()
        if len(reader_args['string_field_column']) > 0:     
            for (field, column) in group(reader_args['string_field_column'], 2):
                string_fields[field] = column
            user_args['string_fields'] = string_fields
        del reader_args['string_field_column']

    if 'real_field_column' in reader_args:
        real_fields = dict()
        if len(reader_args['real_field_column']) > 0:     
            for (field, column) in group(reader_args['real_field_column'], 2):
                real_fields[field] = column
            user_args['real_fields'] = real_fields
        del reader_args['real_field_column']
 
     if 'time_field_column' in reader_args:
        time_fields = dict()
        if len(reader_args['time_field_column']) > 0:     
            for (field, column) in group(reader_args['time_field_column'], 2):
                time_fields[field] = column
            user_args['time_fields'] = time_fields
        del reader_args['time_field_column']


    # That's all the command-line arguments processed.  Now we take whatever's 
    # left, add in anything the user supplied, and go get a reader.
    final_args = reader_args
    final_args.update(user_args)
    return configure_trajectory_point_reader(infile, **final_args)


# ----------------------------------------------------------------------


# ---------------------------------------------------------------------


def example_point_reader():
    """Example of how to create and read from a point reader

    This function is a minimal, self-contained example of how to use 
    a trajectory point reader to read from a file.  We set all the
    options on the point reader even though some of them are the same
    as the defaults.

    Note further that some properties such as aircraft type don't change
    from one point to the next.  Those should be set on the trajectory,
    not the individual points, but that's beyond the scope of this example.

    No arguments; no return value.
    """

    real_columns = {
        'speed': 4,
        'heading': 5,
        'altitude': 6
    }
    string_columns = {'aircraft_type': 14}
    time_columns = {
        'scheduled_departure_time': 23, 
        'actual_departure_time': 24
        }
    print("Opening sample data file.")
    sample_filename = os.path.join(data_directory(), 'SampleASDI.csv')
    with open(sample_filename, 'rb') as infile:
        print("Instantiating reader.")
        reader = trajectory_point_reader(
            infile,
            domain='terrestrial',
            delimiter=',',
            comment_character='#',
            object_id_column=0,
            timestamp_column=1,
            longitude_column=2,
            latitude_column=3,
            real_fields=real_columns,
            string_fields=string_columns,
            time_fields=time_columns
           )

        # We iterate over the contents of the reader to get the points that it
        # finds.
        num_points_to_print = 20
        print("Iterating over points.")
        for (i, point) in enumerate(reader):
            if i > num_points_to_print:
                print("Stopping after reading {} points.".format(num_points_to_print))
                return 0
            else:
                print("Read trajectory point: {}".format(str(point)))



if __name__ == '__main__':
    sys.exit(example_point_reader())
