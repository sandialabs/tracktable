.. _Python_Tracktable_Movie_Example:

=============================
Making Movies of Trajectories
=============================

.. todo:: Explore having a trajectory movie hosted on this page.

.. important:: `Cartopy <https://scitools.org.uk/cartopy/docs/latest/>`_ 0.18.0
   is required to successfully render maps and pass our internal tests.

.. note:: The images generated from the below commands will have a
   large border around the rendered map; this is expected and correct.

To render a movie, we render short subsets of trajectories over and
over. As such we can re-use all of the arguments and algorithms we
already have for rendering trajectory maps with just a few additions
for movie duration, frames per second, and trajectory length. In the examples below,
``TRACKTABLE_HOME`` refers to the directory where you unpacked/installed Tracktable.


Terrestrial Movie
^^^^^^^^^^^^^^^^^

We'll begin with a short movie (10 seconds long, 10 frames per second)
where each moving object has a trail showing the last hour of its
motion.

.. code-block:: console

   $ python -m "tracktable.examples.movie_from_points" \
        --trail-duration 3600 \
        --trajectory-linewidth 2 \
        --fps 10 \
        --duration 10 \
        TRACKTABLE_HOME/examples/data/SampleTrajectories.csv \
        MovieExample1.mp4

This will encode a movie using vanilla MPEG4 that should be playable by
anything less than ten years old. `Quicktime Player
<http://www.apple.com/quicktime/download/>`_, `iTunes <http://www.apple.com/itunes>`_,
and `Windows Media Player <http://windows.microsoft.com/en-us/windows/download-windows-media-player>`_
can all handle this. If you don't already have `VLC <http://www.videolan.org>`_ installed we recommend that as well.

We have two more features to demonstrate here. First, instead of having the trajectory
lines be of constant width along their length we can have them taper as they get older.
We do this with ``--trajectory-width taper``, ``--trajectory-initial-linewidth`` and ``--trajectory-final-linewidth``.
Second, we will also put a dot at the head of each trajectory with ``--decorate-trajectory-head`` and ``--trajectory-head-dot-size``.

.. code-block:: console

   $ python -m "tracktable.examples.movie_from_points" \
      --trail-duration 3600 \
      --trajectory-linewidth taper \
      --trajectory-initial-linewidth 3 \
      --trajectory-final-linewidth 0 \
      --decorate-trajectory-head \
      --trajectory-head-dot-size 3 \
      --fps 10 \
      --duration 10 \
      TRACKTABLE_HOME/examples/data/SampleTrajectories.csv \
      MovieExample2.mp4


Cartesian Movie
^^^^^^^^^^^^^^^

As with geographic data, we can also make movies from data in flat Cartesian space.

.. code-block:: console

    $ python -m "tracktable.examples.movie_from_points" \
      --domain cartesian2d \
      --map-bbox -100 -100 100 100 \
      --trajectory-linewidth taper \
      --trajectory-initial-linewidth 4 \
      --trajectory-final-linewidth 1 \
      TRACKTABLE_HOME/examples/data/SamplePointsCartesian.csv \
      MovieExample3.mp4

.. note:: Recall that trails are colored by their progress
   from start to finish and the default colormap ("heat") is black at the
   beginning. If you would like to see them bright and vivid right from
   the start, add an argument like ``--trajectory-colormap prism`` (or
   any other Matplotib colormap you like).


Using Parallel Processing
^^^^^^^^^^^^^^^^^^^^^^^^^

Where available, we can make use of multiple processes simultaneously for
the rendering of movies. In this example, the result will be the same as
Cartesian example above.

.. code-block:: console

    $ python -m "tracktable.examples.parallel_movie_from_points" \
      --processors 8 \
      --domain cartesian2d \
      --object-id-column 0 \
      --timestamp-column 1 \
      --x-column 2 \
      --y-column 3 \
      --delimiter , \
      --map-bbox -100 -100 100 100 \
      --trajectory-linewidth taper \
      --trajectory-initial-linewidth 4 \
      --trajectory-final-linewidth 1 \
      TRACKTABLE_HOME/examples/data/SamplePointsCartesian.csv \
      MovieExample4.mp4

.. note:: The efficiency of this method is greatly dependent on the
   underlying operating system and the complexity of the movie being
   rendered. For example, on Windows, this method is likely to be
   slower than using the single threaded version.
