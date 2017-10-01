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

"""Customized version of argparse with Response Files

Regular argparse has some support for response files but they're
pretty bare.  There's nowhere to put comments, for example.  This
subclass enhances that.  It adds a few capabilities:

* Argument Groups - Use a group of thematically-related arguments all
  at once instead of having to insert them one by one

* Response Files - Response files can have comments in them.  They
  will be automatically parsed from the command line.

* --write-response-file - Like --help, this will write an example
  response file and then exit.
"""

from __future__ import absolute_import

__all__ = [ 'ArgumentParser' ]

import argparse as standard_argparse
from argparse import SUPPRESS, FileType, Action, ArgumentTypeError, ArgumentError, HelpFormatter, RawDescriptionHelpFormatter, RawTextHelpFormatter, ArgumentDefaultsHelpFormatter

from gettext import gettext as _
import os
import shlex
import sys
import textwrap

POSITIONAL_ARGUMENT = 'Positional Argument'

ARGUMENTS_TO_IGNORE = [ '-h', '--help', '--write-response-file' ]

class ArgumentParser(standard_argparse.ArgumentParser):
    """Enhanced version of the standard Python ArgumentParser.

    Attributes:
      add_response_file (boolean): Add the '--write-response-file' option.
      comment_character (string): This character indicates that a line in
        a response file should be ignored.

    ORIGINAL ARGPARSE DOCUMENTATION:

    Object for parsing command line strings into Python objects.

    Keyword Arguments:
        - prog -- The name of the program (default: sys.argv[0])
        - usage -- A usage message (default: auto-generated from arguments)
        - description -- A description of what the program does
        - epilog -- Text following the argument descriptions
        - parents -- Parsers whose arguments should be copied into this one
        - formatter_class -- HelpFormatter class for printing help messages
        - prefix_chars -- Characters that prefix optional arguments
        - fromfile_prefix_chars -- Characters that prefix files containing
            additional arguments
        - argument_default -- The default value for all arguments
        - conflict_handler -- String indicating how to handle conflicts
        - add_help -- Add a -h/-help option

    """

    def __init__(self,
                 add_response_file=True,
                 fromfile_prefix_chars='@',
                 prefix_chars='-',
                 comment_character='#',
                 conflict_handler='resolve',
                 **kwargs):
        """Initialize custom argument parser

        Initialize our version of ArgumentParser that can handle
        response files with comments.  The only real difference from
        the parent class's constructor is that we include an argument
        for the comment character.

        Kwargs:
          add_response_file (boolean): Whether to include the argument
             for --write-response-file.  Defaults to true.
          fromfile_prefix_chars (string): Characters that will indicate
             a response file on the command line instead of an argument.
          prefix_chars (string): Characters that will indicate an argument
             name instead of a value or a positional argument.
          comment_character (string): Character in response file that
             will indicate that a line is a comment.
          kwargs: Any other arguments will be passed on to the regular
             ArgParse constructor
        """

        super(ArgumentParser, self).__init__(
            fromfile_prefix_chars=fromfile_prefix_chars,
            prefix_chars=prefix_chars,
            conflict_handler=conflict_handler,
            **kwargs)

        self._suppressed_arguments = [ 'help', 'write-response-file' ]
        self.add_response_file = add_response_file
        self.comment_character = comment_character

        self.register('action', 'write_response_file', _WriteResponseFile)

        default_prefix = '-' if '-' in prefix_chars else prefix_chars[0]
        if self.add_response_file:
            self.add_argument(
                default_prefix*2+'write-response-file',
                action='write_response_file',
                default=SUPPRESS,
                help=_('Write a sample response file to stdout and exit'))

    def _get_kwargs(self):
        """Pretty method for __repr__"""

        names = [ 'add_response_file' ]
        local_args = [ (name, getattr(self, name)) for name in names ]
        return local_args + super(ArgumentParser, self)._get_kwargs()

    def write_response_file(self, out=sys.stdout):
        """Write an example response file

        Write a response file with every line commented out to the
        specified file-like object.  It will be populated with every
        argument (positional and optional) that has been configured
        for this parser including descent into any argument groups.
        The '--help' and '--write-response-file' arguments will be
        omitted.

        Args:
           out: File-like object for output

        Returns:
           None
        """

        writer = _ResponseFileWriter(out)

        if self.prog not in (None, SUPPRESS):
            writer.write_line('Response file for {}'.format(self.prog))
        else:
            writer.write_line('Response file for unnamed program')

        writer.write_line('')
        writer.write_action_group(self)

    def _read_args_from_files(self, arg_strings, file_depth=0):
        """Recursively expand arguments that refer to response files

        Internal method.  Given a list of arguments, traverse it and
        look for strings that indicate response files.  Load those
        response files and repeat the process with their contents.

        NOTE: This function is not smart enough to guard against
        self-referencing response files.

        Args:
           List of argument strings to examine

        Returns:
           List of argument strings, including contents of any and all
           response files

        """

        new_arg_strings = []
        for arg_string in arg_strings:
            if not arg_string:
                new_arg_strings.append(arg_string)
            elif arg_string[0] not in self.fromfile_prefix_chars:
                new_arg_strings.append(arg_string)
            else:
                # It refers to a response file - open it up, parse it,
                # add its args to the running list
                response_filename = os.path.expanduser(os.path.expandvars(arg_string))
                new_arg_strings.extend(
                    _load_response_file(
                        response_filename,
                        comment_character=self.comment_character,
                        fromfile_prefix_chars=self.fromfile_prefix_chars
                        ))


        return new_arg_strings


