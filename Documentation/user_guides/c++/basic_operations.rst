.. _user-guide-cpp-basic-ops:

================
Basic Operations
================

.. _user-guide-cpp-point-ops:

--------------------
Operations On Points
--------------------

The ``tracktable`` namespace has most of the
operations we want to perform on two or more points. Here are a few
common ones, a comprehensive list of operations can be found in
the :ref:`tracktable core detail reference documentation <cpp-api-core>`.
These operations work with both ``base_point_type`` and ``trajectory_point_type``
points unless otherwise noted.

* ``distance(Geometry1 const& from, Geometry2 const& to)``: Compute distance between from and to
* ``bearing(T const& from, T const& to)``: Compute the bearing from the origin to the destination
* ``speed_between(T const& start, T const& finish)``: Compute speed between two trajectory points
* ``signed_turn_angle(T const& a, T const& b, T const& c)``: Angle between vectors AB and BC
* ``unsigned_turn_angle(T const& a, T const& b, T const& c)``: Absolute value of angle between vectors AB and BC

.. _user-guide-cpp-analysis:

--------
Analysis
--------

Once the points or trajectories have been generated and annotated we need
to perform analysis to determine information about the points or trajectories
such as clustering, distance geometry, nearest neighbors or greatest/best fit circle.

The tracktable ``Analysis`` module contains the following components necessary to
to perform these types of analyses on points or trajectories.

* The :cpp:class:`AssembleTrajectories` class will take a set of points
  and combine them into a trajecotry sorted by non-decreasing timestamp.
* The :cpp:func:`cluster_with_dbscan` and :cpp:func:`build_cluster_membership_lists`
  functions will perform the density-based spatial clustering of applications with
  noise analysis to determine the clustering of the feature vector points.
* The :cpp:func:`distance_geometry_by_distance` and :cpp:func:`distance_geometry_by_time`
  functions will compute the multilevel distance geometry for a
  trajectory based on either ``distance`` or ``time``.
* The :cpp:func:`great_circle_fit_and_project_in_place`, :cpp:func:`great_circle_fit_and_project`,
  :cpp:func:`find_best_fit_plane` and :cpp:func:`project_trajectory_onto_plane`
  functions will generate a circle that best fits the given trajectory and projects it onto the
  specified plane.
* The :cpp:class:`RTree` class will generate an R-tree to efficiently
  compute the nearest neighbors based on provided points within a clustering box.


.. _cpp-trajectory-assembly:

Trajectory Assembly
-------------------

Creating trajectories from a set of points is simple conceptually but
logistically annoying when we write the code ourselves. The overall
idea is as follows:

1. Group points together by object ID and increasing timestamp.

2. For each object ID, connect one point to the next to form
   trajectories.

3. Break the sequence to create a new trajectory whenever it doesn't
   make sense to connect two neighboring points.

When assembling trajectories from a sequence of points
we can specify two parameters that control when to start a new trajectory:

* ``separation_time``: A ``boost::posix_time`` object specifying the
  longest permissible gap between points in the same trajectory. Any
  gap longer than this will start a new trajectory.

* ``separation_distance``: A ``float`` value representing the
  maximum permissible distance (in kilometers) between two points in
  the same trajectory. Any gap longer than this will start a new trajectory.

We can also specify a ``MinimumTrajectoryLength``. Trajectories with fewer than
this many points will be silently discarded.

