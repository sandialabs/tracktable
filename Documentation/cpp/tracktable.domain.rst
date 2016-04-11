========================
Tracktable Point Domains
========================

Point domains are how we keep track of the different coordinate
systems and sets of units that points can use.  For each domain we
specify (1) a native coordinate system, (2) an ordering for
coordinates if appropriate, and (3) units for measuring position,
distance and speed.  In addition, each domain defines the following
types:

``base_point_type``: Point with coordinates only.  This is descended
from tracktable::core::PointBase.

``trajectory_point_type``: Point with coordinates, timestamp, ID and
properties.  This behaves like
tracktable::core::TrajectoryPoint<base_point_type>.

``linestring_type``: Vector of bare points.  Boost's Geometry library
will recognize this as a model of Linestring.

``trajectory_type``: Vector of trajectory points with its own ID and
user-defined properties.

``base_point_reader_type``: PointReader for the domain's bare point
type.  This is an instance of
``tracktable::io::PointReader<base_point_type>``.

``trajectory_point_reader_type``: PointReader for the domain's
trajectory point type.  This is an instance of
``tracktable::io::PointReader<trajectory_point_type>``.

We also provide specializations of all the appropriate measurement
functions that return their results in the domain's units.  This part
is done behind the scenes with templates and should be invisible to
the user.  You simply call ``tracktable::distance()`` (for example)
and trust that the units will be kilometers (for the Terrestrial
domain).

In some cases, a geometric algorithm defined in one domain is
undefined in another.  This happens with ``signed_turn_angle()``.  A
signed angle is meaningful in two dimensions (the Terrestrial and
Cartesian2D domains) but not in three dimensions (the Cartesian3D
domain).  Calls to ``signed_turn_angle()`` using 3D points will fail
to compile.

.. todo: Document which measures are implemented for each domain


Terrestrial Domain
------------------

Specification
^^^^^^^^^^^^^

The Terrestrial domain (``tracktable::domain::terrestrial``) concerns
points on the surface of the Earth.  These points are located using
longitude and latitude.  In Tracktable, longitude and latitude are
always measured in degrees and longitude always comes first.  We
prefer to let longitude range from -180 to 180 but the underlying math
doesn't care.

Units
^^^^^

Position in the terrestrial domain is measured in degrees of longitude
and latitude.  Longitude is always coordinate 0 and latitude is always
coordinate 1.  Points are presumed to lie on the surface of the Earth.
If you want to include altitude, use the user-defined properties.

Distances are measured in kilometers.  Speeds are measured in
kilometers per hour.



2D Cartesian Domain
-------------------

Specification
^^^^^^^^^^^^^

The 2D Cartesian domain (``tracktable::domain::cartesian2d``) concerns
points in a flat 2D space.  These points are located with respect to
the origin.  Unlike the terrestrial domain, there are no
discontinuities or distinguished points apart from the origin.

Units
^^^^^

Position in 2D Cartesian space is denoted (x, y).  You, the user, can
decide what those axes mean.  Without a tie to some underlying
physical domain they are purely abstract.  Distances in this space are
measured in dimensionless units.  Speed is measured in units per
second.



3D Cartesian Domain
-------------------

Specification
^^^^^^^^^^^^^

The 3D Cartesian domain (``tracktable::domain::cartesian3d``) concerns
points in a flat 3D space.  These points are located with respect to
the origin.  Unlike the terrestrial domain, there are no
discontinuities or distinguished points apart from the origin.

Units
^^^^^

Position in 3D Cartesian space is denoted (x, y, z).  You, the user, can
decide what those axes mean.  Without a tie to some underlying
physical domain they are purely abstract.  Distances in this space are
measured in dimensionless units.  Speed is measured in units per
second.

