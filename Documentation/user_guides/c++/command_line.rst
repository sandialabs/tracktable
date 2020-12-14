
.. _userguide-cpp-command-line:

============
Command Line
============

Tracktable's various rendering facilities have a lot of options.
Python makes it easy for us to expose these as command-line options
that can be passed to scripts. However, that just pushes the problem
out one level: now the user has to remember the values for all of
those options, or else write shell scripts that call Python scripts in
order to keep track of what parameters were used where.

We introduce two facilities to help tame this morass:

1. **Argument Groups**: An argument group is a set of command-line
   arguments that all pertain to a single capability. For example,
   the argument group for trajectory assembly has entries for the
   maximum separation distance, maximum separation time and minimum
   length as described above in :ref:`c-trajectory-assembly`.

2. **Response Files**: A response file is a way to package up
   arbitrarily many command-line arguments in a file and pass them to
   a script all at once. It is independent of which script is being
   run. Since a response file is just text it is easy to place under
   version control. We provide a slightly modified version of the
   standard Python :py:mod:`argparse` module that includes support
   for response files containing comments and response files that load
   other response files.