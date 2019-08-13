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

from tracktable.domain import all_domains as ALL_DOMAINS
import importlib
import itertools

def configure_point_reader(infile, **kwargs):
  """
  Purpose: Set up a trajectory point reader for terrestrial points
  
  Args:
    infile: An open file or file-like object containing the input
    kwargs: A dictionary of argument names and values. Arguments can be:
            delimiter:         A single character that deparates fields in the input
            comment_character: Lines where this character is the first 
                               non-whitespace character will be ignored.
            object_id, timestamp, coordinate0, coordinate1, coordinate2:
                                column numbers that contain the object_id, timestamp, longitude,
                                latitude, and z-order respectively
            The above arguments are required.Can optionally contain any additional columns and 
            column numbers such as altitude, airline, etc as long as the value is 
            string, integer, or timestamp.
  Returns: A ready-to-use point reader. In order to actually retrieve the points, 
           iterate over the contents of the 'reader'.
            
    Example:
      field_map = dict()
      field_map["object_id"] = 0
      field_map["timestamp"] = 1
      field_map['coordinate0'] = 2
      field_map['coordinate1'] = 3
      field_map['coordinate2'] = None
      field_map["altitude"] = 4
      field_map["speed"] = 5
      field_map["airline_name"] = 6
      
    TrajectoryPoint has 'object_id' and 'timestamp' as class members
    accessed with 'my_point.object_id' and 'my_point.timestamp'.  All
    other named properties are accessed as
    'my_point.properties["prop_name"]'.
    
  """
  domain = kwargs['domain']
  if domain.lower() not in ALL_DOMAINS:
    raise KeyError("Domain '{}' is not in list of installed domains ({}).".format(domain, ', '.join(ALL_DOMAINS)))
  else:
    domain_to_import = 'tracktable.domain.{}'.format(domain.lower())
    domain_module = importlib.import_module(domain_to_import)
  
  reader = domain_module.TrajectoryPointReader()
  reader.input = infile
  reader.comment_character = kwargs['comment_character']
  reader.field_delimiter = kwargs['delimiter']
  
  if kwargs['object_id'] is not None:
    reader.object_id_column = kwargs['object_id']
  if kwargs['timestamp'] is not None:
    reader.timestamp_column = kwargs['timestamp']
  if kwargs['coordinate0'] is not None:
    reader.coordinates[0] = int(kwargs['coordinate0'])
  if kwargs['coordinate1'] is not None:
    reader.coordinates[1] = int(kwargs['coordinate1'])
  if kwargs['coordinate2'] is not None:
    reader.coordinates[2] = int(kwargs['coordinate2'])
  if (kwargs['string_field_column'] is not None and
    len(kwargs['string_field_column']) > 0):
    for (field, column) in group(kwargs['string_field_column'], 2):
      reader.string_fields[field] = column

  if (kwargs['time_field_column'] is not None and
    len(kwargs['time_field_column']) > 0):
    for (field, column) in group(kwargs['time_field_column'], 2):
      reader.time_fields[field] = column

  if (kwargs['numeric_field_column'] is not None and
    len(kwargs['numeric_field_column']) > 0):
    for (field, column) in group(kwargs['numeric_field_column'], 2):
      reader.numeric_fields[field] = column
  return reader


#-----------------------------------------------------------------------
# Utility function for reading groups of elements from an iterable

def group(iterable, howmany, fillvalue=None):
  # Collect data into fixed length chunks or blocks
  # group('ABCDEFG', 3, 'x') --> ABC DEF Gxx
  args = [iter(iterable)] * howmany
  return izip_longest(fillvalue=fillvalue, *args)
