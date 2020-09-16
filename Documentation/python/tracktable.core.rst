.. _module-tracktable-core:

======================
tracktable.core module
======================

----------
Submodules
----------

.. toctree::
   :maxdepth: 2

   tracktable.core.compatibility
   tracktable.core.conversions
   tracktable.core.core_types
   tracktable.core.geomath.rst
   tracktable.core.log.rst
   tracktable.core.misc
   tracktable.core.register_core_types
   tracktable.core.simple_timezone.rst
   tracktable.core.test_utilities
   tracktable.core.testutils
   tracktable.core.timestamp.rst


---------------
Module contents
---------------

.. automodule:: tracktable.core
    :members:
    :undoc-members:
    :show-inheritance:



.. py:class:: tracktable.core.TrajectoryPoint(longitude=0, latitude=0, altitude=0)
   :module: tracktable.core

   Bases: :class:`object`

   This is the core geographic point class for Tracktable.  NOTE: The
   'Bases' is not accurate but will do for now.

   This is the core geographic point class for Tracktable.  You will
   not instantiate this yourself: instead, use
   tracktable.domain.<domain>.TrajectoryPoint.

   TrajectoryPoint specifies a point on the surface of a sphere that
   is annotated with an object ID, coordinates, timestamp, and
   possibly other attributes (commonly altitude, heading and speed).
   Any or all of these may be left uninitialized depending on the
   user's actions although a point without coordinates is not
   especially useful.

   We require that the coordinates be in degrees of longitude and
   latitude.  The units on all numeric properties are user-defined,
   although altitude will usually be in either feet or meters
   (depending on your data source) and heading will usually be in
   degrees clockwise from due north.

   The (longitude, latitude) coordinates of a TrajectoryPoint
   object are accessed as if the object were a Python array,
   using the ``[]`` operator::

     from tracktable.domain.terrestrial import TrajectoryPoint

     my_point = TrajectoryPoint()
     longitude = 30
     latitude = 40
     my_point[0] = longitude
     my_point[1] = latitude

   Longitude is always coordinate 0 and latitude is always coordinate 1.
   We choose this ordering for consistency with the 2D Cartesian domain
   where the X coordinate is always at position 0 and the Y coordinate is
   at position 1. Longitude is between -180 and 180 and
   latitude is between -90 and 90.

   .. note:: TrajectoryPoint is implemented in C++ and exposed to
             Python via the Boost.Python module.  I will include a
             link to the C++ class definition as soon as I figure out
             how to do so within Sphinx, Breathe and Napoleon.

   .. attribute:: object_id

		  *string*

		  Object ID of entity referred to by this point

   .. attribute:: timestamp

		  *datetime*

		  Timestamp corresponding to this point

   .. attribute:: properties

		  *dict*

		  User-defined properties.  Names are strings, values
		  are numbers, timestamps and strings.  All properties
		  other than object ID, coordinates, and timestamp
		  will be stored here.

   .. py:method:: TrajectoryPoint.has_property(property_name)
      :module: tracktable.core

      Check to see whether an entry is present in the property map

      :param property_name: Name of property to look for

      :type property_name: string

      :returns: True or false depending on whether property was found


