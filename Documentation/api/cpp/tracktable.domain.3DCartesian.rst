===================
3D Cartesian Domain
===================


Specification
^^^^^^^^^^^^^

The 3D Cartesian domain (``tracktable::domain::cartesian3d``) concerns
points in a flat 3D space. These points are located with respect to
the origin. Unlike the terrestrial domain, there are no
discontinuities or distinguished points apart from the origin.

Units
^^^^^

Position in 3D Cartesian space is denoted (x, y, z). You, the user, can
decide what those axes mean. Without a tie to some underlying
physical domain they are purely abstract. Distances in this space are
measured in dimensionless units. Speed is measured in units per
second.

Module Contents
^^^^^^^^^^^^^^^

.. doxygenclass:: tracktable::domain::cartesian3d::CartesianPoint3D
   :members:
   :protected-members:
   :private-members:
   :undoc-members:

.. doxygenclass:: tracktable::domain::cartesian3d::CartesianTrajectoryPoint3D
   :members:
   :protected-members:
   :private-members:
   :undoc-members:
