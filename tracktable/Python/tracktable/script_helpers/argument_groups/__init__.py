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

"""Argument groups: sets of co-occurring command line arguments

The various capabilities in Tracktable tend to have several arguments.
If we want to expose those in scripts we wind up making a lot of calls
to argparse and then spending a lot of time handling the arguments.
This file collects utilities for

(1) defining sets of arguments for later use,

(2) creating example 'response files' (text files that contain lots of
'--arg value' pairs) for the user to customize,

(3) performing initial parsing of a set of arguments to recursively
expand response files.

Here is an example of how to create and populate an argument group::

   create_argument_group('example', title='Sample Argument Group', description='This argument group exists to demonstrate what response files look like.')
   add_argument('example', [ '--string-arg', '-s' ], help='An argument with a string value', default='Foo!')
   add_argument('example', [ '--integer-arg', '-i' ], help='An integer argument', default=3)
   add_argument('example', [ '--other' ], help='A required other argument with no default', required=Tru)

"""

### Here are the functions that will be exposed to the world.

__all__ = [ 'create_argument_group', 'add_argument', 'available_argument_groups', 'use_argument_group', 'extract_arguments' ]

import importlib

from tracktable.script_helpers.argument_groups.utilities import _create_argument_group as create_argument_group
from tracktable.script_helpers.argument_groups.utilities import _add_argument as add_argument
from tracktable.script_helpers.argument_groups.utilities import _available_argument_groups as available_argument_groups
from tracktable.script_helpers.argument_groups.utilities import _use_argument_group as use_argument_group
from tracktable.script_helpers.argument_groups.utilities import _extract_arguments as extract_arguments

_ARGUMENT_GROUPS = [
    'dt_point_loader',
    'image',
    'mapmaker',
    'movie_rendering',
    'parallel',
    'trajectory_assembly',
    'trajectory_rendering',
    'trajectory_reader'
    ]

_INITIALIZED = False

if not _INITIALIZED:
    _INITIALIZED = True
    for group in _ARGUMENT_GROUPS:
        full_package_name = 'tracktable.script_helpers.argument_groups.{}'.format(group)
        arg_group = importlib.import_module(full_package_name)
        arg_group.install_group()

