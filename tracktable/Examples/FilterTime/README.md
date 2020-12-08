This program takes an input file of points and filters for points that fall within
two given timestamps

The filter_time example demonstrates:
    - Using command line factories to read points
    - Using 'required' options
    - Using a function object to filter those points
    - Using a point writer to output those points.

Typical use:
    ./filter_time --input=/data/flights.tsv --output=/results/filtered.tsv --start=2013-07-10-00:00:05 --stop=2013-07-10-00:01:05

Defaults assume a tab separated points file formatted as :

OBJECTID TIMESTAMP LON LAT