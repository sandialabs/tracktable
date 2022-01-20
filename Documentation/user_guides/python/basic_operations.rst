.. _user-guide-python-basic-ops:

****************
Basic Operations
****************

.. _user-guide-python-point-ops:

Operations On Points
====================

You will most commonly operate on points (singly or in small sets)
in order to construct trajectories or while manipulating
trajectories to construct more trajectories.

The second most common use case for operations on points is to
to compute point-to-point quantities like speed, bearing, distance,
and turn angle. These can be used as features in analysis or as
annotations to decorate trajectories during rendering.

All of our mathematical operations on trajectory points are in the
module :py:mod:`tracktable.core.geomath`. These include concepts
like distance or speed between two points, the bearing from one point
to another, the turn angle at a point, and the geometric mean or
median of set of points. Please refer to the ``geomath`` module
for details.


Examples of Per-Point Features
------------------------------

.. todo::
   Write this section


Adding Per-Point Features To Trajectories
-----------------------------------------


Once we have points or trajectories in memory we may want to
annotate them with derived quantities for analysis or rendering. For
example, we might want to color an airplane's trajectory using its
climb rate to indicate takeoff, landing, ascent and descent. We
might want to use acceleration, deceleration and rates of turning to
help classify moving objects.

In order to accomplish this, we add features to the per-point properties
of ``TrajectoryPoint`` objects as *annotations*. The
:py:mod:`tracktable.feature.annotations` module contains functions for
this: *calculators* to compute a feature and *accessors* to retrieve the
feature later for analysis and rendering. Calculators and accessors
are deliberately simple to make it easier for you to add your own. There
is no limit to the number of features you can add to each point.

The simplest feature is *progress*. This has a value of zero at the
beginning of the trajectory and one at the end. It is useful for color-
coding trajectories for visualization so that their beginnings and ends
are easy to distinguish.


Annotations Example
^^^^^^^^^^^^^^^^^^^

.. code-block:: python
   :caption: Adding Progress Indicator To Trajectories
   :linenos:

   from tracktable.feature import annotations

   # Suppose that my_trajectories is a list of already-
   # compiled trajectories. We want to add the "progress"
   # annotation to all the points in each trajectory.

   annotated_trajectories = [
       annotations.progress(t) for t in my_trajectories
   ]


.. code-block:: python
   :caption: Retrieving Accessor For Given Annotation
   :linenos:

   from tracktable.feature import annotations

   # Retrieve the color type of the trajectory
   if trajectory_color_type == 'scalar':
       annotator = annotations.retrieve_feature_function(trajectory_color)

       def annotation_generator(traj_source):
           for trajectory in traj_source:
               yield(annotator(trajectory))

       trajectories_to_render = annotation_generator(trajectory_source)
       scalar_generator = annotations.retrieve_feature_accessor(trajectory_color)
       colormap = trajectory_colormap

.. todo::
   This second code snippet is confusing.

.. _python-trajectory-assembly:


Assembling Trajectories from Points
-----------------------------------

Creating trajectories from a set of points is at heart a simple
operation. Sort a set of input points by non-decreasing timestamp,
then group them by object ID. Each different group can then be viewed
as the vertices of a polyline (connected series of line segments).
This is our representation for a trajectory.

The task becomes more nuanced when we consider the following question:

    If a trajectory contains a large gap in either time or distance
    between two successive points, is it still a single trajectory?

The answer to this question changes for every different data set. The
trajectory assembler in Tracktable allows you to specify your own
values for the distance and time separation thresholds. Here are the details.


Tracktable includes a filter,
:py:class:`tracktable.applications.assemble_trajectories.AssembleTrajectoryFromPoints`,
to create a sequence of trajectories from a sequence of trajectory
points sorted by increasing timestamp. The caller is responsible
for ensuring that the points are sorted.

This filter is present in both C++ and Python. In Python, the input
point sequence only needs to be an *iterable* and will only be traversed
once. The output (sequence of trajectories) is also an iterable and can
only be traversed once. In practice, we almost always save the assembled
trajectories in a list for later use.

``AssembleTrajectoryFromPoints`` has three parameters in addition to
the point sequence:

#. ``separation_time`` (:py:class:`datetime.timedelta`) If the
   timestamps of two successive points with the same object ID
   differ by more than this amount, the points before the gap will
   be packaged up as a finished trajectory. A new trajectory will
   begin with the first point after the gap. The default separation
   time is 30 minutes.

#. ``separation_distance`` (float): If two successive points with
   the same object ID are more than this distance apart, the points
   before the gap will be packaged up as a finished trajectory.
   A new trajectory will begin with the first point after the gap.
   The units of measurement for the separation distance depend on
   the point domain: kilometers for Terrestrial, no units for 2D
   and 3D Cartesian points. The default separation distance is
   infinite; that is, as long as two points are close enough together
   in time, the trajectory will continue.

#. ``minimum_length`` (integer): Finished trajectories will be discarded
   unless they contain at least this many points. The default is 2
   points.

.. note::
   The name "minimum_length" is confusing because *length* can refer to
   distance as well as number of points. We will provide a better name
   in Tracktable 1.6, deprecate the existing name, and remove it in some
   future release.



Trajectory Assembly Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
   :caption: Trajectory Assembly
   :linenos:

   from tracktable.domain.terrestrial import TrajectoryPointReader

   with open('SampleFlight.csv', 'rb') as infile:
       reader = TrajectoryPointReader()
       reader.input = infile
       reader.delimiter = ','

       # Columns 0 and 1 are the object ID and timestamp
       reader.object_id_column = 0
       reader.timestamp_column = 1

       # Columns 2 and 3 are the longitude and
       # latitude (coordinates 0 and 1)
       reader.coordinates[0] = 2
       reader.coordinates[1] = 3

       # Column 4 is the altitude
       reader.set_real_field_column("altitude", 4)

       trajectory_assembler = AssembleTrajectoryFromPoints()
       trajectory_assembler.input = reader

       trajectory_assembler.separation_time = datetime.timedelta(minutes=30)
       trajectory_assembler.separation_distance = 100
       trajectory_assembler.minimum_length = 10

       trajectories = list(trajectory_assembler)
       # process trajectories here or add to a list



Operations On Trajectories
==========================

Some common use cases for operating on trajectories:

#. Interpolate between points to find an approximate position at a
    specified time or distance traveled

#. Extract a subset of the trajectory with endpoints specified by
    time or distance traveled

#. Compute a scalar feature that describes some aspect of the entire
    trajectory

#. Compute a vector of distance geometry values that collectively describe
    the trajectory's shape



Interpolation and Subsets
-------------------------

The module :py:mod:`tracktable.core.geomath` contains several
functions for interpolation along trajectories and extracting
subsets between interpolated points. The first two will produce a
TrajectoryPoint at some specified fraction along the trajectory,
parameterized between 0 and 1 by time elapsed or by distance
traveled.

#. :py:func:`tracktable.core.geomath.point_at_time_fraction`

#. :py:func:`tracktable.core.geomath.point_at_length_fraction`

These functions interpolate coordinates, timestamps, and all of the
additional features present at points. We provide two separate
parameterizations because indexing by time can lead to division by
zero in later algorithms when a trajectory includes a stretch where
the underlying vehicle stopped. Indexing by distance avoids this
problem by ignoring veloity.

To extract a subset of trajectory instead of individual points, use
:py:func:`subset_during_interval`. This function takes its endpoints
as fractions between 0 and 1 (parameterized by time). We will add
analogous functions to extract a subset by distance traveled,
time fraction, and distance fraction for Tracktable 1.6.


Computing Scalar-Valued Trajectory Features
-------------------------------------------

A scalar-valued trajectory feature is a single number that describes
some aspect of the trajectory. A collection of these features can
characterize a trajectory well enough to establish similarity and
difference in a collection.

Here are a few examples along with code snippets to compute them. There
are many other possible features.

.. code-block:: python
    :linenos:

    import tracktable.core.geomath

    def total_travel_distance(trajectory):
        return trajectory[-1].current_length

    def end_to_end_distance(trajectory):
        return tracktable.core.geomath.distance(
            trajectory[0], trajectory[-1]
        )

    def straightness_ratio(trajectory):
        return end_to_end_distance(trajectory) / total_travel_distance(trajectory)

    def total_winding(trajectory):
        t = trajectory
        return sum([
            tracktable.core.geomath.signed_turn_angle(t[i], t[i+1], t[i+2])
            for i in range(0, len(trajectory) - 3)
        ])

    def total_turning(trajectory):
        t = trajectory
        return sum([
        tracktable.core.geomath.unsigned_turn_angle(t[i], t[i+1], t[i+2])
        for i in range(0, len(trajectory) - 3)
        ])



Computing Distance Geometry Features
------------------------------------

.. _python-distance-geometry:

`Distance geometry <https://en.wikipedia.org/wiki/Distance_geometry>`_ is
a family of methods for analyzing sets of points based only on the distances
between pairs of members. In Tracktable, we use distance geometry to compute
a multiscale description (called a *signature*) of a trajectory's shape that
can be used to search for similar trajectories independent of translation,
uniform scale, rotation, or reflection.


The :py:mod:`tracktable.algorithms.distance_geometry` module is responsible
for computing the multilevel distance geometry signature of a given
trajectory. As with extracting points and subsets, we provide functions
to compute this signature with points sampled by length or time. If your
data includes trajectories of objects that stop in one place, we recommend
that you use the parameterization over length to avoid division by zero.




How Distance Geometry Works
^^^^^^^^^^^^^^^^^^^^^^^^^^^

When computing the distance geometry feature values
for a trajectory, we first choose a depth *d*. For each level
``L = 1 ... d``, we place ``L+1`` points along the trajectory, equally spaced
in either distance or time. Then, for that level, we compute the straightness
of the ``L`` line segments that connect those points from beginning to end.
A straightness value of 1 means that the trajectory is perfectly straight between
two sample points. A straightness value of 0 means that the trajectory ends
at the same point it began for a given segment regardless of its meandering
along the way.

We collect these straightness values for all *d* levels to assemble a signature,
which can be used as a feature vector. A distance geometry signature with depth
*d* will have ``(d * (d+1)) / 2`` values.


Distance Geometry Example
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
    :caption: Distance Geometry by Distance and Time
    :linenos:

    from tracktable.algorithms.distance_geometry import distance_geometry_by_distance
    from tracktable.algorithms.distance_geometry import distance_geometry_by_time
    from tracktable.domain.terrestrial import TrajectoryPointReader

    with open('point_data.csv', 'rb') as infile:
        reader = TrajectoryPointReader()
        reader.input = infile
        reader.delimiter = ','

        # Columns 0 and 1 are the object ID and timestamp
        reader.object_id_column = 0
        reader.timestamp_column = 1

        # Columns 2 and 3 are the longitude and
        # latitude (coordinates 0 and 1)
        reader.coordinates[0] = 2
        reader.coordinates[1] = 3

        # Column 4 is the altitude
        reader.set_real_field_column("altitude", 4)

        trajectory_assembler = AssembleTrajectoryFromPoints()
        trajectory_assembler.input = reader

        trajectory_assembler.separation_time = datetime.timedelta(minutes=30)
        trajectory_assembler.separation_distance = 100
        trajectory_assembler.minimum_length = 10

        distance_geometry_length_values = distance_geometry_by_distance(trajectory_assembler.trajectories(), 4)
        distance_geometry_time_values = distance_geometry_by_time(trajectory_assembler.trajectories(), 4)


.. note::
   Refer to "Clustering with Distance Geometry" example
   Mention what we could do with these distance geometry values after computing them




Analyzing Trajectories Using Feature Vectors
============================================

.. _user-guide-python-analysis:

The goal of feature creation is to represent each data point (in this
case, each trajectory) with a feature vector. then to use those feature
vectors as the inputs for further analysis.

In this section we will show you how to create a feature vector from
a collection of features and how to feed those features to DBSCAN
for clustering and an R-tree for finding items similar to an example.


Creating Feature Vectors
------------------------


Tracktable has a specific point domain for feature vectors just as it has
domains for geographic and Cartesian coordinates. In our current release we
support feature vectors with 1 to 30 components. The function
:py:func:`tracktable.domain.feature_vectors.convert_to_feature_vector` will
convert a list or array of values into a feature vector:

.. code-block:: python
    :caption: Creating a Feature Vector
    :linenos:

    from tracktable.domain.feature_vectors import convert_to_feature_vector

    # Suppose that the array 'my_feature_values' contains all of the features
    # for a single trajectory.

    my_feature_vector = convert_to_feature_vector(my_feature_values)

Like other Tracktable point types, the caller can read and write the
individual values in a feature vector using the ``[]`` operator. In
other words, just treat it like an ordinary list or array.



* The :py:mod:`tracktable.algorithms.distance_geometry` submodule will
  compute the multilevel distance geometry for a trajectory based on either ``length``
  or ``time``.
* The :py:mod:`tracktable.algorithms.dbscan` submodule will perform box density-based spatial
  clustering of applications with noise analysis to determine the clustering of the
  feature vector points.
