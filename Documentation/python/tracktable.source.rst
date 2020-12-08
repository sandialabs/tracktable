========================
tracktable.source module
========================

The ``tracktable.source`` submodules have been relocated to more
appropriate locations listed below and ``tracktable.source`` will
become fully deprecated in Tracktable 1.6.

* ``tracktable.source.combine`` -> ``tracktable.feature.interleave_points``
* ``tracktable.source.path_point_source`` -> ``tracktable.feature.interpolated_points``
* ``tracktable.source.point`` -> ``tracktable.data_generators.point``
* ``tracktable.source.trajectory`` -> ``tracktable.analysis.assemble_trajectories``

.. important:: ``tracktable.source`` submodules are still importable and usable in Tracktable 1.5.
   They *need* to be of the format ``from tracktable.source.<submodule> import <function/class>``. For example,
   to import ``AssembleTrajectoryFromPoints`` you would do ``from tracktable.source.trajectory import AssembleTrajectoryFromPoints``

----------
Submodules
----------


.. toctree::
   :maxdepth: 2

   tracktable.analysis.assemble_trajectories.rst
   tracktable.data_generators.point.rst
   tracktable.feature.interleave_points.rst
   tracktable.feature.interpolated_points.rst