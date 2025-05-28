The assemble example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Writing trajectories to file for later use

Typical use:
    ./assemble --input=/data/flights.tsv --output=/data/flights.trj

Defaults assume a tab separated file formatted as :

OBJECTID TIMESTAMP LON LAT

Default output is standard out