==================
Terrestrial Domain
==================

Specification
^^^^^^^^^^^^^

The Terrestrial domain (``tracktable::domain::terrestrial``) concerns
points on the surface of the Earth. These points are located using
longitude and latitude. In Tracktable, longitude and latitude are
always measured in degrees and longitude always comes first. We
prefer to let longitude range from -180 to 180 but the underlying math
doesn't care.

Units
^^^^^

Position in the terrestrial domain is measured in degrees of longitude
and latitude. Longitude is always coordinate 0 and latitude is always
coordinate 1. Points are presumed to lie on the surface of the Earth.
If you want to include altitude, use the user-defined properties.

Distances are measured in kilometers. Speeds are measured in
kilometers per hour.

Module Contents
^^^^^^^^^^^^^^^

.. doxygenclass:: tracktable::domain::terrestrial::TerrestrialPoint
   :members:
   :protected-members:
   :private-members:
   :undoc-members:

.. doxygenclass:: tracktable::domain::terrestrial::TerrestrialTrajectoryPoint
   :members:
   :protected-members:
   :private-members:
   :undoc-members: