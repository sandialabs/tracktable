#
# Copyright (c) 2014-2017 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
#
# Distribution and use in source and binary forms, with or without
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

"""Arguments for the trajectory reader.

Use this group as follows::

   from tracktable.script_helpers import argument_groups, argparse
   my_parser = argparse.ArgumentParser()
   argument_groups.use_group('trajectory_reader', my_parser)

Arguments:
| ``--domain NAME`` Name of domain (terrestrial, cartesian2d, cartesian3d)
|   for points to be read
"""


from tracktable.script_helpers.argument_groups import create_argument_group, add_argument

GROUP_INSTALLED = False

def install_group():
    """Create the argument group for TrajectoryReader.

    This function is called automatically when the argument_groups
    module is loaded.

    """

    global GROUP_INSTALLED
    if GROUP_INSTALLED:
        return
    else:
        GROUP_INSTALLED = True

    create_argument_group("trajectory_reader",
                          title="Trajectory Reader",
                          description="Parameters for loading trajectories from delimited text files")

    add_argument("trajectory_reader", [ '--domain' ],
                 help='Specify point domain for data in file',
                 default='terrestrial')
