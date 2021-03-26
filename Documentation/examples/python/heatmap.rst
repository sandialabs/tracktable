.. _Python_Heatmap_Example:

================================
Rendering a Heat Map from Points
================================

.. important:: `Cartopy <https://scitools.org.uk/cartopy/docs/latest/>`_ 0.18.0
   is required to successfully render maps and pass our internal tests.

.. note:: The images generated from the commands below will have a
   large border around the rendered map; this is expected and correct.

The simplest display type that Tracktable supports is the
2-dimensional histogram or `heatmap
<http://en.wikipedia.org/wiki/Heat_map>`_. It requires points that
contain longitude/latitude coordinates. The points can contain any
number of other attributes but they will be ignored. In the examples below,
``TRACKTABLE_HOME`` refers to the directory where you unpacked/installed Tracktable.

Run the example as follows:

.. code-block:: console

   $ python -m "tracktable.examples.heatmap_from_points" \
      TRACKTABLE_HOME/examples/data/SampleHeatmapPoints.csv \
      HeatmapExample1.png

Open the resulting image (``HeatmapExample1.png``) in your favorite
image viewer. You will see a map of the Earth with a smattering of
red and yellow dots. These are our example points, all generated in the
neighborhood of population centers.

.. image:: /images/HeatmapExample1.png
   :scale: 50%

Now it's time to change things around. Let's suppose that you want to
see larger-area patterns with a coarser distribution. You can change
the histogram resolution with the ``--histogram-bin-size`` argument.

.. code-block:: console

   $ python -m "tracktable.examples.heatmap_from_points" \
      --histogram-bin-size 5 \
      TRACKTABLE_HOME/examples/data/SampleHeatmapPoints.csv \
      HeatmapExample2.png

.. image:: /images/HeatmapExample2.png
   :scale: 50%

Perhaps when you open up that image you find that the bins are now too
large. The earlier size was good but the histogram is too sparse. If
you change the color map to use a logarithmic scale instead of a
linear one you might get more detail.

.. code-block:: console

   $ python -m "tracktable.examples.heatmap_from_points" \
      --scale logarithmic \
      TRACKTABLE_HOME/examples/data/SampleHeatmapPoints.csv \
      HeatmapExample3.png

.. image:: /images/HeatmapExample3.png
   :scale: 50%

That doesn't help much. What if we zoom in on Europe and make the
bins smaller?

.. code-block:: console

   $ python -m "tracktable.examples.heatmap_from_points" \
      --scale logarithmic \
      --map region:europe \
      --histogram-bin-size 0.5 \
      TRACKTABLE_HOME/examples/data/SampleHeatmapPoints.csv \
      HeatmapExample4.png

.. image:: /images/HeatmapExample4.png
   :scale: 50%

There are many more options that you can change including map region,
point domain (geographic or Cartesian), decoration, colors, image
resolution and input configuration. You can get a full list of
options with the ``--help`` argument.

.. code-block:: console

   $ python -m "tracktable.examples.heatmap_from_points" --help
