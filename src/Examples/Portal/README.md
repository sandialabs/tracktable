The portal example takes trajectory data and attempts to find origin/destination
pairs. It breaks the USA into a grid, identifies what cells are populated by trajectories
and then refines the grid based on desired parameters. Each level of 'depth' is an
additional layer of refinement of the original grid. Each level is divided into
'bin-count' sections in both longitude and latitude. So each the number of cells:

cells = 12*5*bins^(2+depth)

empty cells are dropped but a cell is only empty if no trajectories pass through it

The portal example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Using boost program options to take parameters from command lines(in addition to the factories)
    - Use of boost::geometry::intersects to test where trajectories overlap regions

Typical use:
    ./portal-- input=/data/flights.tsv --depth=5 --min-value=12 --min-seperation=10 --bin-count=2

Defaults assume a tab separated file formatted as :

OBJECTID TIMESTAMP LON LAT