.. py:class:: tracktable.core.Trajectory()
   :module: tracktable.core

   Bases: :class:`object`

   Ordered sequence of timestamped points.

   This class is the heart of most of what Tracktable does.  It
   implements an ordered sequence of TrajectoryPoint objects, each of
   which has an ID, coordinates and a timestamp.  Those compose a
   trajectory.  All points in a single Trajectory should have the
   same `object_id`.

   .. note:: The Trajectory class is implemented in C++ and exposed to
             Python via the Boost.Python module.  We use the vector
             indexing suite from Boost to make a trajectory act like a
             list of points.

   .. attribute:: object_id

		  *string*

		  ID of object described in this trajectory.  This
		  will be the string "(empty)" if the trajectory does
		  not contain any points.

   .. attribute:: start_time

                  *datetime*

		  Timestamp of the first point in the trajectory.
		  This will be invalid if the trajectory contains no
		  points.

   .. attribute:: end_time

		  *datetime*

		  Timestamp of the last point in the trajectory.  This
		  will be invalid if the trajectory contains no
		  points.

   .. py:method:: Trajectory.subset_in_window(start_time, end_time)
      :module: tracktable.core

      Compute the subset of a trajectory between two timestamps.

      We often want to clip a trajectory to just the part that fits
      within a certain window of time.  This method interpolates new
      start and end positions that fall exactly at `start_time` and
      `end_time` and includes between them all of the points in the
      trajectory that occur within the specified interval.  If the
      trajectory does not intersect the interval at all then the
      return value will be an empty Trajectory.

      :param start_time: Beginning of time window

      :type start_time: datetime

      :param end_time: End of time window

      :type end_time: datetime

      :returns: New Trajectory with endpoints at `start_time` and `end_time`

   .. py:method:: Trajectory.point_at_time(when)
      :module: tracktable.core

      Find the position on a trajectory at a specified time.

      If the specified time falls between points on the trajectory
      then we will interpolate as needed.  If you ask for a point
      before the trajectory begins or after the trajectory ends you
      will get the first or last point of the trajectory respectively.

      :param when: Time at which to evaluate trajectory

      :type when: datetime

      :returns: TrajectoryPoint at specified time

   .. py:method:: Trajectory.recompute_speed()
      :module: tracktable.core

      Compute speeds at each point of a trajectory.

      Sometimes the speed measurements that come with a data set are
      noisy or outright wrong.  Sometimes they're missing.  This
      method is for those situations.  When you call it, it will use
      the position and timestamp data to compute a speed at each point
      in the trajectory.  This value can be accessed with
      :code:`my_speed = my_trajectory[i].properties['speed']`.

      .. :note:: If your position/timestamp measurements are also bad
                 then the results from this method will be less than
                 ideal.

   .. py:method:: Trajectory.recompute_heading()
      :module: tracktable.core

      Compute headings at each point of a trajectory.

      The heading at each point of a trajectory is the direction to
      the next point.  The heading at the very last point is the same
      as the heading at the penultimate point.  This value can be accessed with
      :code:`my_heading = my_trajectory[i].properties['heading']`.


   .. py:method:: Trajectory.intersects_box(southwest_corner, northeast_corner)
      :module: tracktable.core

      Test to see whether a trajectory intersects a rectangle in longitude/latitude space.

      A trajectory intersects a box if any of its coordinates falls within the box.

      :param southwest_corner: Southwest corner of box of interest

      :type southwest_corner: TrajectoryPoint or (longitude, latitude) tuple

      :param northwest_corner: Northwest corner of box of interest

      :type northwest_corner: TrajectoryPoint or (longitude, latitude) tuple

      :returns: True or False

      .. :warning:: This will miss cases where one segment of the
                    trajectory intersects the box but none of its
                    vertices are inside.

      .. :warning:: We cannot yet handle bounding boxes that cross the
                    map discontinuity at longitude +/- 180 degrees.
                    Long trajectories that cross this discontinuity
                    are also tough.  At the moment we automatically
                    return `true` for any trajectory that spans more
                    than 90 degrees of longitude as a temporary fix.

   .. py:staticmethod:: Trajectory.from_position_list(points)
      :module: tracktable.core

      Assemble a Trajectory from a list of TrajectoryPoints.

      :param points: List of TrajectoryPoint objects

      :type points: list

      :returns: New Trajectory instance containing copies of all supplied points




