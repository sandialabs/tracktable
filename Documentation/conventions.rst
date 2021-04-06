.. _Tracktable_Conventions:

Conventions & Principles
==========================

1. **C++**: Point classes in tracktable/Core (e.g. ``PointBase``, ``PointLonLat`` and
   ``PointCartesian``) should not be instantiated directly.

   Instead of using these, we encourage users to use the classes in
   tracktable/Domain. Each domain shall provide classes named
   ``base_point_type``, ``trajectory_point_type``, ``trajectory_type``,
   ``linestring_type``, ``box_type``, ``base_point_reader_type``,
   ``trajectory_reader_type`` and ``trajectory_point_reader_type``.

   To create a variable that is a trajectory in the Terrestrial
   domain in C++, use code like the following:

   .. code-block:: c++
      :linenos:

      #include <tracktable/Domain/Terrestrial.h>

      tracktable::domain::terrestrial::trajectory_type my_trajectory;


2. Each domain shall be consistent in its use of units.

   The Terrestrial domain shall compute distances in kilometers and
   speeds in kilometers per hour. Positions shall be measured in
   degrees of latitude and longitude. Speaking of which...

   
3. Positions on the Earth shall be measured in **degrees of longitude and latitude**.

   This one is simpler. The only real question is whether latitude or
   longitude should come first. Both approaches have their
   proponents. *We will always specify longitude first in tuples*.
   The canonical globe will have longitudes from -180 to 180 and
   latitudes from -90 to 90.

   
4. Bearings shall be measured in degrees. A bearing of 0 is due north
   and 90 degrees is due east.

   This has been navigational convention for a very, very long time.

   
5. All default **color maps shall be accessible** to people with red-green color blindness.

   At a minimum , a color map should be usable when converted to black
   and white. In addition, its color channels should obey the
   following rules of thumb: one can use either red or green but not
   both in the same color map.

   We will never use or encourage the use of the Dreaded Rainbow Color Map.
   If you are unfamiliar with this controversy we strongly encourage you to
   read `How the Rainbow Color Map Deceives <http://eagereyes.org/basics/rainbow-color-map>`_
   and `Rainbow Color Map (Still) Considered Harmful <http://people.renci.org/~borland/pdfs/RainbowColorMap_VisViewpoints.pdf>`_.

   
6. External software dependencies should be minimized.

   We have all had the experience of trying to install a software
   package only to discover that we are missing some crucial
   dependency. That dependency has two other dependencies. Finally, deep down,
   the entire house of code requires a never-released bootleg version
   of some library that noone has used since the days of the PDP/11.

   Obviously we want to prevent this.

   However, there is an even more compelling reason to minimize
   dependencies. There are computing environments where software
   installation is governed by administrative and legal constraints
   rather than technical ones. In such an environment it can take
   months just to install a more recent version of an already-approved
   package, let alone an entirely new one. By minimizing our external
   dependencies and sticking to stable versions we make it easier to
   use Tracktable in any environment of interest.

   We ruefully acknowledge the fact that Boost is not a minimal
   dependency.

.. todo:: Define coding conventions for Python and C++

"Those are my principles, and if you don't like them... well, I have others."

Groucho Marx