.. code-block:: c++
   :caption: Trajectory Assembly
   :linenos:

    #include <tracktable/Domain/Terrestrial.h>
    #include <tracktable/Analysis/AssembleTrajectories.h>

    typedef tracktable::domain::terrestrial::trajectory_point_reader_type reader_type;
    typedef tracktable::domain::terrestrial::trajectory_type trajectory_type;
    typedef tracktable::AssembleTrajectories<trajectory_type, reader_type::iterator> assembler_type;

    reader_type point_reader;
    assembler_type trajectory_builder;

    trajectory_builder.set_separation_time(tracktable::minutes(20));
    trajectory_builder.set_separation_distance(100);
    trajectory_builder.set_minimum_trajectory_length(500);

    std::string filename = "point_data.csv";
    std::ifstream infile(filename.c_str());

    if (!infile)
      {
        std::cerr << "ERROR: Could not open file '" << filename << "'\n";
        return -1;
      }

    point_reader.set_input(infile);
    point_reader.set_object_id_column(0);
    point_reader.set_timestamp_column(1);
    point_reader.set_longitude_column(2);
    point_reader.set_latitude_column(3);

    trajectory_builder.set_input(point_reader.begin(), point_reader.end());

    for (assembler_type::iterator iter = trajectory_builder.begin(); iter != trajectory_builder.end(); ++iter)
      {
        // Process trajectories here
      }


.. _cpp-dbscan:

DBSCAN Clustering
-----------------

The DBSCAN module is responsible for performing box based
density based clustering for any given set of feature vector points
for a given search area. The number of points that define a cluster
can be adjusted as needed. Additional information
on DBSCAN clustering can be found at: https://en.wikipedia.org/wiki/DBSCAN

.. note:: Our implementation of DBSCAN is templated on point type and uses
   boost::geometry for all of its distance math. This means that it
   will automatically adapt to whatever coordinate system you're using
   for your points as long as Boost knows what to do with it.

   This is usually great. However, there are times when it will slow
   you down tremendously. For example, if you're clustering a bunch
   of points that are very close together on the surface of a sphere,
   you might do just fine by pretending that the space is Cartesian
   (flat) instead of spherical. That will run dramatically more
   quickly and with greater precision than the trigonometry necessary
   for doing distance computations on a sphere.

.. code-block:: c++
   :caption: DBSCAN Clustering
   :linenos:

    #include <tracktable/Analysis/ComputeDBSCANClustering.h>
    #include <tracktable/Domain/Terrestrial.h>

    typedef tracktable::domain::terrestrial::TerrestrialPoint TerrestrialPoint;

    TerrestrialPoint point_one;
    TerrestrialPoint point_two;
    std::vector<tracktable::domain::terrestrial::TerrestrialPoint> my_points;
    std::vector<std::pair<int, int>> cluster_labels;
    TerrestrialPoint search_box(0.5, 0.5);
    int min_cluster_size = 10;

    point_one.set_longitude(40);
    point_one.set_latitude(50);

    point_two.set_longitude(41);
    point_two.set_latitude(51);

    my_points.push_back(point_one);
    my_points.push_back(point_two);

    int num_clusters = cluster_with_dbscan<TerrestrialPoint>(
      my_points.begin(),
      my_points.end(),
      search_box,
      min_cluster_size,
      std::back_inserter(cluster_labels)
    );

.. _cpp-distance-geometry:

Distance Geometry
-----------------

The Distance Geometry module is responsible for computing
the mutilevel distance geometry signiture of a given trajectory sampled by ``distance`` or ``time``.
Each level *d* approximates the input trajectory with *d* equal-length line segments.
The distance geometry values for that level are the lengths of all *d* line segments,
normalized to lie between 0 and 1. A value of 1 indicates the length of the entire trajectory.
The D-level distance geometry for a curve will result in ``(D * (D+1)) / 2``  separate values.

.. code-block:: c++
    :caption: Distance Geometry by Distance and Time
    :linenos:

    #include <tracktable/Analysis/DistanceGeometry.h>
    #include <tracktable/Domain/Terrestrial.h>

    typedef tracktable::domain::terrestrial::trajectory_point_type TerrestrialTrajectoryPoint;
    typedef tracktable::domain::terrestrial::trajectory_type TerrestrialTrajectory;

    double terrestrial_coordinates[][2] = {
      {0, 80},
      {90, 80},
      {180, 80},
      {-90, 80},
      {0, 80},
      {-1000, -1000}
    };

    const char* timestamps[] = {
      "2000-01-01 00:00:00",
      "2000-01-01 02:00:00",
      "2000-01-01 03:00:00",
      "2000-01-01 04:00:00",
      "2000-01-01 06:00:00"
    };

    TerrestrialTrajectory trajectory;
    int i = 0;
    while (terrestrial_coordinates[i][0] > -1000)
    {
      TerrestrialTrajectoryPoint point;
      point.set_object_id("terrestrial_dg_test");
      point.set_longitude(terrestrial_coordinates[i][0],);
      point.set_latitude(terrestrial_coordinates[i][1]);
      point.set_timestamp(tracktable::time_from_string(timestamps[i]));

      trajectory.push_back(point);

      ++i;
    }

    std::vector<double> terrestrial_dg = tracktable::distance_geometry_by_time(trajectory, 4);

