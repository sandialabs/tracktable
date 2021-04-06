.. _user-guide-python-command-line:

============
Command Line
============

.. note:: While the information below is referencing Tracktable's
   rendering facilities, the command line functionality presented
   can be applied to other tracktable scripts.

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
   length as described in the :ref:`Trajectory Assembly <python-trajectory-assembly>`
   section.

2. **Response Files**: A response file is a way to package up
   arbitrarily many command-line arguments in a file and pass them to
   a script all at once. It is independent of which script is being
   run. Since a response file is just text it is easy to place under
   version control. We provide a slightly modified version of the
   standard Python :py:mod:`argparse` module that includes support
   for response files containing comments and response files that load
   other response files.

.. _user-guide-python-argument-groups:

---------------
Argument Groups
---------------

The point of an argument group is to save us from having to cut and
paste the same potentially-lengthy list of arguments and their
respective handlers into each new script we write. When we render a
movie of data over time, for example, we will always need several
pieces of information including resolution, frame rate, and the
duration of our movie.

Since we're human we are guaranteed to forget an argument here, spell
one differently there, and before long we have a dozen scripts that
all take completely different command-line arguments. Bundling
arguments in an easy-to-reuse fashion makes it easy for us to use the
same ones consistently.

We derive another benefit at the same time. By abstracting away a set
of arguments into a semi-opaque module, we can add capability to (for
example) the mapmaker without having to change our movie-making
script. Once the argument group for the mapmaker is updated, any
script that uses the mapmaker's argument group will automatically gain
access to the new capability.

There are three parts to using argument groups. First they must be
created and registered. Second, they are applied when we create an
argument parser for a script. Finally, once command-line arguments
have been parsed, we (as the programmers) can extract values for each
argument group that you used. All of these functions are in the
:py:mod:`tracktable.script_helpers.argument_groups.utilities` module.

.. _create-arg-group-python:

Creating an Argument Group
--------------------------

We create an argument group first by declaring it with
:py:func:`create_argument_group() <tracktable.script_helpers.utilities.create_argument_group>`
and then populating it with calls to
:py:func:`add_argument() <tracktable.script_helpers.utilities.add_argument>`.
Here is an example from the ``movie_rendering`` group:

.. code-block:: python
   :linenos:

   create_argument_group("movie_rendering",
                        title="Movie Parameters",
                        description="Movie-specific parameters such as frame rate, encoder options, title and metadata")

   add_argument("movie_rendering", [ "--duration" ],
               type=int,
               default=60,
               help="How many seconds long the movie should be")

   add_argument("movie_rendering", [ "--fps" ],
               type=int,
               default=30,
               help="Movie frame rate in frames/second")

   add_argument("movie_rendering", [ "--encoder-args" ],
               default="-c:v mpeg4 -q:v 5",
               help="Extra args to pass to the encoder (pass in as a single string)")

All of Tracktable's standard argument groups are in files in the
``Python/tracktable/script_helpers/argument_groups`` directory. Look
at ``__init__.py`` in that directory for an example of how to add one
to the registry. You can register your own groups anywhere in your
code that you choose.

.. _apply-arg-group-python:

Applying Argument Groups
------------------------

We use argument groups by applying their arguments to an
already-instantiated argument parser. That can be an instance of the
standard :py:class:`argparse.ArgumentParser` or our customized version
:py:class:`tracktable.script_helpers.argparse.ArgumentParser`. For example:

.. code-block:: python
   :linenos:

    from tracktable.script_helpers import argparse, argument_groups

    parser = argparse.ArgumentParser()
    argument_groups.use_argument_group("delimited_text_point_reader", parser)
    argument_groups.use_argument_group("trajectory_assembly", parser)
    argument_groups.use_argument_group("trajectory_rendering", parser)
    argument_groups.use_argument_group("mapmaker", parser)

We can interleave calls to :py:func:`use_argument_group() <tracktable.script_helpers.argument_groups.utilities.use_argument_group>`
freely with calls to other functions defined on
:py:class:`ArgumentParser <argparse.ArgumentParser>`.
We recommend reading the code for
:py:func:`use_argument_group() <tracktable.script_helpers.argument_groups.utilities.use_argument_group>`
if you need to do especially complex things with ``argparse`` such
as mutually exclusive sets of options.

.. _use-parsed-arg-vals-python:

Using Parsed Argument Values
----------------------------

After we call :py:meth:``parser.parse_args()
<argparse.ArgumentParser.parse_args>`` we are left with a ``Namespace``
object containing all the values for our command-line options, both
user-supplied and default. We use the :py:func:``extract_arguments()
<tracktable.script_helpers.argument_groups.utilities.extract_arguments>``
function to retrieve sets of arguments that we configured using
:py:func:``use_argument_group()
<tracktable.script_helpers.argument_groups.utilities.use_argument_group>``.
Our practice is to define handler functions that take every argument
in a group so that we can write code like the following:

.. code-block:: python
   :linenos:

   def setup_trajectory_source(point_source, args):
       trajectory_args = argument_groups.extract_arguments("trajectory_assembly", args)
       source = example_trajectory_builder.configure_trajectory_builder(
           **trajectory_args
          )
       source.input = point_source

       return source.trajectories()

Since we are not required to refer to the individual arguments
directly, the user can take advantage of new capabilities added to the
underlying modules whether or not we know about them when we write our
script.

.. todo:: Add tracktable.script_helpers.argument_groups to the documentation

.. _user-guide-python-response-files:

--------------
Response Files
--------------

.. todo:: Document response files in full

Once we start calling scripts with more than 3 or 4 options it becomes
difficult to keep track of all the arguments and difficult to edit the
command line. We address this with *response files*, textual listings
of command-line options and their values that we can pass to scripts.
The standard Python ``argparse`` module has limited support for
response files. We expand upon it with our own extended ``argparse``.

Fuller documentation is coming soon. This should be enough to get you started:

.. code-block:: console

   $ cd tracktable/Python/tracktable/examples
   $ python heatmap_from_csv.py --write-response-file > heatmap_response_file.txt

Now open up ``heatmap_response_file.txt`` in your favorite editor.
Lines that begin with ``#`` are comments. Uncomment any arguments you
please and add or change values for them. After you save the file,
run the script as follows:

.. code-block:: console

   $ python heatmap_from_csv.py @heatmap_response_file.txt

That will tell the script to read arguments from
``heatmap_response_file.txt`` as well as from the command line.

You can freely mix response files and standard arguments on a single
command line. You can also use multiple response files. The
following command line would be perfectly valid:

.. code-block:: console

   $ python make_movie.py @hd_movie_params.txt @my_favorite_map.txt movie_outfile.mkv