# ----------------------------------------------------------------------

def _load_response_file(filename,
                        comment_character='#',
                        fromfile_prefix_chars='@'):
    """Load a set of arguments from a response file

    Open and read a response file.  Ignore lines whose first
    non-whitespace character is the comment character.

    Args:
      filename (string): String with leading prefix character ('@filename.txt')
      comment_character (string): Character indicating lines to ignore
      fromfile_prefix_chars (string): character indicating "more arguments in this file"

    Returns:
      List of arguments parsed from 'filename'
    """

    args_to_return = []

    with open(filename[1:], 'r') as infile:
        for raw_line in infile:
            args_to_return.extend(
                _text_line_to_args(
                    raw_line.strip(),
                    comment_character=comment_character,
                    fromfile_prefix_chars=fromfile_prefix_chars
                ))
    return args_to_return


def _text_line_to_args(text,
                       comment_character='#',
                       fromfile_prefix_chars='@'):
    """Internal method - read args from a line of text

    Take a line of text.  Unless it starts with a comment character,
    split it into words (obeying quotes as the shell would) and treat
    them each as an argument.  Return the list of arguments, including
    expanding response files if found.

    Args:
      text (string): String to parse
      comment_character (string): Character indicating 'no more commands in this row'
      fromfile_prefix_chars (string): Character indicating 'this argument is a response file'

    Returns:
      A list of the arguments after parsing.
    """

    if (not text) or text[0] == comment_character:
        return []
    else:
        args = []
        for maybe_arg in shlex.split(text):
            if (not maybe_arg) or len(maybe_arg) == 0:
                args.append(maybe_arg)
            elif maybe_arg[0] == comment_character:
                return args
            elif maybe_arg[0] in fromfile_prefix_chars:
                args.extend(
                    _load_response_file(
                        maybe_arg,
                        comment_character=comment_character,
                        fromfile_prefix_chars=fromfile_prefix_chars
                        ))
            else:
                args.append(maybe_arg)

        return args

# ----------------------------------------------------------------------