.. _cpp-great-fit-circle:

Great Fit Circle
----------------

The Great Fit Circle module is responsible for generating the great circle
that best fits each given trajectory or set of points with the option to
project the circle onto a specified plane. The functions in this module
provide options for generating and projecting great circles.

.. code-block:: c++
    :caption: Great Fit Circle and Projection
    :linenos:

    #include <tracktable/Analysis/GreatCircleFit.h>
    #include <tracktable/Domain/Terrestrial.h>

    using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
    using PointT = TrajectoryT::point_type;

    auto NUM_POINTS = 100u;
    auto HEADING_EAST = 90.0;
    auto HEADING_NORTH = 0.0;
    auto SPEED = 30.0;
    auto ALTITUDE = 1000.0;
    auto ZIG = 0.01;
    auto ZAG = -ZIG;
    auto NORMAL_TOLERANCE = 0.0001;

    // Generate points and accompanying trajectory

    auto p = tracktable::arithmetic::zero<PointT>();
    p.set_property("altitude", ALTITUDE);

    // Generator for a trajectory with a speed of .01(deg/s), an update interval of 60s and a heading of 90deg
    tracktable::ConstantSpeedPointGenerator generatorEast(p, tracktable::minutes(1), SPEED, HEADING_EAST);

    TrajectoryT hundredPointEast;

    for (auto i = 0u; i < NUM_POINTS; ++i) {
      hundredPointEast.push_back(generatorEast.next());
    }

    // Fit a circle

    auto normal = tracktable::find_best_fit_plane(hundredPointEast);

    // Project the circle onto a plane

    tracktable::project_trajectory_onto_plane(hundredPointEast, normal);

.. _cpp-rtree:

R-Tree
------

The :cpp:class:`RTree` class is responsible for generating an R-tree
data structure. An R-tree data structure is used for spatial access methods such as indexing
geographical coordinates or polygons. The functions within this module will generate the r-tree
structure as well as finding find all of the points within a given bounding box as well as find the
K nearest neighbor for a given search point.

.. code-block:: c++
    :caption: RTree: Finding Points and Neighbors
    :linenos:

    #include <tracktable/Analysis/RTree.h>
    #include <tracktable/Domain/Terrestrial.h>
    #include <boost/tuple/tuple.hpp>

    std::vector<tracktable::domain::terrestrial::base_point_type> base_points;

    // This function algorithmically creates a point grid that will produce an R-Tree structure
    create_point_grid<base_point_type>(1, 9, std::back_inserter(base_points));

    base_point_type search_point;
    for (unsigned int i = 0; i < search_point.size(); ++i)
      {
        search_point[i] = 0;
      }
    search_point[0] = -20;

    tracktable::RTree<base_point_type> rtree(base_points.begin(),
                                            base_points.end());

    std::vector<base_point_type> query_results_bare, query_results_pair, query_results_tuple;
    rtree.find_nearest_neighbors(
      search_point,
      1,
      std::back_inserter(query_results_bare)
    );

    rtree.find_nearest_neighbors(
        std::make_pair(search_point, 1000),
        1,
        std::back_inserter(query_results_pair)
      );

    rtree.find_nearest_neighbors(
        boost::make_tuple(search_point, 10000),
        1,
        std::back_inserter(query_results_tuple)
      );