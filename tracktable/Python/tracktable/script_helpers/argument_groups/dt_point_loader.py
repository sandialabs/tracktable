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

"""Arguments for the delimited text point reader.

Use this group as follows::

   from tracktable.script_helpers import argument_groups, argparse
   my_parser = argparse.ArgumentParser()
   argument_groups.use_group('dt_point_loader', my_parser)

Arguments:

| ``--delimiter CHARACTER``
|   Single character delimiter for fields
|
| ``--comment-character CHARACTER``
|   Single character indicating 'skip this line' when found as the first non-whitespace character on a line
|
| ``--domain NAME`` Name of domain (terrestrial, cartesian2d, cartesian3d)
|   for points to be read
|
| ``--longitude-column COL``
|   Populate longitude with the contents of column COL
|
| ``--latitude-column COL``
|   Populate latitude with the contents of column COL
|
| ``--x-column COL``
|   Populate X coordinate with the contents of column COL
|
| ``--y-column COL``
|   Populate Y coordinate with the contents of column COL
|
| ``--string-field-column NAME COL``
|   Populate field NAME with column COL as a string
|
| ``--numeric-field-column NAME COL``
|   Populate field NAME with column COL as a number
|
| ``--timestamp-field-column NAME COL``
|   Populate field NAME with column COL as a timestamp.  Not the same as the timestamp column.
|
| ``--object-id-column COL``
|   Populate the point's object ID with column COL.  Only applies to trajectory points.
|
| ``--timestamp-column COL``
|   Populate the point's timestamp with column C.  Only applies to trajectory points.



"""


from tracktable.script_helpers.argument_groups import create_argument_group, add_argument

GROUP_INSTALLED = False

def install_group():
    """Create the argument group for DelimitedTextPointReader.

    This function is called automatically when the argument_groups
    module is loaded.

    """

    global GROUP_INSTALLED
    if GROUP_INSTALLED:
        return
    else:
        GROUP_INSTALLED = True

    create_argument_group("delimited_text_point_reader",
                          title="Delimited Text Point Reader",
                          description="Parameters for parsing points from delimited text files")

    add_argument("delimited_text_point_reader", [ '--delimiter' ],
                 help='Character that separates fields in the input file.  Use any single character.  The string "tab" will be interpreted as the tab character.',
                 default=',' )

    add_argument("delimited_text_point_reader", [ '--comment-character' ],
                 help='Character that indicates comment lines in the input file.  Lines where this is the first non-whitespace character will be ignored.',
                 default='#' )

    add_argument("delimited_text_point_reader", [ '--domain' ],
                 help='Specify point domain for data in file',
                 default='terrestrial')

#    add_argument("delimited_text_point_reader", [ '--coordinate-column' ],
#                 nargs=2,
#                 action='append',
#                 help='Populate coordinate X using the contents of column Y.  You probably want to use "--x-column", "--y-column", "--longitude-column" and "--latitude-column" instead.')

    add_argument("delimited_text_point_reader", [ '--longitude-column' ],
                 type=int,
                 dest='coordinate0',
                 help="Use column N in the file for longitude values")

    add_argument("delimited_text_point_reader", [ '--latitude-column' ],
                 type=int,
                 dest='coordinate1',
                 help="Use column N in the file for latitude values")

    add_argument("delimited_text_point_reader", [ '--x-column' ],
                 type=int,
                 dest='coordinate0',
                 help="Use column N in the file for X coordinate values")

    add_argument("delimited_text_point_reader", [ '--y-column' ],
                 type=int,
                 dest='coordinate1',
                 help="Use column N in the file for Y values")

    add_argument("delimited_text_point_reader", [ '--z-column' ],
                 type=int,
                 dest='coordinate2',
                 help="Use column N in the file for Y values")

    add_argument("delimited_text_point_reader", [ '--string-field-column' ],
                 nargs=2,
                 action='append',
                 help='Populate field X using the contents of column Y as a string')

    add_argument("delimited_text_point_reader", [ '--numeric-field-column' ],
                 nargs=2,
                 action='append',
                 help='Populate field X using the contents of column Y as a number')

    add_argument("delimited_text_point_reader", [ '--time-field-column' ],
                 nargs=2,
                 action='append',
                 help='Populate field X using the contents of column Y as a timestamp')

    add_argument("delimited_text_point_reader", [ '--object-id-column' ],
                 help='Column in input files containing the ID associated with each moving object',
                 default=None,
                 type=int )

    add_argument("delimited_text_point_reader", [ '--timestamp-column' ],
                 help='Column in input file containing the timestamp for each point',
                 default=None,
                 type=int )
