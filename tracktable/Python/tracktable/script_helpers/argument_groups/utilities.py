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

"""INTERNAL: Implementations for manipulating argument groups

"""

from __future__ import print_function

import string
import sys
import textwrap

__all__ = [ '_create_argument_group', '_add_argument', '_available_argument_groups', '_use_argument_group', '_extract_arguments' ]

_ARGUMENT_GROUPS = {}

def _create_argument_group(group_name,
                           title=None,
                           description=None):
    """Register a new, empty group of arguments

    Arguments to configure different capabilities tend to come in
    groups.  For example, movie-making includes frames per second,
    movie duration, encoder type and encoder options.  This function
    lets you create such subject-related groups.

    Note that this function only *creates* the group.  You still have to
    populate it using register_argument (q.v.).

    Args:
       group_name (string): Name of the group you want to add.
       title (string): Title of the group.  Not required but highly recommended.
       description (string): Description / help text.  Not required but highly recommended.

    Returns:
       The name of the group just added.

    """

    global _ARGUMENT_GROUPS
    group = _ARGUMENT_GROUPS.get(group_name, None)
    if group is None:
        group = { 'name': group_name, 'args': dict() }
        _ARGUMENT_GROUPS[group_name] = group

    group['title'] = title
    group['description'] = description

    return group_name

# ----------------------------------------------------------------------

def _add_argument(group_name,
                  option_names,
                  **kwargs):

    """Add a single command-line argument to a group.

    Args:
       group_name (string):  Name for conceptual group of arguments (such as 'movie' for movie-making parameters)
       option_names (list):  A list of command-line options that can be used to specify this argument (such as [ '--frame-rate', '-f' ])

       All other arguments will be passed straight to argparse.add_argument() when this argument group is requested.

    Returns:
       The name of the argument just added.

    Raises:
       KeyError: the specified argument group does not exist.

    Examples:

       >>> add_argument('movies', [ '--frame-rate', '-f' ],
                        help='Desired frame rate for movie',
                        type=int,
                        default=30)
       '--frame-rate'

       >>> add_argument('nonexistent_group', [ '--foo', '-g' ])
       XXX INSERT ERROR MESSAGES

    """

    global _ARGUMENT_GROUPS

    group = _ARGUMENT_GROUPS[group_name]

    main_name = option_names[0]
    group['args'][main_name] = { 'names': option_names, 'info': kwargs }

    return main_name

# ----------------------------------------------------------------------

def _use_argument_group(group_name, parser):
    """Add a group of arguments to a parser.

    Args:
       group_name: Name of the desired group of arguments
       parser:      An instance of argparse.ArgumentParser

    Returns:
       Parser after the arguments have been added

    Raises:
       KeyError: the desired argument group does not exist

    Once you have registered one or more arguments in a group, call
    use_arguments to add them to a parser.  They will be added to a
    group in that parser.

    Examples:
    XXX TODO
    """

    global _ARGUMENT_GROUPS
    arg_group = _ARGUMENT_GROUPS[group_name]

    subparser = parser.add_argument_group(title=arg_group['title'],
                                          description=arg_group['description'])

    for (main_name, info) in arg_group['args'].items():
        arg_names = info['names']
        arg_parameters = info['info']
        subparser.add_argument(*arg_names, **arg_parameters)

    return parser


# ----------------------------------------------------------------------

def _available_argument_groups():
    """Return a list of all available argument groups.

    Args:
      None

    Returns:
      A list of strings, each the name of a registered argument group
    """

    global _ARGUMENT_GROUPS
    return _ARGUMENT_GROUPS.keys()

# ----------------------------------------------------------------------

def _extract_arguments(group_name, parsed_args, switch_character='-'):
    """Extract a group of arguments from a Namespace into a dict

    Argument groups make it easy to include a batch of options all at
    once.  This function is the next step: after you've used
    argparse.ArgumentParser to parse a set of command-line arguments,
    you use extract_arguments to extract a group of arguments
    into a dict.  This dict can then be passed on to a function as a
    set of keyword arguments.

    The difference between this and calling vals() on the namespace
    returned by parse_args() is that this pulls out just the arguments
    associated with the specified group.

    Args:
       group_name:       A string naming the group to extract
       parsed_args:      A Namespace object returned from argparse.ArgumentParser.parse_args()
       switch_character: Character used to prefix switches, e.g. '-' for options like '--foo' and '-f'

    Returns:
       A dict() whose names are the destinations (*) associated with
       the command-line arguments and whose values are the values from
       the command line

    Raises:
       KeyError: The desired argument group doesn't exist

    """


    result = {}

    global _ARGUMENT_GROUPS
    arg_group = _ARGUMENT_GROUPS.get(group_name, None)
    if arg_group is None:
        raise KeyError("extract_arguments: No such group '{}'.".format(group_name))

    if isinstance(parsed_args, dict):
        parsed_values = dict(parsed_args)
    else:
        parsed_values = vars(parsed_args)

    for arg in arg_group['args'].values():
        destvar_name = _arg_to_destvar(arg)
        if destvar_name not in parsed_values:
            raise KeyError("WARNING: extract_arguments: Destination '{}' not found for argument '{}' in group '{}'\n".format(destvar_name, arg['names'][0], group_name))
            continue
        result[destvar_name] = parsed_values[destvar_name]

    return result

# ----------------------------------------------------------------------

def _arg_to_destvar(arg, switch_character='-'):
    """INTERNAL: Look up the destination variable an argument writes into

    The argparse library allows you to specify the name of the
    property into which an argument's value will be stored.  This
    function abstracts that away.  When you call it you will get back
    our best guess at the property that will contain values for the
    specified argument.

    Args:
      arg (dict): Entry from argument group
      switch_character (character): Optional switch character, defaults to '-'

    Returns:
      String containing name of property for argument
    """

    arg_info = arg['info']

    if 'dest' in arg_info:
        return arg_info['dest']
    else:
        original_name = arg['names'][0]
        destvar_name = original_name.lstrip(switch_character).replace('-', '_')
        return destvar_name

