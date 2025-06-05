The findid example demonstrates:
    - Using command line factories to read points and assemble trajectories
    - Reading a list of ids from a file
    - Searching trajectories for specific object ids

Typical use:
    ./findid --input=/data/flights.tsv --idfile=/data/mapping_ids.txt

Defaults assume a tab separated points file formatted as :

OBJECTID TIMESTAMP LON LAT

And an id file with a single object id per line.

Default output is a simple count of how many trajectories were found.