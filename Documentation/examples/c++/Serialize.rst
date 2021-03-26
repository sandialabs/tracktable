=================
Serialize Example
=================

The serialize example compares storage costs for various methods of
serializing trajectories.

We have three ways to save trajectories:

    1. ``tracktable::TrajectoryWriter``  (C++, Python)

        This uses our own home-grown delimited text format. It is rather
        verbose.

    2. ``tracktable.rw.read_write_json`` (Python)

        Write to JSON. This is also rather verbose and has trouble with
        incremental loads.

    3. ``boost::serialization`` (C++)

        Write to Boost's archive format (text, binary or XML).

This example runs #1 and #3 on a sample trajectory and compares the
storage requirements.

This example demonstrates how to:

* Manually construct points and trajectories
* Use boost program options
* Use boost archives
* Use trajectory writer

The full ``serialize`` example source code can be found in the Tracktable source
code distribution in the directory ``tracktable/Examples`` and the example
can be executed by calling the ``serialize`` program from the command line provided
that the example is built and it's location is exposed to the appropriate system path.
Below you will find the execution command for the example as well as the
source files in there entirety for quick reference.

Example Source Files
--------------------

The page listed here contains a direct import of the source code for this example. This
is provided for convenience and reference.

.. toctree::
   :maxdepth: 2

   source/serialize.rst

Command Line Interface
----------------------

.. note:: This command is specific to Linux and Mac. Windows
   machines will have a different command line call.

The command to run the ``serialize`` example is as follows.

.. code-block:: console

   $ ./serialize_trajectories --trajectory-count=100 --point-count=100

This command takes a trajectory count parameter for the number of trajectories
to generate and serialize and a point count parameter for the number of points
per trajectory.

The command line interface contains a ``--help`` option that will display all of the possible
switches for the example

.. code-block:: console

   $ ./serialize --help

will display:

.. code-block:: console

  Options:
   --help                        Print help
   --trajectory-count arg (=100) number of trajectories to use
   --point-count arg (=100)      number of points per trajectory