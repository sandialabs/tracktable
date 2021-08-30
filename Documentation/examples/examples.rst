.. _Tracktable_Examples:

========
Examples
========

To help you get started using Tracktable we have included demonstrations of
its various capabilities, Python and C++ alike, and sample data to experiment with.
C++ examples are in the source code distribution in the directory
``tracktable/Examples``. Python examples, tutorials and demos are available,
from the Pip package, Anaconda package and source code distribution in the
directory ``tracktable/Python/tracktable/examples``, as standalone Python scripts
and Jupyter_ notebooks.

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

.. note:: We include several Jupyter_ notebooks that demonstrate and illustrate Tracktable's capabilities.
         Each Jupyter notebook page listed below is an actual Jupyter notebook, including output, embedded directly in the documention.

Tutorials
*********

.. graphviz::
   :align: center
   :caption: Tutorial Flow

   digraph tut_flow {
      tut1 [label="Tutorial 1: How to read in points from csv/tsv"];
      tut2 [label="Tutorial 2: How to read in trajectories from csv/tsv"];
      tut3 [label="Tutorial 3: Writing Traj Files"];
      tut4 [label="Tutorial 4: Reading Traj Files"];
      viz [label="Visualization"]
      tut5A [label="Tutorial 5A: Interactive Trajectory Visualization"];
      tut5B [label="Tutorial 5B: Static Trajectory Visualization"];
      tut5C [label="Tutorial 5C: Heatmap Trajectory Visualization"];
      tut5D [label="Tutorial 5D: Trajectory Visualization For Print"];
      tut6 [label="Tutorial 6: Filtering"];

      tut1 -> tut2;
      tut2 -> tut3;
      tut2 -> tut4;
      tut2 -> viz;
      viz -> tut5A;
      viz -> tut5B;
      viz -> tut5C;
      viz -> tut5D;
      tut2 -> tut6;
   }

.. toctree::
   :maxdepth: 1

   Tutorial_01
   Tutorial_02
   Tutorial_03
   Tutorial_04
   Tutorial_05A
   Tutorial_05B
   Tutorial_05C
   Tutorial_05D
   Tutorial_06

Analytic Demos
**************

.. toctree::
   :maxdepth: 1

   Demo_01
   Demo_02
   Demo_03
   Demo_04
   Demo_05


If you wish to modify or run the notebooks locally there are three ways to get them:

 #. Clone Tracktable's Github repository: `<https://github.com/sandialabs/tracktable>`_.
 #. Download Tracktable's source code from `<https://tracktable.sandia.gov/downloads/source_code.html>`_ (starting with Tracktable 1.3).
 #. If you have Tracktable installed, the function ``tracktable.examples.copy_example_notebooks`` will move the notebooks to a place of your choosing.

      - Detailed information about ``copy_example_notebooks`` can be found here: :ref:`python_examples_module_label`

.. _Jupyter: https://jupyter.org