* The :py:mod:`tracktable.domain.rtree` submodule will generate an R-tree that
  can efficiently compute the nearest neighbors of a given point or set of points.



.. _python-dbscan:

DBSCAN Clustering
-----------------

`DBSCAN <https://en.wikipedia.org/wiki/DBSCAN>`_ is a density-based
clustering method that does not need to know the number of clusters
in advance. It operates instead on a notion of when two points are
close together. You must supply two parameters:

#. **Closeness:** How close must two points be along each axis
    in order to belong to the same cluster?

#. **Minimum cluster size:** How many points must be close to one another
    in order to be considered a cluster instead of coincidence?

As originally described, DBSCAN uses a single value to define "closeness".
This value is used as the radius of a sphere. For any given point, all
other points within that sphere are close by.

In Tracktable, we specify closeness as a list of values, one per feature.
This allows different values of closeness depending on the properties
of each feature.

Suppose that you have maximum altitude and maximum speed as two of your
features. In clustering, you might want to identify trajectories that have
similar combinations of altitude and speed. In this situation you need
a neighborhood defined with a box and a sphere because of the ranges of the
variables involved. Maximum altitude is measured in feet above sea level and ranges
from 0 to around 40,000. Maximum speed is measured in kilometers per hour and ranges
from 0 to around 1000. Since these ranges are so different, any value that encompasses
"close enough" for altitude will be too large to distinguish different classes
of speeds. Conversely, any value that can divide speeds into different classes
will be too small to group altitudes together.

Mathematically, a single radius is equivalent to clustering on the L2 norm.
A vector of distances is conceptually equivalent to the L-infinity norm.

.. note::
   An upcoming release of Tracktable will add back in the ability to specify
   a single radius. We also hope to extend DBSCAN to arbitrary metrics.

.. todo::
   Modify this example to use max altitude / max speed as our features. Run
   on an example data set that has a mix of different classes of aircraft.

Our implementation of DBSCAN is in the :py:mod:`tracktable.algorithms.dbscan`
module. Here is an example of how to invoke it.


.. code-block:: python
   :caption: DBSCAN Clustering
   :linenos:

   from tracktable.algorithms.dbscan import compute_cluster_labels
   import tracktable.core.geomath

   # Assume that 'all_trajectories' is a list of trajectories from some
   # data source

   # First we need features.
   def end_to_end_distance(trajectory):
       return tracktable.core.geomath.distance(trajectory[0], trajectory[-1])

   def total_length(trajectory):
       return trajectory[-1].current_length

   feature_values = [
      [end_to_end_distance(t), total_length(t)] for t in all_trajectories
   ]

   # Now we can create feature vectors.
   feature_vectors = [convert_to_feature_vector(fv) for fv in feature_values]

   # Let's say that two flights are "similar" if they have end-to-end distances
   # within 5km of one another (suggesting that they flew between the same two
   # airports) and total lengths within 100km of one another (to allow for
   # minor diversions and holding patterns).

   closeness = [5, 100]

   minimum_cluster_size = 10

   # And now we can run DBSCAN.

   cluster_labels = compute_cluster_labels(
                        feature_vectors,
                        closeness,
                        minimum_cluster_size
                    )

   # Done -- conduct further analysis or visualization based on the cluster labels.

.. _python-rtree:

R-Tree
------

The R-tree is a data structure that provides a fast way to find all
points near a given search position. We use it to find all feature
vectors within some specified distance of a sample feature vector.
This, in turn, allows us to identify trajectories that have similar
features.

.. note::
   This may sound very familiar to the description of how DBSCAN
   identifies points that are close together. DBSCAN uses an
   R-tree internally.

As in our last example, we will use end-to-end distance and total
travel distance as our two features.



