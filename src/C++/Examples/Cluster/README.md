The cluster example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Create features using distance geometries
    - Cluster and and assign membership using dbscan

Typical use:
    ./cluster --input=/data/flights.tsv

Defaults assume a tab separated points file formatted as :

OBJECTID TIMESTAMP LON LAT