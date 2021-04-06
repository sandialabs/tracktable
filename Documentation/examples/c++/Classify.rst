================
Classify Example
================

This example demonstrates how to:

* Read in points using Tracktable's C++ command line factories
* Assemble points into trajectories
* Filtering trajectories on any combination of the following:

    * Length
    * Curvature
    * Hull Gyration Ratio
    * Length Ratio
    * Hull-aspect Ratio
    * Straightness
    * Number of turn arounds
* Different methods of applying filters
* Write trajectories out as KML

The full ``classify`` example source code can be found in the Tracktable source
code distribution in the directory ``tracktable/Examples`` and the example
can be executed by calling the ``classify`` program from the command line provided
that the example is built and it's location is exposed to the appropriate system path.
Below you will find the execution command for the example as well as the
source files in there entirety for quick reference.

Example Source Files
--------------------

The page listed here contains a direct import of the source code for this example. This
is provided for convenience and reference.

.. toctree::
   :maxdepth: 2

   source/classify.rst

Command Line Interface
----------------------

.. note:: This command is specific to Linux and Mac. Windows
   machines will have a different command line call.

The command to run the ``classify`` example is as follows.

.. code-block:: console
   :caption: Typical Command

   $ ./classify --input=/data/flights.tsv --min-turn-arounds=10 --output=/results/mappingflights.kml

This command takes an input parameter of a tab separated value or comma seperated value file
formatted as ``OBJECTID TIMESTAMP LON LAT`` of points to classify and an output parameter of a KML file
for the classified points and a minimum turnaround value.

.. note:: The default delimiter is ``tab``, if you are using a CSV file
   you will need to set the ``--delimiter`` parameter. The default output
   is standard out unless a ``--output`` file is specified.

The command line interface contains a ``--help`` option that will display all of the possible
switches for the example.

.. code-block:: console

   $ ./classify --help

will display:

.. code-block:: console

  --help                            Print help

  Classify:
    --assign-headings                 Assign headings to points
    --min-length arg                  minimum length of trajectory
    --max-length arg                  maximum length of trajectory
    --min-curvature arg               minimum curvature of trajectory
    --max-curvature arg               maximum curvature of trajectory

  hull-gyration-ratio:
    --min-hull-gyration-ratio arg     minimum value for hull-gyration-ratio
    --max-hull-gyration-ratio arg     maximum value for hull-gyration-ratio

  length-ratio:
    --min-length-ratio arg            minimum value for length-ratio
    --max-length-ratio arg            maximum value for length-ratio

  hull-aspect-ratio:
    --min-hull-aspect-ratio arg       minimum value for hull-aspect-ratio
    --max-hull-aspect-ratio arg       maximum value for hull-aspect-ratio

  straightness:
    --min-straightness arg            minimum value for straightness
    --max-straightness arg            maximum value for straightness

  turn-arounds:
    --min-turn-arounds arg            minimum value for turn-arounds
    --max-turn-arounds arg            maximum value for turn-arounds

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
    --delimiter arg (=    )              Delimiter for fields in input file

  Assembler:
    --separation-distance arg (=100)  Set maximum separation distance for
                                        trajectory points
    --separation-seconds arg (=1200)  Set maximum separation time (in seconds)
                                        for trajectory points
    --min-points arg (=10)            Trajectories shorter than this will be
                                        discarded
    --clean-up-interval arg (=10000)  Number of points between cleanup

  Output Options:
    --no-output                       specifies no output is wanted
    --separate-kmls                   indicate whether to separate output to
                                        different kmls in [result-dir]
    --result-dir arg (=result/)       directory to store separate kmls
    --output arg (=-)                 file to write to (use '-' for stdout),
                                        overridden by 'separate-kmls'