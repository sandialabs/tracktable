The reduce example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - using tracktable::simplify to remove unnecessary points
    - Writing trajectories to file for later use

Typical use:
    ./reduce --tolerance=0.00001 --input=/data/flights.tsv --output=/data/reduced.traj

Defaults assume a tab separated file formatted as :

OBJECTID TIMESTAMP LON LAT

Default output is standard out