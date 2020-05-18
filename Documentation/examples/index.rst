.. _Tracktable_Examples:


.. toctree::

   /examples/python_scripts/heatmap
   /examples/python_scripts/trajectory_map
   /examples/python_scripts/movies

========
Examples
========

To help you get started using Tracktable we have included demonstrations of 
its various capabilities, Python and C++ alike, and sample data to try it
on.  C++ examples are in the source code distribution in the directory
``tracktable/Examples``.  Python examples are available as scripts you
can execute as well as Jupyter_ notebooks.



C++ Examples
------------

This section will be filled out in patch releases for 1.3 and 1.4.  

Python Scripts
--------------

 - :doc:`/examples/python_scripts/heatmap`
 - :doc:`/examples/python_scripts/trajectory_map`
 - :doc:`/examples/python_scripts/movies`

Jupyter Notebooks
-----------------

This section will be filled out in patch releases for 1.3 and 1.4.

Between now and then, there are two things you need to know.  The first is that we include several Jupyter_ notebooks as examples of how to do various common tasks with Tracktable.  The second is how to get them.  There are two ways:

 1.  Download from `<https://tracktable.sandia.gov/downloads.html>` (starting with 1.3).
 2.  The function `tracktable.examples.copy_example_notebooks`:
 
 ::

     import tracktable.examples
     tracktable.examples.copy_example_notebooks('/my/home/directory/notebooks')


.. _Jupyter: https://jupyter.org

