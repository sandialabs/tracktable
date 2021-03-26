==============
Portal Example
==============

The portal example takes trajectory data and attempts to find origin/destination
pairs. It breaks the USA into a grid, identifies what cells are populated by trajectories
and then refines the grid based on desired parameters. Each level of ``depth`` is an
additional layer of refinement of the original grid. Each level is divided into
``bin-count`` sections in both longitude and latitude. So for each of the cells:

.. math::

   cells = 12*5*bins^{(2+depth)}

Empty cells are dropped but a cell is only empty if no trajectories pass through it.

This example demonstrates how to:

* Read in points using Tracktable's C++ command line factories
* Assemble points into trajectories
* Use boost program options to take parameters from command lines (in addition to the factories)
* Use ``boost::geometry::intersects`` to test where trajectories overlap region

The full ``portal`` example source code can be found in the Tracktable source
code distribution in the directory ``tracktable/Examples`` and the example
can be executed by calling the ``portal`` program from the command line provided
that the example is built and it's location is exposed to the appropriate system path.
Below you will find the execution command for the example as well as the
source files in there entirety for quick reference.

Example Source Files
--------------------

The page listed here contains a direct import of the source code for this example. This
is provided for convenience and reference.

.. toctree::
   :maxdepth: 2

   source/portal.rst

Command Line Interface
----------------------

.. note:: This command is specific to Linux and Mac. Windows
   machines will have a different command line call.

The command to run the ``portal`` example is as follows.

.. code-block:: console
   :caption: Typical Command

   $ ./portal-- input=/data/flights.tsv --depth=5 --min-value=12 --min-seperation=10 --bin-count=2

This command takes an input parameter of a tab separated value or comma seperated value file
formatted as ``OBJECTID TIMESTAMP LON LAT`` of points to assemble, a depth parameter for refinement,
a minimum parameter for portal pairs, minimum value parameter of portal separation distance in lon-lat, and
a bin-count value for number of sections to divide into per level.

.. note:: The default delimiter is ``tab``, if you are using a CSV file
   you will need to set the ``--delimiter`` parameter. The default output
   is standard out.

The command line interface contains a ``--help`` option that will display all of the possible
switches for the example.

.. code-block:: console

   $ ./portal --help

will display:

.. code-block:: console

   --help                            Print help

   Point Reader:
    --input arg (=-)                  Filename for input (use '-' for standard
                                        input)
    --real-field arg                  Field name and column number for a
                                        real-valued point field
    --string-field arg                Field name and column number for a string
                                        point field
    --timestamp-field arg             Field name and column number for a
                                        timestamp point field
    --object-id-column arg (=0)       Column containing object ID for points
    --timestamp-column arg (=1)       Column containing timestamp for points
    --x-column arg (=2)               Column containing X / longitude coordinate
    --y-column arg (=3)               Column containing Y / latitude coordinate
    --delimiter arg (=    )           Delimiter for fields in input file

   Assembler:
    --separation-distance arg (=100)  Set maximum separation distance for
                                        trajectory points
    --separation-seconds arg (=1200)  Set maximum separation time (in seconds)
                                        for trajectory points
    --min-points arg (=10)            Trajectories shorter than this will be
                                        discarded
    --clean-up-interval arg (=10000)  Number of points between cleanup