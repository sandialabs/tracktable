.. _user-guide-python-basic-classes:

=============
Basic Classes
=============

.. _user-guide-python-domain:

----------------------------
Domains (Coordinate Systems)
----------------------------

Tracktable operates on points, timestamps and trajectories. Since
points and trajectories are meaningless without a coordinate system,
we instantiate points and trajectories from a *domain*. Each domain
provides several different data types and a standard set of units. By
design, it is difficult to mix points and trajectories from different
domains. While we cannot prevent you entirely from mixing up (for
example) kilometers and miles when computing distances, we can at
least try to make it difficult.

Tracktable includes the following domains:

.. csv-table:: Available Point Domains
   :header: "Python Module", "Description"
   :widths: 30, 30

   "tracktable.domain.terrestrial", "Points in longitude/latitude space"
   "tracktable.domain.cartesian2d", "Points in flat 2D space"
   "tracktable.domain.cartesian3d", "Points in flat 3D space"
   "tracktable.domain.feature_vectors", "Collection of points in Cartesian space with 2 to 30 dimensions"

Each domain defines several data types:

.. csv-table:: Domain Data Types
   :header: "Python Class", "Description"
   :widths: 10, 40

   "BasePoint", "Bare point - just coordinates."
   "TrajectoryPoint", "Point with coordinates, object ID, timestamp and user-defined properties."
   "Trajectory", "Vector of trajectory points. Trajectories have their own user-defined properties."
   "LineString", "Vector of un-decorated points (base points)."
   "Box", "Axis-aligned bounding box."
   "BasePointReader", "Read BasePoints from a delimited text file."
   "BasePointWriter", "Write BasePoints to a delimited text file."
   "TrajectoryPointReader", "Read TrajectoryPoints from a delimited text file."
   "TrajectoryPointWriter", "Write TrajectoryPoints to a delimited text file."
   "TrajectoryReader", "Read Trajectories from a delimited text file."
   "TrajectoryWriter", "Write Trajectories to a delimited text file."

We provide rendering support for the terrestrial and 2D Cartesian
domains via Matplotlib and Cartopy. Rendering support for 3D points
and trajectories is still an open issue. Given the limited support
for 3D data in Matplotlib we may delegate this job to another library.
Exactly which library we might choose is open for discussion.

.. _user-guide-python-timestamp:

---------
Timestamp
---------

There is a single timestamp class that is common across all domains.
This is a timezone-aware :py:class:`datetime.datetime`.

The :py:class:`tracktable.core.Timestamp <tracktable.core.timestamp.Timestamp>` class contains several
convenience methods for manipulating timestamps. A full list is in
the :ref:`timestamp reference documentation <python_timestamp_reference>`.
We use the following ones most frequently.

* :py:func:`Timestamp.from_any <tracktable.core.timestamp.Timestamp.from_any>`: Try to convert whatever argument we
  supply into a timestamp. The input can be a :py:class:`dict`, a
  :py:class:`datetime <datetime.datetime>`, a string in the format
  ``YYYY-MM-DD HH:MM:SS`` or ``YYYY-MM-DD HH:MM:SS+ZZ`` (for a time
  zone offset from UTC).

* :py:func:`Timestamp.to_string <tracktable.core.timestamp.Timestamp.to_string>`: Convert a timestamp into its string
  representation. By default this will produce a string like
  ``2014-08-28 13:23:45``. Optional arguments to the function will
  allow us to change the output format and include a timezone
  indicator.

.. _user-guide-python-point-classes:

-------------
Point Classes
-------------

Base Points
-----------

Within a domain, Tracktable uses the ``BasePoint`` class to store a bare set of (lon, lat) coordinates.
These :py:class:`BasePoint` coordinates behave like lists
in that we use square brackets, ``[]``, to set and get coordinates. For example:

.. code-block:: python
   :linenos:

   from tracktable.domain.terrestrial import BasePoint

   my_point = BasePoint()
   my_point[0] = my_longitude
   my_point[1] = my_latitude

   # You could also assign the coordinates in the constructor:
   # my_point = BasePoint(my_longitude, my_latitude)

   longitude = my_point[0]
   latitude = my_point[1]

Longitude is always coordinate 0 and latitude is always coordinate 1.
We choose this ordering for consistency with the 2D Cartesian domain
where the X coordinate is always at position 0 and the Y coordinate is
at position 1.

.. _user-guide-python-trajectory-point:

Trajectory Points
-----------------

For assembling trajectories in a given domain, Tracktable uses
the :py:class:`TrajectoryPoint` class to store the (lon, lat)
coordinates as well as additional point information such as the
``timestamp`` and ``object_id``.


Each :py:class:`TrajectoryPoint` has the following properties:

  1. Coordinates (inherited from BasePoint)
  2. An identifier for the moving object
  3. A timestamp for this observation of the object's position

The following code shows how to initialize a trajectory point:

.. code-block:: python
   :linenos:

   from tracktable.domain.terrestrial import TrajectoryPoint
   from tracktable.core import Timestamp

   longitude = 50
   latitude = 40

   my_point = TrajectoryPoint()
   my_point[0] = longitude
   my_point[1] = latitude

   # As with BasePoint, you can also set coordinates in the
   # constructor:
   # my_point = TrajectoryPoint(longitude, latitude)

   my_point.object_id = 'FlightId'
   my_point.timestamp = Timestamp.from_any('2014-04-05 13:25:00')

You may want to associate other data with a point as well. For example,
aircraft trajectories often have altitude and information about the
flight's origin and destination:

.. code-block:: python
   :linenos:

   my_point.properties['altitude'] = 13400
   my_point.properties['origin'] = 'ORD'
   my_point.properties['destination'] = 'LAX'
   my_point.properties['departure_time'] = Timestamp.from_any('2015-02-01 18:00:00')

For the most part you can treat the properties array like a Python
:py:class:`dict`. However, it can only hold values that are of ``float``, ``string`` or
``Timestamp`` type.

.. _user-guide-python-linestrings:

-----------
LineStrings
-----------

We include :py:class:`LineString` for ordered sequences of
points. :py:class:`LineString` is analogous to :py:class:`BasePoint` in
that it has no decoration (as in no additional data that is unrelated
to the points longitude and latitude) at all. It is just a sequence of points.

.. code-block:: python
   :linenos:

    from tracktable.domain.terrestrial import BasePoint

    point_one = BasePoint(50, 40)
    point_two = BasePoint(60, 40)

    linestring = []
    linestring.append(point_one)
    linestring.append(point_two)

.. _user-guide-python-trajectories:

------------
Trajectories
------------

We provide :py:class:`Trajectory` for ordered sequences of points.
:py:class:`Trajectory` has its own ID (``trajectory_id``) as well as
its own properties array. You do not need to supply a trajectory ID:
it is computed automatically from the object ID, start time, and end time.

As with the point classes above, each domain in Tracktable defines a
trajectory class. Trajectories can be treated like Python lists:
indexing, slicing, insertion and removal all work as they do with
an ordinary Python ``list``.

.. code-block:: python
   :caption: Example: Assemble Trajectory from Points
   :linenos:

   # Populate a trajectory from scratch
   from tracktable.domain.terrestrial import Trajectory, TrajectoryPoint
   import datetime

   point1 = TrajectoryPoint(50, 40)
   point1.object_id = "A"
   point1.timestamp = datetime.datetime.now()

   point2 = TrajectoryPoint(60, 30)
   point2.object_id = "A"
   point2.timestamp = point1.timestamp + datetime.timedelta(hours=3)

   traj = Trajectory()
   traj.append(point1)
   traj.append(point2)


.. code-block:: python
   :caption: Assemble Trajectory from List of Points
   :linenos:

   from tracktable.domain.terrestrial import Trajectory

   # Assume that 'mypoints' is a list of TrajectoryPoints that you
   # have populated somewhere else in your code. You can create
   # a Trajectory from that list in one call:

   traj = Trajectory.from_position_list(mypoints)


.. note:: Tracktable expects that all points in a given trajectory
   will have the same object ID. Timestamps must not decrease from one
   point to the next.

There are several free functions defined on trajectories that do
useful things. We expect that the following will be used most often:

* ``point_at_time(trajectory: Trajectory, when: Timestamp)``: Given a
  timestamp, interpolate between points on the trajectory to find the
  point at exactly the specified time. Timestamps before the
  beginning or after the end of the trajectory will return the start
  and end points, respectively. Tracktable will try to interpolate
  all properties that are defined on the trajectory points.

* ``subset_during_interval(trajectory: Trajectory, start, end: Timestamp)``:
  Given a start and end timestamp, extract the subset of the
  trajectory between those two times. The start and end points will
  be at exactly the start and end times you specify. These will be
  interpolated if there are no points in the trajectory at precisely
  the right time. Points in between the start and end times will be
  copied from the trajectory without modification.

* ``recompute_speed(trajectory: Trajectory, target_attribute_name='speed')``:
  Compute new values for
  the ``speed`` numeric property at each point given
  the position and timestamp attributes. These are convenient if our
  original data set lacks speed information or if the original
  values are corrupt.
