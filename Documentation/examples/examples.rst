.. _Tracktable_Examples:

========
Examples
========

To help you get started using Tracktable we have included demonstrations of
its various capabilities, Python and C++ alike, and sample data to experiment with.
C++ examples are in the source code distribution in the directory
``tracktable/Examples``. Python examples are available, from the Pip package
and source code distribution in the directory ``tracktable/Python/tracktable/examples``,
as standalone Python scripts as well as Jupyter_ notebooks.

C++ Examples
------------

.. toctree::
   :maxdepth: 2

   /examples/c++/Assemble.rst
   /examples/c++/Classify.rst
   /examples/c++/Cluster.rst
   /examples/c++/Filter.rst
   /examples/c++/Find_ID.rst
   /examples/c++/Portal.rst
   /examples/c++/Predict.rst
   /examples/c++/Reduce.rst
   /examples/c++/Sample_Project.rst
   /examples/c++/Serialize.rst

Python Examples
---------------

.. toctree::
   :maxdepth: 2

   /examples/python/data_generation.rst
   /examples/python/heatmap.rst
   /examples/python/trajectory_map.rst
   /examples/python/movies.rst

Jupyter Notebook Examples
-------------------------

.. toctree::
   :maxdepth: 2

   Clustering_with_Distance_Geometry
   Heatmap_Rendering
   Interactive_Trajectory_Rendering
   Point_Reader
   Static_Image_Trajectory_Rendering
   Trajectory_Builder
   Trajectory_Reader

We include several Jupyter_ notebooks as examples of how to do various common tasks with Tracktable.
Each Jupyter notebook page listed above is an actual Jupyter notebook, including output, embedded directly in the documention.


There are two ways to get the notebooks if you wish to modify them or run them locally:

 1. Download from `<https://tracktable.sandia.gov/downloads/source_code.html>`_ (starting with 1.3).
 2. The function ``tracktable.examples.copy_example_notebooks``

      - Detailed information about ``copy_example_notebooks`` can be found here: :ref:`python_examples_module_label`

.. _Jupyter: https://jupyter.org
