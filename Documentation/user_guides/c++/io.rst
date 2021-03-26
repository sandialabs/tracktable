.. _user-guide-cpp-input:

=====
Input
=====

.. _point-input-cpp:

-----------
Point Input
-----------

There are three ways to get point data into Tracktable:

1. Instantiate and populate ``base_point_type`` and ``trajectory_point_type`` objects by hand.
2. Load points from a delimited text file.
3. Create points algorithmically.

.. _manually-instantiate-points-cpp:

Manually instantiate Points
---------------------------

For instructions on manually instantiating both ``base_point_type`` and ``trajectory_point_type``
objects refer to the :ref:`Point Classes section <user-guide-cpp-point-classes>` of
the C++ user guide.

.. _loading-points-file-cpp:

Loading Points from Delimited Text
----------------------------------

Tracktable has a flexible point reader for delimited text files. Each
point domain provides two versions of it, one for loading base points
(coordinates only) and one for loading trajectory points.

.. code-block:: c++
   :linenos:

   #include <tracktable/Domain/Terrestrial.h>
   #include <tracktable/Analysis/AssembleTrajectories.h>

   typedef tracktable::domain::terrestrial::trajectory_point_reader_type reader_type;
   typedef tracktable::domain::terrestrial::trajectory_type trajectory_type;
   typedef tracktable::AssembleTrajectories<trajectory_type, reader_type::iterator> assembler_type;

   reader_type point_reader;
   assembler_type trajectory_builder;

   trajectory_builder.set_separation_time(tracktable::minutes(20));
   trajectory_builder.set_separation_distance(100);
   trajectory_builder.set_minimum_trajectory_length(500);

   std::string = "point_data.csv";
   std::ifstream infile(filename.c_str());

   if (!infile)
   {
      std::cerr << "ERROR: Could not open file '" << filename << "'\n";
      return -1;
   }

   point_reader.set_input(infile);
   point_reader.set_object_id_column(0);
   point_reader.set_timestamp_column(1);
   point_reader.set_longitude_column(2);
   point_reader.set_latitude_column(3);

   for (reader_type it = point_reader.begin(); it != point_reader.end(); ++it) {
      // Do whatever you want with the points here
   }

.. _cpp-point-sources:

Algorithmically Creating Points
-------------------------------

.. important:: To create points algorithmically we will need to supply
   (at a minimum) coordinates, a timestamp and an ID.

The :cpp:class:`TrajectoryPoint` class can generate points interpolated between
each trajectory point of a given trajectory. ``TrajectoryPoint`` s are inherited in each type of domain
under under the ``trajectory_point_type``. These points can then be assembled
into trajectories which is show below but is explained in further detail in the
:ref:`Trajectory Assembly <cpp-trajectory-assembly>` section.

.. code-block:: c++
   :linenos:

   #include <tracktable/Domain/Terrestrial.h>

   using tracktable::domain::terrestrial::trajectory_point_type;
   using tracktable::domain::terrestrial::trajectory_type;

   trajectory_point_type albuquerque;
   trajectory_point_type santa_fe;
   trajectory_point_type roswell;
   trajectory_type trajectory;

   std::string obj_id("GreenChileExpress001");
   albuquerque.set_latitude(35.1107);
   albuquerque.set_longitude(-106.6100);
   albuquerque.set_object_id(obj_id);
   albuquerque.set_timestamp(tracktable::time_from_string("2014-05-01 12:00:00"));

   santa_fe.set_latitude(35.6672);
   santa_fe.set_longitude(-105.9644);
   santa_fe.set_object_id(obj_id);
   santa_fe.set_timestamp(tracktable::time_from_string("2014-05-01 13:00:00"));

   roswell.set_latitude(33.3872);
   roswell.set_longitude(-104.5281);
   roswell.set_object_id(obj_id);
   roswell.set_timestamp(tracktable::time_from_string("2014-05-01 14:00:00"));

   trajectory.push_back(albuquerque);
   trajectory.push_back(santa_fe);
   trajectory.push_back(roswell);

.. _trajectory-input-cpp:

----------------
Trajectory Input
----------------

There are two ways to get trajectory data into Tracktable:

1. Instantiate and populate ``trajectory_type`` objects by hand.
2. Load trajectories from a delimited text file.

.. _manually-instantiate-trajectories-cpp:

Manually instantiate Trajectories
---------------------------------

For instructions on manually instantiating :py:class:`Trajectory`
objects refer to the :ref:`Trajectories section <user-guide-cpp-trajectories>`
of the C++ user guide.

.. _loading-trajectories-file-cpp:

Loading Trajectories from Delimited File
----------------------------------------

Tracktable has a flexible trajectory reader for delimited text files. Each
point domain provides a trajectory reader. The trajectory reader functionality
is the same across all point domains. Trajectories can be loaded from standard
CSV and TSV delimited files as well as tracktable's own TRAJ file type.
Refer to the :ref:`Tracktable Data <tracktable-data>` page for more
information about the TRAJ format.

.. code-block:: c++
   :linenos:

   #include <tracktable/RW/TrajectoryReader.h>
   #include <tracktable/Core/Trajectory.h>
   #include <tracktable/Core/TrajectoryPoint.h>

   typedef tracktable::TrajectoryPoint<point_type> trajectory_point_type;
   typedef tracktable::Trajectory<trajectory_point_type> trajectory_type;

   std::string filename = "trajectories.csv";
   std::ifstream infile(filename.c_str());

   tracktable::TrajectoryReader<trajectory_type> reader(infile);

   for (trajectory_type iter = reader.begin(); iter != reader.end(); ++iter)
   {
      // Do whatever you want with the trajectories here
   }


----------------------------

.. _user-guide-cpp-output:

======
Output
======

.. _point-output-cpp:

------------
Point Output
------------

Both ``base_point_type`` and ``trajectory_point_type`` are output by the
:cpp:class:`PointWriter`. Each point domain has it's own version of the writer.
Output can be directed to a delimited file or a standard output buffer.
Below is an example of exporting points of type ``trajectory_point_type``
to a file, exporting points of the type ``base_point_type`` or using a
buffer would have a similar structure.

.. code-block:: c++
   :linenos:

   #include <tracktable/Core/TrajectoryPoint.h>
   #include <tracktable/RW/PointWriter.h>

   std::string filename = "points.csv";
   std::ofstream ofile(filename.c_str());

   // Generate/Read points here

   tracktable::PointWriter writer(ofile);
   writer.write(points.begin(), points.end());

.. _trajectory-output-cpp:

-----------------
Trajectory Output
-----------------

Similar to the point output, in order to output a ``Trajectory`` from Tracktable the
:cpp:class:`TrajectoryWriter` is be used. The functionality of the writer is the same as the
``base_point_type`` and ``trajectory_point_type`` writers.

.. code-block:: c++
   :linenos:

   #include <tracktable/RW/TrajectoryWriter.h>
   #include <tracktable/Core/Trajectory.h>
   #include <tracktable/Core/TrajectoryPoint.h>

   std::string filename = "trajectories.csv"; // "trajectories.traj"
   std::ofstream ofile(filename.c_str());

   // Generate/Read trajectories here

   tracktable::TrajectoryWriter writer(ofile);
   writer.write(trajectory);