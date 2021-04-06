.. _user-guide-cpp-basic-classes:

=============
Basic Classes
=============

.. _user-guide-cpp-domain:

-------
Domains
-------

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
   :header: "C++ Namespace", "Description"
   :widths: 30, 30

   "tracktable::domain::terrestrial", "Points in longitude/latitude space"
   "tracktable::domain::cartesian2d", "Points in flat 2D space"
   "tracktable::doamin::cartesian3d", "Points in flat 3D space"
   "tracktable::doamin::feature_vectors", "Collection of points in cartesian space with 2 to 30 dimensions"

Each domain defines several data types:

.. csv-table:: Domain Data Types
   :header: "C++ Class", "Description"
   :widths: 10, 40

   "base_point_type", "Bare point - just coordinates."
   "trajectory_point_type", "Point with coordinates, object ID, timestamp and user-defined properties."
   "trajectory_type", "Vector of trajectory points. Trajectories have their own user-defined properties."
   "linestring_type", "Vector of un-decorated points (base points)."
   "box_type", "Axis-aligned bounding box."
   "base_point_reader_type", "Read base points from a delimited text file."
   "trajectory_reader_type", "Read Trajectories from a delimited text file."
   "trajectory_point_reader_type", "Read Trajectory points from a delimited text file."

.. note:: In this guide we will assume you are working with
   ``trajectory_point_type`` data rather than ``base_point_type`` data
   and that the data is in the terrestrial domain.

.. _user-guide-cpp-timestamp:

---------
Timestamp
---------


There is a single timestamp class that is common across all point
domains. ``tracktable::Timestamp`` is a thinly disguised
``boost::posix_time::ptime``.

The ``tracktable`` namespace contains several
convenience methods for manipulating timestamps. A full list is located in
the :ref:`timestamp reference documentation <cpp_timestamp_reference>`.
We use the following ones most frequently.

* :cpp:func:`tracktable::time_from_string`: Convert a string into it's timestamp
  representation. By default this will produce the timestamp `March 5, 2014 at 13:44:06`
  from the string `"2014-03-05 13:44:06"`.

* :cpp:func:`tracktable::time_to_string`: Convert a timestamp into its string
  representation. By default this will produce the string `"2014-03-05 13:44:06"`
  from the timestamp `March 5, 2014 at 13:44:06`.

.. _user-guide-cpp-point-classes:

-----------
Point Types
-----------

Base Points
-----------

Within a domain, Tracktable uses the ``base_point_type`` to store a bare set of coordinates.
These behave like standard C++ objects with the appropriate getters and setters.

.. code-block:: c++
   :linenos:

   #include <tracktable/Domain/Terrestrial.h>

   typedef tracktable::domain::terrestrial::TerrestrialPoint TerrestrialPoint;

   int lon = 40;
   int lat = 50;

   TerrestrialPoint point;
   point.set_longitude(lon);
   point.set_latitude(lat);

.. _user-guide-cpp-trajectory-point:

Trajectory Points
-----------------

For assembling trajectories in a given domain, Tracktable uses
the ``trajectory_point_type`` class to store the (lon, lat)
coordinates as well as additional point information such as the
``timestamp`` and ``object_id``.

These are the main differences between ``base_point_type`` and ``trajectory_point_type``.

  1. Its coordinates, reference BasePoint above.
  2. An identifier for the moving object.
  3. A timestamp recording when the object was observed.

To generate and initialize a trajectory point you would do something like the code below:

.. code-block:: c++
   :linenos:

   #include <tracktable/Core/TrajectoryPoint.h>
   #include <tracktable/Core/Timestamp.h>

   typedef tracktable::domain::terrestrial::TerrestrialTrajectoryPoint TerrestrialTrajectoryPoint;

   std::string id = "FlightId";
   int lon = 40;
   int lat = 50;

   TerrestrialTrajectoryPoint point;
   point.set_object_id(id);
   point.set_longitude(lon);
   point.set_latitude(lat);
   point.set_timestamp(tracktable::time_from_string("2014-04-05 13:25:00"));

.. note:: The ``timestamp`` and ``object_id`` properties are specific to trajectory points.

