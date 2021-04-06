==============
Filter Example
==============

This example demonstrates how to:

* Read in points using Tracktable's C++ command line factories
* Using 'required' option
* Using a function object to filter those points
* Using a point writer to output those points

The full ``filter`` example source code can be found in the Tracktable source
code distribution in the directory ``tracktable/Examples`` and the example
can be executed by calling the ``filter`` program from the command line provided
that the example is built and it's location is exposed to the appropriate system path.
Below you will find the execution command for the example as well as the
source files in there entirety for quick reference.

Example Source Files
--------------------

The page listed here contains a direct import of the source code for this example. This
is provided for convenience and reference.

.. toctree::
   :maxdepth: 2

   source/filter.rst

Command Line Interface
----------------------

.. note:: This command is specific to Linux and Mac. Windows
   machines will have a different command line call.

The command to run the ``filter`` example is as follows.

.. code-block:: console
   :caption: Typical Command

   $ ./filter_time --input=/data/flights.tsv --output=/results/filtered.tsv --start=2013-07-10-00:00:05 --stop=2013-07-10-00:01:05

This command takes an input parameter of a tab separated value or comma seperated value file
formatted as ``OBJECTID TIMESTAMP LON LAT``, an output parameter tab separated value or comma seperated value
file for the filtered points and start and stop timestamps parameters to use as a filter bounds.

.. note:: The default delimiter is ``tab``, if you are using a CSV file
   you will need to set the ``--delimiter`` parameter. The default output
   is standard out unless a ``--output`` file is specified.

The command line interface contains a ``--help`` option that will display all of the possible
switches for the example.

.. code-block:: console

   $ ./filter --help

will display:

.. code-block:: console

  --help                       Print help
  --output arg (=-)            file to write to (use '-' for stdout),
                               overridden by 'separate-kmls'
  --output arg (=-)            file to write to (use '-' for stdout),
                               overridden by 'separate-kmls'
  --start arg                   timestamp to start at
  --stop arg                   timestamp to stop at

  Point Reader:
    --input arg (=-)             Filename for input (use '-' for standard input)
    --real-field arg             Field name and column number for a real-valued
                                point field
    --string-field arg           Field name and column number for a string point
                                field
    --timestamp-field arg        Field name and column number for a timestamp
                                point field
    --object-id-column arg (=0)  Column containing object ID for points
    --timestamp-column arg (=1)  Column containing timestamp for points
    --x-column arg (=2)          Column containing X / longitude coordinate
    --y-column arg (=3)          Column containing Y / latitude coordinate
    --delimiter arg (=    )         Delimiter for fields in input file