class _WriteResponseFile(standard_argparse.Action):
    """Action to tell the parser to write a response file

    Args:
      option_strings: Strings that can invoke command

    Kwargs:
      dest: Not Used
      default: Not Used
      help: Not Used
      **kwargs:  Other keyword arguments

    Returns:
      None
    """

    def __init__(self,
                 option_strings,
                 dest=SUPPRESS,
                 default=SUPPRESS,
                 help=None,
                 **kwargs):
        """Initialize a response file writer.

        Args:
           option_strings: Strings that can invoke the 'write response
              file' command

        Kwargs:
           dest (string): Where to store the response file output.
             Defaults to SUPPRESS since this is meaningless.
           default (string): Default value for the argument.
             Defaults to SUPPRESS since there isn't one.
           help (string): Help message for the argument.
             Defaults to None - we always supply this elsewhere.
           kwargs (dict): Any other arguments.  Passed along to the
             standard argparse.Action constructor.
        """

        super(_WriteResponseFile, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
            **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Call the write_response_file method on the parser"""
        parser.write_response_file()
        parser.exit()

# ----------------------------------------------------------------------

def _get_argument_name(arg):
    """Try to retrieve an argument name from an Action record.

    Look at the option_strings member in the action and return the
    first one.  Hopefully that will be the longest.  If there are no
    option strings then we're dealing with a positional argument --
    say so.

    Args:
       arg: Action record (argparse.Action)

    Returns:
       string containing guessed-at argument name
    """

    if arg is None:
        return None
    elif arg.option_strings:
        return arg.option_strings[0]
    else:
        global POSITIONAL_ARGUMENT
        return POSITIONAL_ARGUMENT

# ----------------------------------------------------------------------

class _ResponseFileWriter(object):
    """Formatter for generating example resonse files.

    This class is considered an entirely private API.

    Attributes:
       output (file-like): Destination for response file
       comment_character (string): Character prefix for each line
           in a blank response file
    """

    def __init__(self,
                 output,
                 comment_character='#'):
        """Initialize a response file writer with output stream and comment character.

        Args:
          output (file-like): Destination for response file
          comment_character (string): Prefix for each line in the file
        """

        self.output = output
        self.comment_character = comment_character
        self.args_written = set()

    def write_blank_line(self):
        """Write a blank line with just a leading comment character to the output file.
        """
        self.output.write('{}\n'.format(self.comment_character))

    def write_line(self, text):
        """Write a line of text prefixed with a comment character.

        Args:
             text (string): Text to write
        """

        self.output.write('{} {}\n'.format(self.comment_character, text))

    def write_action_group(self, group):
        """Write all the actions in a group

        Write a new section in a response file.  This will include the
        action group's title and description if available, all the
        actions in that group, and any subgroups.

        Args:
          group:  Action group to write to response file

        Returns:
          None
        """

        self.write_blank_line()
        self.write_line('------------------------------------')
        self.write_blank_line()

        if hasattr(group, 'title') and group.title not in (None, SUPPRESS):
            self.write_line('SECTION: {}'.format(group.title))
            self.write_blank_line()

        if group.description not in (None, SUPPRESS):
            wrapped_description_lines = textwrap.wrap(group.description, 72)
            for line in wrapped_description_lines:
                self.write_line(line)
            self.write_blank_line()

        for action in group._actions:
            if action.container == group:
                self.write_action(action)

        for subgroup in group._action_groups:
            self.write_action_group(subgroup)

    def write_action(self, action):
        """Write a single action to a response file.

        Write the action's help message (if any), option name (if any)
        and default value (if any) to a file.  The text will be
        commented out so that the user can choose which things to
        configure and which to leave alone.

        Args:
           action (argparse.Action): Action to write
        """

        global POSITIONAL_ARGUMENT, ARGUMENTS_TO_IGNORE

        argname = _get_argument_name(action)
        argname_for_desc = '{}: '.format(argname)

        if argname in ARGUMENTS_TO_IGNORE:
            return

        if argname in self.args_written:
            return
        else:
            self.args_written.add(argname)

        self.write_blank_line()

        if action.help not in (None, SUPPRESS):
            help_message = action.help
        else:
            help_message = ''

        option_intro = '{}{}'.format(argname_for_desc, help_message)
        hanging_indent = ' ' * (len(argname) + 2)
        wrapped_intro = textwrap.wrap(option_intro, subsequent_indent=hanging_indent)

        if action.choices not in (None, SUPPRESS):
            wrapped_intro.append('  Must be one of {}'.format(action.choices))

        for line in wrapped_intro:
            self.write_line(line)

        # The real line needs to have a proper name or nothing
        if argname == POSITIONAL_ARGUMENT:
            argname = ''

        if action.default not in (None, SUPPRESS):
            # We don't actually care what the value is for store_const
            # arguments since the user can't change it
            if hasattr(action, 'const') and action.const not in (None, SUPPRESS):
                self.write_line('{}'.format(argname))
            else:
                self.write_line('{} {}'.format(argname, action.default))
        else:
            self.write_line('{}'.format(argname))
