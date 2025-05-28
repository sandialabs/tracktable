The classify example demonstrates:
- Using command line factories to read points and assemble trajectories
- Using boost program options to take parameters from command lines (in addtion to the factories)
- Filtering trajectories on any combination of the following :
  - length
  - curvature
  - hull gyration ratio
  - length ratio
  - hull-aspect ratio
  - straightness
  - number of turn arounds
- A few different methods of applying these filters are demonstrated int he code
- Writing trajectories as KML

Typical use:
    ./classify --input=/data/flights.tsv --min-turn-arounds=10 --output=/results/mappingflights.kml

Defaults assume a tab separated file formatted as:

    OBJECTID TIMESTAMP LON LAT

Default output is standard out
