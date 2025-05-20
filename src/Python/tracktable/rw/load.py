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

"""tracktable.rw.load: Load in trajectories or trajectory points from a file

This file will intelligently load in trajectory or trajectory point files for
supported file types (.csv, .tsv, .traj). This includes automatic trajectory assembly if
the file being loaded is a .csv or .tsv file as well as automatically utilizing the correct
domain readers so points or trajectories are correctly associated with the
Terrestrial or Cartesian domains.
"""

import logging
from datetime import timedelta
import os

from tracktable.applications.assemble_trajectories import \
    AssembleTrajectoryFromPoints
from tracktable.domain import domain_module_from_name

try:
    from tqdm import tqdm
    tqdm_installed = True
except ImportError as e:
    tqdm_installed = False

logger = logging.getLogger(__name__)

def load_trajectories(infile,
        comment_character="#",
        domain='terrestrial',
        field_delimiter=',',
        object_id_column=0,
        timestamp_column=1,
        longitude_column=2,
        latitude_column=3,
        x_column=2,
        y_column=3,
        z_column=4,
        real_fields = dict(), # {'altitude': 4}
        string_fields = dict(), # {'vessel-name': 7}
        time_fields = dict(), # {'eta': 17}
        separation_distance = None, # km
        separation_time = 30, # minutes
        minimum_length=2, # points
        return_trajectory_points = False,
        return_list=True
        ):

    """Load trajectories or trajectory points from .csv, .tsv and .traj files

    Arguments:
        infile (file-like object): File path for trajectory data

    Keyword arguments:
        comment_character (character): Any row where this is the first
            non-whitespace character will be ignored. (default: '#')
        delimiter (character): What character separates columns?
            (default: ',')
        domain (str): Which point domain will the points belong to?
            (default: 'terrestrial')
        object_id_column (int): Which column contains the object ID
            (default: 0)
        timestamp_column (int): Which column contains the timestamp
            (default: 1)
        longitude_column (int): Which column contains the longitude for
            each point? (default: 2, assumes terrestrial domain)
        latitude_column (int): Which column contains the latitude for
            each point? (default: 3, assumes terrestrial domain)
        x_column (int): Which column contains the X coordinate for
            each point? (default: 2, assumes cartesian2d or cartesian3d)
        y_column (int): Which column contains the Y coordinate for
            each point? (default: 3, assumes cartesian2d or cartesian3d)
        z_column (int): Which column contains the X coordinate for
            each point? (default: 4, assumes cartesian3d)
        string_fields (dict, int -> string): Columns in the input that
            should be attached to each point as a string. The keys
            in this dictionary are column numbers. Their corresponding
            values are the name of the field that will be added to
            the point's properties. (default: empty)
        real_fields (dict, int -> string): Columns in the input that
            should be attached to each point as a real number. The keys
            in this dictionary are column numbers. Their corresponding
            values are the name of the field that will be added to
            the point's properties. (default: empty)
        time_fields (dict, int -> string): Columns in the input that
            should be attached to each point as a timestamp. The keys
            in this dictionary are column numbers. Their corresponding
            values are the name of the field that will be added to
            the point's properties. The timestamps must be in the same
            format as for the point as a whole, namely `YYYY-mm-dd HH:MM:SS`.
            (default: empty)
        separation_distance (int): Distance in KM between points signifying the need
            to generate a new trajectory. (default: 10)
        separation_time (int): Time in minutes between seperated points signifying the need
            to generate a new trajectory. (20)
        return_trajectory_points (boolean): When loading a .csv or .tsv file return the points in the
            file and don't generate trajectories. When loading a .traj return a list of lists of the points
            that make up the given trajectory for all trajectories in the file. (default: False)
        return_list (boolean): When returning the reader or assembler object have the loader
            automatically pull all of the yielded trajectories into a list for further processing. (default: False)

    Returns:
        List of trajectory points or trajectories depending on input file and params.

    Raises:
        IOError: Unsupported filetype
        ValueError: Unsupported domain or comment character
    """

    if len(comment_character) != 1:
        raise ValueError('Unsupported comment character `{}`, comment character must be 1 character long.'.format(comment_character))

    domain_module = domain_module_from_name(domain)

    if infile.endswith('.traj'):
        # Read in the trajectories from the traj file
        reader = domain_module.TrajectoryReader()
        reader.input = open(infile, 'r')

        if return_list:
            if tqdm_installed:
                trajectories = list(tqdm(reader, desc="Loading Trajectories", unit=" trajectory"))
            else:
                trajectories = list(reader)
        else:
            trajectories = reader

        if return_trajectory_points:
            trajectory_points = []
            if tqdm_installed:
                for trajectory in tqdm(trajectories, desc="Decomposing Trajectories Into Trajectory Points", unit=" trajectory"):
                    point_list = []
                    for point in trajectory:
                        point_list.append(point)
                    trajectory_points.append(point_list)
            else:
                for trajectory in trajectories:
                    point_list = []
                    for point in trajectory:
                        point_list.append(point)
                    trajectory_points.append(point_list)
            return trajectory_points
        else:
            return trajectories
    elif infile.endswith('.csv') or infile.endswith('.tsv'):
        # Read in the points from the CSV file
        reader = domain_module.TrajectoryPointReader()
        reader.input = open(infile, 'r')
        reader.comment_character = comment_character
        if infile.endswith('.tsv') and field_delimiter != '\t':
            field_delimiter = '\t'
        reader.field_delimiter = field_delimiter
        reader.object_id_column = object_id_column
        reader.timestamp_column = timestamp_column
        if domain == 'terrestrial':
            reader.coordinates[0] = longitude_column
            reader.coordinates[1] = latitude_column
        elif domain in ['cartesian2d', 'cartesian3d']:
            reader.coordinates[0] = x_column
            reader.coordinates[1] = y_column
            if domain == 'cartesian3d':
                reader.coordinates[2] = z_column
        else:
            raise ValueError('Unsupported domain: `{}`, supported domains are terrestrial, cartesian2d and cartesian3d'.format(domain))

        for name, column_num in real_fields.items():
            reader.set_real_field_column(name, column_num)

        for name, column_num in string_fields.items():
            reader.set_string_field_column(name, column_num)

        for name, column_num in time_fields.items():
            reader.set_time_field_column(name, column_num)

        if return_trajectory_points:
            if return_list:
                if tqdm_installed:
                    trajectory_points = list(tqdm(reader, desc="Loading Trajectory Points", unit=" point"))
                else:
                    trajectory_points = list(reader)
            else:
                trajectory_points = reader
            return trajectory_points
        else:
            # Assemble the points into trajectories
            assembler = AssembleTrajectoryFromPoints()
            assembler.input = reader
            assembler.separation_distance = separation_distance
            assembler.separation_time = timedelta(minutes=separation_time)
            assembler.minimum_length = minimum_length
            if return_list:
                if tqdm_installed:
                    trajectories = list(tqdm(assembler.trajectories(), desc="Loading Trajectory Points And Assembling Points Into Trajectories", unit=" trajectory"))
                else:
                    trajectories = list(assembler.trajectories())
            else:
                trajectories = assembler
            return trajectories
    else:
        filename, file_extension = os.path.splitext(infile)
        logger.error("Unsupported file type: `{}`, supported file types are .csv, .tsv and .traj.".format(file_extension))
        raise IOError
