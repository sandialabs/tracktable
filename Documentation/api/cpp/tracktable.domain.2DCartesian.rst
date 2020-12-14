===================
2D Cartesian Domain
===================


Specification
^^^^^^^^^^^^^

The 2D Cartesian domain (``tracktable::domain::cartesian2d``) concerns
points in a flat 2D space. These points are located with respect to
the origin. Unlike the terrestrial domain, there are no
discontinuities or distinguished points apart from the origin.

Units
^^^^^

Position in 2D Cartesian space is denoted (x, y). You, the user, can
decide what those axes mean. Without a tie to some underlying
physical domain they are purely abstract. Distances in this space are
measured in dimensionless units. Speed is measured in units per
second.

Module Contents
^^^^^^^^^^^^^^^

.. doxygenclass:: tracktable::domain::cartesian2d::CartesianPoint2D
   :members:
   :protected-members:
   :private-members:
   :undoc-members:

.. doxygenclass:: tracktable::domain::cartesian2d::CartesianTrajectoryPoint2D
   :members:
   :protected-members:
   :private-members:
   :undoc-members: