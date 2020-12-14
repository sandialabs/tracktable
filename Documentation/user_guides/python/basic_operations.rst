.. _userguide-python-basic-ops:

================
Basic Operations
================

.. _userguide-python-point-ops:

--------------------
Operations On Points
--------------------

The module :py:mod:`tracktable.core.geomath` has most of the
operations we want to perform on two or more points. Here are a few
common ones, a comprehensive list of operations can be found in
the :ref:`geomath reference documentation <python_geomath_reference>`.
These operations work with both :py:class:`BasePoint` and :py:class:`TrajectoryPoint`
unless otherwise noted.

* ``distance(A, B)``: Compute distance between A and B
* ``bearing(origin, destination)``: Compute the bearing from the origin to the destination
* ``speed_between(here, there)``: Compute speed between two TrajectoryPoints
* ``signed_turn_angle(A, B, C)``: Angle between vectors AB and BC
* ``unsigned_turn_angle(A, B, C)``: Absolute value of angle between vectors AB and BC

.. _userguide-python-annotations:

-----------
Annotations
-----------

Once we have points or trajectories in memory we may want to
annotate them with derived quantities for analysis or rendering. For
example, we might want to color an airplane's trajectory using its
climb rate to indicate takeoff, landing, ascent and descent. we
might want to use acceleration, deceleration and rates of turning to
help classify moving objects.

The :py:mod:`tracktable.feature.annotations` module contains functions to do
perform these operations. Every feature defined in that package has two functions
associated with it: a ``calculator`` and an ``accessor``. The calculator
computes the values for a feature and stores them in the trajectory.
The accessor takes an already-annotated trajectory and returns a
1-dimensional array containing the values of the already-computed
feature. This allows us to attach as many annotations to a
trajectory as we like and then select which one to use (and how) at
render time.

.. code-block:: python
   :caption: Adding Progress Indicator To Trajectories
   :linenos:

    from tracktable.feature import annotations

    point_filename = args.point_data_file[0]
    field_assignments = extract_field_assignments(vars(args))

    with open(point_filename, 'r') as infile:
        logger.info('Loading points and building trajectories.')
        trajectories = list(
            trajectories_from_point_file(
                infile,
                object_id_column=args.object_id_column,
                timestamp_column=args.timestamp_column,
                coordinate0_column=args.coordinate0,
                coordinate1_column=args.coordinate1,
                string_fields=field_assignments['string'],
                real_fields=field_assignments['real'],
                time_fields=field_assignments['time'],
                comment_character=args.comment_character,
                field_delimiter=args.delimiter,
                separation_distance=args.separation_distance,
                separation_time=datetime.timedelta(minutes=args.separation_time),
                minimum_length=args.minimum_length,
                domain=args.domain)
            )
        # Add the 'progress' annotation to all of our trajectories so
        # we have some way to color them
        trajectories = [annotations.progress(t) for t in trajectories]


.. code-block:: python
   :caption: Retrieving Accessor For Given Annotation
   :linenos:

    from tracktable.feature import annotations

    if trajectory_color_type == 'scalar':
        annotator = annotations.retrieve_feature_function(trajectory_color)

        def annotation_generator(traj_source):
            for trajectory in traj_source:
                yield(annotator(trajectory))

        trajectories_to_render = annotation_generator(trajectory_source)
        scalar_generator = annotations.retrieve_feature_accessor(trajectory_color)
        colormap = trajectory_colormap

.. _userguide-python-analysis:

--------
Analysis
--------
Once the points or trajectories have been generated and annotated we need
to perform analysis to determine information about the points or trajectories
such as clustering, distance geometry or nearest neighbors.

The :py:mod:`tracktable.analysis` module contains the following submodules necessary to
to perform these types of analyses on points or trajectories.

* The :py:mod:`tracktable.analysis.assemble_trajectories` submodule will take a set of points
  and combine them into a trajecotry sorted by non-decreasing timestamp.
* The :py:mod:`tracktable.analysis.dbscan` submodule will perform the density-based spatial
  clustering of applications with noise analysis to determine the clustering of the
  feature vector points.
* The :py:mod:`tracktable.analysis.distance_geometry` submodule will
  compute the multilevel distance geometry for a trajectory based on either ``length``
  or ``time``.