.. py:class:: tracktable.core.Timestamp()
   :module: tracktable.core

   Convenience methods for working with timestamps.

   Recall that a Timestamp is just a timezone-aware
   :py:class:`datetime.datetime` object.  That gives us all of the
   standard Python date/time functions to use
   for manipulating them.  As a result we only need convenience
   functions to take care of the awkward parts: turning strings into
   timestamps, timestamps into strings, and imbuing a naive
   ``datetime`` object with a time zone.

   .. py:staticmethod:: Timestamp.beginning_of_time()
      :module: tracktable.core

      Return a timestamp equal to January 1, 1400.  No valid timestamp
      should ever be this old.

      :returns: Timestamp object set to the first day of 1400

   .. py:staticmethod:: Timestamp.from_struct_time(mytime)
      :module: tracktable.core

      Construct a datetime from a time.struct_time object.

      :param mytime: Source time

      :type mytime: :py:class:`time.struct_time`

      :returns: An aware datetime object imbued with ``tracktable.core.timestamp.DEFAULT_TIMEZONE``

   .. py:staticmethod:: Timestamp.from_dict(mydict)
      :module: tracktable.core

      Construct a datetime from a dict with named elements.

      :param mydict: Dict with zero or more of 'hour', 'minute',
            'second', 'year', 'month', 'day', and 'utc_offset'
            entries.  Missing entries will be set to their minimum
            legal values.

      :type mydict: :py:class:`dict`

      :returns: An aware datetime object imbued with
            ``tracktable.core.DEFAULT_TIMEZONE`` unless a 'utc_offset'
            value is specified, in which case the specified time zone
            will be used instead.

   .. py:staticmethod:: Timestamp.from_datetime(mytime)
      :module: tracktable.core

      Convert a :py:class:`datetime <datetime.datetime>` into an
      aware timestamp.

      :param mytime: ``datetime`` object to convert

      :type mytime: :py:class:`datetime.datetime`

      :returns: ``datetime`` that will definitely have a time zone
                  attached.  If the input already has a time zone then
                  it will be returned without modification.  If not, a
                  new timestamp will be created with the supplied
                  date/time and the default time zone.

   .. py:staticmethod:: Timestamp.from_any(thing)
      :module: tracktable.core

      Try to construct a timestamp from whatever we're given.

      The possible inputs can be:

      * a Python datetime (in which case we just return a copy of the input)

      * a string in the format ``2013-04-05 11:23:45``, in which case
        we will assume that it resides in ``timestamp.DEFAULT_TIMEZONE``

      * a string in the format ``2013-04-05 11:23:45-05``, in which case we will
        assume that it's UTC-5 (or other time zone, accordingly)

      * a string in the format ``2013-04-05T11:23:45`` or
        ``2013-04-05T11:23:45-05`` -- just like above but with a T in
        the middle instead of a space

      * a string in the format ``20130405112345`` - these are assumed
        to reside in the default time zone

      * a string in the format ``MM-DD-YYYY HH:MM:SS``

      * a string such as ``08-Aug-2013 12:34:45`` where 'Aug' is the
        abbreviated name for a month in your local environment

      * a dict containing at least ``year``, ``month``, ``day`` entries
        and optionally ``hour``, ``minute``, ``second`` and ``utc_offset``

      Internally this method dispatches to all of the other
      ``Timestamp.from_xxx()`` methods.

      :param thing: Thing to try to convert to a timestamp

      :returns: Timezone-aware :py:class:`datetime <datetime.datetime>` object

   .. py:staticmethod:: Timestamp.to_string(dt, format_string='%Y-%m-%d %H:%M:%S', include_tz=False)

      Create a string from a timestamp.

      Format contents as a string, by default formatted as
      ``2013-04-21 14:45:00``.  You may supply an argument
      ``format_string`` if you want it in a different form.  See the
      documentation for :py:func:`datetime.strftime` for information on what this
      format string looks like.

      :param dt: Timestamp object to stringify

      :type dt: :py:class:`datetime.datetime`

      :param format_string: String to pass to :py:func:`datetime.strftime`

      :type format_string: string

      :param include_tz: Whether or not to append timezone as UTC offset

      :type include_tz: Boolean

      :returns: String representation of timestamp
