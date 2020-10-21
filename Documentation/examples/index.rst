.. _Tracktable_Examples:

========
Examples
========

To help you get started using Tracktable we have included demonstrations of
its various capabilities, Python and C++ alike, and sample data to try it
on.  C++ examples are in the source code distribution in the directory
``tracktable/Examples``.  Python examples are available as scripts you
can execute as well as Jupyter_ notebooks.

Example Data
------------

.. toctree::
   :maxdepth: 2

   /user_guide/example_data.rst

C++ Examples
------------

This section will be filled out in patch releases for 1.3 and 1.4.

Python Scripts
--------------

.. toctree::
   :maxdepth: 2

   /examples/python_scripts/heatmap.rst
   /examples/python_scripts/trajectory_map.rst
   /examples/python_scripts/movies.rst

Jupyter Notebooks
-----------------

.. toctree::
   :maxdepth: 2

   Clustering_with_Distance_Geometry
   Heatmap_Rendering
   Interactive_Trajectory_Rendering
   Point_Reader
   Static_Image_Trajectory_Rendering
   Trajectory_Builder
   Trajectory_Reader

There are two things you need to know. The first is that we include
several Jupyter_ notebooks as examples of how to do various common tasks with Tracktable.
The second is how to get them. There are two ways:

 1.  Download from `<https://tracktable.sandia.gov/downloads.html>`_ (starting with 1.3).
 2.  The function ``tracktable.examples.copy_example_notebooks``:

Example:

.. code-block:: python

     import tracktable.examples
     tracktable.examples.copy_example_notebooks('/my/home/directory/notebooks')


.. _Jupyter: https://jupyter.org