.. code-block:: python
   :caption: R-Tree Search
   :linenos:

   from tracktable.domain.rtree import RTree
   from tracktable.domain.feature_vectors import convert_to_feature_vector
   import tracktable.core.geomath

   # Assume that 'all_trajectories' is a list of trajectories from some
   # data source

   # First we need features.
   def end_to_end_distance(trajectory):
       return tracktable.core.geomath.distance(trajectory[0], trajectory[-1])

   def total_length(trajectory):
       return trajectory[-1].current_length

   feature_values = [
      [end_to_end_distance(t), total_length(t)] for t in all_trajectories
   ]

   # Now we can create feature vectors.
   feature_vectors = [convert_to_feature_vector(fv) for fv in feature_values]

   # Now we create an R-tree from those feature vectors.
   my_tree = RTree(feature_vectors)

   # Suppose that we have an interesting trajectory whose end-to-end distance
   # is 1000 km but traveled a total of 2000 km -- that is, there was some
   # significant wandering involved. We want to find similar trajectories.

   interesting_feature_vector = convert_to_feature_vector([1000, 2000])

   # Case 1: We want the 10 nearest neighbors.
   nearest_neighbor_indices = my_tree.find_nearest_neighbors(
                                interesting_feature_vector, 10
                                )

   # Case 2: We want all the points with end-to-end distance between
   # 950 and 1050 km but total distance between 1900 and 5000 km.

   search_box_min = convert_to_feature_vector([950, 1900])
   search_box_max = convert_to_feature_vector([1050, 5000])

   similar_indices = my_tree.find_points_in_box(
                                    search_box_min,
                                    search_box_max
                                    )

   # The contents of nearest_neighbor_indices and similar_indices are
   # indices into the list of feature vectors. Because the feature
   # vectors are stored in the same order as the list of input
   # trajectories, we can also use them as indices back into the
   # list of trajectories.

.. _user-guide-python-airports-ports:

Retrieving Airport and Port Information
=======================================

Tracktable includes data bases of worldwide airports
and maritime ports which can be used for rendering, data
generation and analytics. Rendering guides can be found
on the :ref:`Rendering <user-guide-python-rendering>` page
and in our :ref:`notebook tutorials <notebook_tutorials>` while data generation guides can be found on
the :ref:`Data Generation <Python_Data_Generation_Example>` page.
Both airport and port modules have convient functions for retrieving
information from their respective databases, these are outlined below.

Airports
--------

.. code-block:: python
   :caption: Retrieve All Airports In Database
   :linenos:

    from tracktable.info import airports
    all_airports = airports.all_airports()


.. code-block:: python
   :caption: Airport Information Retrieval By Name
   :linenos:

    from tracktable.info import airports
    abq_airport = airports.airport_information("ABQ")

.. code-block:: python
   :caption: Airport Information Retrieval By Rank
   :linenos:

    from tracktable.info import airports
    abq_airport = airports.airport_size_rank("ABQ")

Ports
-----

.. code-block:: python
   :caption: Retrieve All Ports In Database
   :linenos:

   from tracktable.info import ports
   all_ports = ports.all_ports

.. code-block:: python
   :caption: Port Information Retrieval By Name
   :linenos:

    from tracktable.info import ports
    alexandria_port = ports.port_information("Alexandria")

.. code-block:: python
   :caption: Port Information Retrieval By Name And Specific Country
   :linenos:

    from tracktable.info import ports
    newport_port = ports.port_information("Newport", country='United Kingdom')

.. code-block:: python
   :caption: Port Information Retrieval By A Port's Alternate Name
   :linenos:

    from tracktable.info import ports
    new_shoreham_port = ports.port_information("New Shoreham")

.. code-block:: python
   :caption: Port Information Retrieval By A Port's World Port Index Number
   :linenos:

    from tracktable.info import ports

    # WPI number can be str or int
    newcastle_port = ports.port_information("53610")
    newcastle_port = ports.port_information(53610)

.. code-block:: python
   :caption: Retrieve All Ports For A Specific Country
   :linenos:

    from tracktable.info import ports
    united_states_ports = ports.all_ports_by_country("United States")

.. code-block:: python
   :caption: Retrieve All Ports For A Specific Body Of Water
   :linenos:

    from tracktable.info import ports
    pacific_ocean_ports = ports.all_ports_by_water_body("Pacific Ocean")

.. code-block:: python
   :caption: Retrieve All Ports For A Specific World Port Index Region
   :linenos:

    from tracktable.info import ports

    # Any of the following will work when retrieving ports by WPI region
    wpi_region_wales_ports = ports.all_ports_by_wpi_region("Wales -- 34710")

    wpi_region_wales_ports = ports.all_ports_by_wpi_region("Wales")

    wpi_region_wales_ports = ports.all_ports_by_wpi_region("34710")

    wpi_region_wales_ports = ports.all_ports_by_wpi_region(34710)

.. code-block:: python
   :caption: Retrieve All Ports Within A Specified Bounding Box
   :linenos:

    from tracktable.domain.terrestrial import BoundingBox
    from tracktable.info import ports

    # Ports around Florida
    bbox = BoundingBox((-88, 24), (-79.5, 31))
    bounding_box_ports = ports.all_ports_within_bounding_box(bbox)