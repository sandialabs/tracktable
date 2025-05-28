This example demonstrates using feature vectors to measure similarities between
trajectories via an Rtree

The predict example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Using boost program options to take parameters from command lines(in addition to the factories)
    - Conditioning trajectories based on length and objectid
    - Using boost rtree to locate similar trajectories based on cartesian distance in feature space

Typical use: '--string-field=dest x' is required

    ./predict --input=/data/SampleASDI.csv --delimeter=, --string-field=dest 30 --num-samples=10