You may want to associate other data with a point as well. For example:

.. code-block:: c++
   :linenos:

   point.set_property("altitude", 13400);
   point.set_property("origin, "ORD");
   point.set_property("destination", "LAX");
   point.set_property("departure_time", tracktable::time_from_string("2015-02-01 18:00:00"));

The trajectory can only hold values that are of ``numeric``, ``string`` or
``Timestamp`` type.

.. _user-guide-cpp-linestrings:

-----------
LineStrings
-----------

We include ``linestring_type`` for the ability to create ordered sequences of
points. ``linestring_type`` is analogous to ``base_point_type`` in that it has no
decoration at all. ``linestring_type`` just a vector of ``base_point_type`` points.

.. code-block:: c++
   :linenos:

   #include <tracktable/Domain/Terrestrial.h>

   typedef tracktable::domain::terrestrial::TerrestrialPoint TerrestrialPoint;
   typedef tracktable::domain::terrestrial::linestring_type LineStringTerrestrial;

   double corners[3][2] = {
      { 44, 33 },
      { 44.0769, 32.5862 },
      { 44, 33 }
   };

   LineStringTerrestrial linestring;
   linestring.push_back(TerrestrialPoint(corners[0]));
   linestring.push_back(TerrestrialPoint(corners[1]));
   linestring.push_back(TerrestrialPoint(corners[2]));

.. _user-guide-cpp-trajectories:

------------
Trajectories
------------

We include :cpp:class:`Trajectory` for ordered sequences of points.
:cpp:class:`Trajectory`  has its own ID (``trajectory_id``) as well as its own properties
array.

As with the point types above, each domain in Tracktable defines a
trajectory class. A trajectory is just a vector of points with a few
extra properties attached. A trajectory is an iterable just like
any other point sequence. Here is an example of creating a trajectory.

.. code-block:: c++
   :linenos:

   #include <tracktable/Domain/Terrestrial.h>

   using tracktable::domain::terrestrial::base_point_type;
   using tracktable::domain::terrestrial::trajectory_point_type;
   using tracktable::domain::terrestrial::trajectory_type;

   trajectory_point_type albuquerque;
   trajectory_point_type santa_fe;
   trajectory_point_type roswell;
   trajectory_type trajectory;

   std::string obj_id("GreenChileExpress001");
   albuquerque.set_longitude(-106.6100);
   albuquerque.set_latitude(35.1107);
   albuquerque.set_object_id(obj_id);
   albuquerque.set_timestamp(tracktable::time_from_string("2014-05-01 12:00:00"));

   santa_fe.set_longitude(-105.9644);
   santa_fe.set_latitude(35.6672);
   santa_fe.set_object_id(obj_id);
   santa_fe.set_timestamp(tracktable::time_from_string("2014-05-01 13:00:00"));

   roswell.set_longitude(-104.5281);
   roswell.set_latitude(33.3872);
   roswell.set_object_id(obj_id);
   roswell.set_timestamp(tracktable::time_from_string("2014-05-01 14:00:00"));

   trajectory.push_back(albuquerque);
   trajectory.push_back(santa_fe);
   trajectory.push_back(roswell);

.. note:: Tracktable expects that all points in a given trajectory will have the
   same object ID. Timestamps must not decrease from one point to the
   next.

There are several free functions defined on trajectories that do
useful things. We expect that the following will be used most often:

* ``point_at_time(TrajectoryT const& path, Timestamp const& time)``: Given a
  timestamp, interpolate between points on the trajectory to find the
  point at exactly the specified time. Timestamps before the
  beginning or after the end of the trajectory will return the start
  and end points, respectively. Tracktable will try to interpolate
  all properties that are defined on the trajectory points.

* ``subset_during_interval(TrajectoryT const& path, Timestamp const& start, Timestamp const& finish)``:
  Given a start and end timestamp, extract the subset of the
  trajectory between those two times. The start and end points will
  be at exactly the start and end times you specify. These will be
  interpolated if there are no points in the trajectory at precisely
  the right time. Points in between the start and end times will be
  copied from the trajectory without modification.