* The :py:mod:`tracktable.analysis.rtree` submodule will generate an rtree that
  will compute the nearest neighbors based on provided points within a clustering box.


.. _python-trajectory-assembly:

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

This is common enough that Tracktable includes a filter
(:py:class:`tracktable.analysis.assemble_trajectories.AssembleTrajectoryFromPoints`)
to perform the assembly starting from a Python iterable of points
sorted by non-decreasing timestamp. We can specify two parameters that
control when to start a new trajectory:

* ``separation_time``: A :py:class:`datetime.timedelta` specifying the
  longest permissible gap between points in the same trajectory. Any
  gap longer than this will start a new trajectory.

* ``separation_distance``: A ``float`` value representing the
  maximum permissible distance (in kilometers) between two points in
  the same trajectory. Any gap longer than this will start a new trajectory.

We can also specify a ``minimum_length``. Trajectories with fewer than
this many points will be silently discarded.

.. code-block:: python
   :caption: Trajectory Assembly
   :linenos:

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

	for traj in trajectory_assembler.trajectories():
		# process trajectories here


.. _python-dbscan:

DBSCAN Clustering
-----------------

The :py:mod:`tracktable.analysis.dbscan` module is responsible for performing
density based clustering for any given set of feature vectors points for a given search area.
The number of points that define a cluster can be adjusted as needed.

.. code-block:: python
   :caption: DBSCAN Clustering
   :linenos:

    from tracktable.analysis.dbscan import compute_cluster_labels

    builder = AssembleTrajectoryFromPoints()
    builder.input = reader
    builder.minimum_length = 5
    builder.minimum_distance = 100
    builder.minimum_time = 20

    all_trajectories = list(builder)

    # Get feature vectors for each trajectory describing their distance geometry
    num_control_points = 4
    feature_vectors = [distance_geometry_signature(trajectory, num_control_points, True)
                    for trajectory in all_trajectories]

    # DBSCAN needs two parameters
    #  1. Size of the box that defines when two points are close enough to one another to
    #     belong to the same cluster.
    #  2. Minimum number of points in a cluster
    #
    signature_length = len(feature_vectors[0])

    # This is the default search box size. Feel free to change to fit your data.
    search_box_span = [0.01] * signature_length
    minimum_cluster_size = 5

    cluster_labels = compute_cluster_labels(feature_vectors, search_box_span, minimum_cluster_size)

.. _python-distance-geometry:

Distance Geometry
-----------------

The :py:mod:`tracktable.analysis.distance_geometry` module is responsible for computing
the mutilevel distance geometry signiture of a given trajectory sampled by ``length`` or ``time``.
Each level *d* approximates the input trajectory with *d* equal-length line segments.
The distance geometry values for that level are the lengths of all *d* line segments,
normalized to lie between 0 and 1. A value of 1 indicates the length of the entire trajectory.
The D-level distance geometry for a curve will result in ``(D * (D+1)) / 2``  separate values.

.. code-block:: python
    :caption: Distance Geometry by Distance and Time
    :linenos:

    from tracktable.analysis.distance_geometry import distance_geometry_by_distance
    from tracktable.analysis.distance_geometry import distance_geometry_by_time
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

.. _python-rtree:

RTree
-----

The :py:mod:`tracktable.analysis.rtree` module is responsible for generating an R-tree
data structure. An R-tree data structure is used for spatial access methods such as indexing
geographical coordinates or polygons. The functions within this module will generate the r-tree
structure as well as finding find all of the points within a given bounding box as well as find the
K nearest neighbor for a given search point.

.. code-block:: python
    :caption: RTree: Finding Points and Neighbors
    :linenos:

    from tracktable.analysis.rtree import RTree

    points = []

    for i in range(10):
        point = TrajectoryPoint()
        for d in range(len(point)):
            point[d] = i
        points.append(point)

    sample_point = TrajectoryPoint()
    for d in range(len(sample_point)):
        sample_point[d] = 4.5

    box_min = TrajectoryPoint()
    box_max = TrajectoryPoint()

    for d in range(len(box_min)):
        box_min[d] = 2.5
        box_max[d] = 6.5

    tree = RTree(points)

    points_in_box = tree.find_points_in_box(box_min, box_max)
    nearby_point_indices = tree.find_nearest_neighbors(sample_point, 4)
