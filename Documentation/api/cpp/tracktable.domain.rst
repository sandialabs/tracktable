========================
Tracktable Point Domains
========================


---------------
Module contents
---------------

Point domains are how we keep track of the different coordinate
systems and sets of units that points can use. For each domain we
specify (1) a native coordinate system, (2) an ordering for
coordinates if appropriate, and (3) units for measuring position,
distance and speed. In addition, each domain defines the following
types:

``base_point_type``: Point with coordinates only. This is descended
from tracktable::core::PointBase.

``trajectory_point_type``: Point with coordinates, timestamp, ID and
properties. This behaves like
tracktable::core::TrajectoryPoint<base_point_type>.

``linestring_type``: Vector of bare points. Boost's Geometry library
will recognize this as a model of Linestring.

``trajectory_type``: Vector of trajectory points with its own ID and
user-defined properties.

``base_point_reader_type``: PointReader for the domain's bare point
type. This is an instance of
``tracktable::rw::PointReader<base_point_type>``.

``trajectory_point_reader_type``: PointReader for the domain's
trajectory point type. This is an instance of
``tracktable::rw::PointReader<trajectory_point_type>``.

We also provide specializations of all the appropriate measurement
functions that return their results in the domain's units. This part
is done behind the scenes with templates and should be invisible to
the user. You simply call ``tracktable::distance()`` (for example)
and trust that the units will be kilometers (for the Terrestrial
domain).

In some cases, a geometric algorithm defined in one domain is
undefined in another. This happens with ``signed_turn_angle()``. A
signed angle is meaningful in two dimensions (the Terrestrial and
Cartesian2D domains) but not in three dimensions (the Cartesian3D
domain). Calls to ``signed_turn_angle()`` using 3D points will fail
to compile.

-------
Domains
-------

.. toctree::
   :maxdepth: 2

   tracktable.domain.2DCartesian.rst
   tracktable.domain.3DCartesian.rst
   tracktable.domain.FeatureVectors.rst
   tracktable.domain.Terrestrial.rst