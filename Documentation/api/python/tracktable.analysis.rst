==========================
tracktable.analysis module
==========================


.. attention:: The ``tracktable.analysis`` submodules have been relocated to more
      appropriate locations which are listed below and ``tracktable.analysis`` will
      become fully deprecated in Tracktable 1.8.

      * ``tracktable.analysis.assemble_trajectories`` -> ``tracktable.applications.assemble_trajectories``
      * ``tracktable.analysis.dbscan`` -> ``tracktable.algorithms.dbscan``
      * ``tracktable.analysis.distance_geometry`` -> ``tracktable.algorithms.distance_geometry``
      * ``tracktable.analysis.rtree`` -> ``tracktable.domain.rtree``

.. important:: ``tracktable.analysis`` submodules are still importable and usable.
   However, they *need* to be of the format ``from tracktable.analysis.<submodule> import <function/class>``. For example,
   to import ``AssembleTrajectoryFromPoints`` you would do
   ``from tracktable.analysis.assemble_trajectories import AssembleTrajectoryFromPoints``


----------
Submodules
----------


.. toctree::
   :maxdepth: 2

   tracktable.applications.assemble_trajectories.rst
   tracktable.algorithms.dbscan.rst
   tracktable.algorithms.distance_geometry.rst
   tracktable.domain.rtree.rst

