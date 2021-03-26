=======================
Data Used By Tracktable
=======================

Tracktable loads and saves points in delimited text format, most 
commonly CSV (comma-separated values) and TSV (tab-separated values) 
files.  This page describes how the point reader and writer classes
deal with comments, headers, and metadata columns.

Support for storing and loading trajectories using 
`GeoJSON <https://geojson.org>`_ files is slated for release no later
than Tracktable 1.7.

.. note:: The only difference in the examples for CSV and TSV files
   is the delimiter.  The data sets are identical.

CSV Data
========

Point Data
----------
.. code-block::

    # object_id timestamp latitude longitude altitude heading speed
    KKK011,2004-12-07 11:36:18,-81.9731,26.995,2700,108,349,0
    KKK011,2004-12-07 11:37:56,-81.9844,27.0447,4200,108,349,-27
    KKK011,2004-12-07 11:39:18,-82.0458,27.1136,6700,225,322,-22
    KKK011,2004-12-07 11:40:18,-82.0961,27.1389,7900,180,300,5
    KKK011,2004-12-07 11:41:18,-82.1442,27.1683,9200,181,305,-2
    KKK011,2004-12-07 11:42:18,-82.1967,27.1978,10300,193,303,-1
    KKK011,2004-12-07 11:43:18,-82.2469,27.2253,11300,183,302,0
    KKK011,2004-12-07 11:44:18,-82.2997,27.2544,12500,193,302,1
    KKK011,2004-12-07 11:45:18,-82.3525,27.2839,13500,194,303,6
    KKK011,2004-12-07 11:46:18,-82.4008,27.3175,14400,190,309,-8


Point Data With Comments
------------------------
.. code-block::

    # object_id timestamp latitude longitude altitude heading speed
    KKK011,2004-12-07 11:36:18,-81.9731,26.995,2700,108,349,0
    #KKK011,2004-12-07 11:37:56,-81.9844,27.0447,4200,108,349,-27
    #  KKK011,2004-12-07 11:39:18,-82.0458,27.1136,6700,225,322,-22
    KKK011,2004-12-07 11:40:18,-82.0961,27.1389,7900,180,300,5
    KKK011#,2004-12-07 11:41:18,-82.1442,27.1683,9200,181,305,-2
    #
    #
    KKK011,2004-12-07 11:42:18,-82.1967,27.1978,10300,193,303,-1
    KKK011,2004-12-07 11:43:18,-82.2469,27.2253,11300,183,302,0
    KKK011,2004-12-07 11:44:18,-82.2997,27.2544,12500,193,302,1


Point Data With Skippable Headers
---------------------------------
.. code-block::

    Undelimited line header with additional and maybe irrelevant information
    This part of the file is not intended to be processed

    # object_id timestamp latitude longitude altitude heading speed
    KKK011,2004-12-07 11:36:18,-81.9731,26.995,2700,108,349,0
    #KKK011,2004-12-07 11:37:56,-81.9844,27.0447,4200,108,349,-27
    #  KKK011,2004-12-07 11:39:18,-82.0458,27.1136,6700,225,322,-22
    KKK011,2004-12-07 11:40:18,-82.0961,27.1389,7900,180,300,5
    KKK011#,2004-12-07 11:41:18,-82.1442,27.1683,9200,181,305,-2
    #
    #
    KKK011,2004-12-07 11:42:18,-82.1967,27.1978,10300,193,303,-1

.. note:: Headers are not skipped by default. Comment delimiters and hard
    values for number of lines to skip are passed in as parameters when
    configuring your point and trajectory readers.

TSV Data
========

Point Data
----------
.. code-block::

    # object_id timestamp longitude latitude
    ANON	2014-01-01 00:00:00	132.3653180042665	37.83452922520744
    ANON	2014-01-01 00:00:00	140.1555350524732	37.00319417805791
    ANON	2014-01-01 00:00:00	138.8552751176905	33.91442753969869
    ANON	2014-01-01 00:00:00	139.54339149007725	34.37733184602518
    ANON	2014-01-01 00:00:00	138.6712734537105	36.79593017895808
    ANON	2014-01-01 00:00:00	142.1620084423819	35.09865794853191
    ANON	2014-01-01 00:00:00	145.53358077966556	41.534209724603194
    ANON	2014-01-01 00:00:00	139.7960001774872	35.78134081160728
    ANON	2014-01-01 00:00:00	140.82555476137813	35.69316848225954
    ANON	2014-01-01 00:00:00	145.63477153712424	37.974929548163544

Point Data With Comments
------------------------
.. code-block::

    # object_id timestamp latitude longitude altitude heading speed
    KKK011	2004-12-07 11:36:18	-81.9731	26.995	2700	108	349	0
    #KKK011	2004-12-07 11:37:56	-81.9844	27.0447	4200	108	349	-27
    #  KKK011	2004-12-07 11:39:18	-82.0458	27.1136	6700	225	322	-22
    KKK011	2004-12-07 11:40:18	-82.0961	27.1389	7900	180	300	5
    KKK011#	2004-12-07 11:41:18	-82.1442	27.1683	9200	181	305	-2
    #
    #
    KKK011	2004-12-07 11:42:18	-82.1967	27.1978	10300	193	303	-1
    KKK011	2004-12-07 11:43:18	-82.2469	27.2253	11300	183	302	0
    KKK011	2004-12-07 11:44:18	-82.2997	27.2544	12500	193	302	1


Point Data With Skippable Headers
---------------------------------
.. code-block::

    Undelimited line header with additional and maybe irrelevant information
    This part of the file is not intended to be processed

    # object_id timestamp latitude longitude altitude heading speed
    KKK011	2004-12-07 11:36:18	-81.9731	26.995	2700	108	349	0
    #KKK011	2004-12-07 11:37:56	-81.9844	27.0447	4200	108	349	-27
    #  KKK011	2004-12-07 11:39:18	-82.0458	27.1136	6700	225	322	-22
    KKK011	2004-12-07 11:40:18	-82.0961	27.1389	7900	180	300	5
    KKK011#	2004-12-07 11:41:18	-82.1442	27.1683	9200	181	305	-2
    #
    #
    KKK011	2004-12-07 11:42:18	-82.1967	27.1978	10300	193	303	-1
