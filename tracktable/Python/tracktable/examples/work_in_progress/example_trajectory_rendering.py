#
# Copyright (c) 2014-2020 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""example_trajectory_rendering - Arguments and code for drawing trajectories

This file contains a complete, runnable example of how to render
trajectories onto a map (example_trajectory_rendering()) as well as
utility functions that you can use in your own code.  Those functions
address questions such as...

* How should the line segments in the trajectory be colored?
* What should the line width for each segment be?
* Should there be a dot at the head of the trajectory?  What size and
  color?
* What layer (Z-order) should the trajectories live in?

"""

import matplotlib.colors

from tracktable.feature import annotations
from tracktable.render import paths

import numpy
import sys
from tracktable.examples.example_trajectory_builder import example_trajectory_builder
from tracktable.domain import terrestrial
from tracktable.render import mapmaker
from matplotlib import pyplot

# ----------------------------------------------------------------------

def example_trajectory_rendering():
    '''Sample code to render trajectories from points

        In some cases, you may wish to read in trajectories with certain constraints. For example, we can have trajectories with a minimum number of points. Or we acknowledge that the points in the
        trajectory should be within a certain time and/or distance threshold to belong to the same trajectory. The Trajectory Builder does this.'''

    # First, We will need data points built into trajectories. Replace the following with your own code to build the trajectories or use the provided example.
    fileName = './tracktable/examples/data/SampleTrajectories.csv'
    trajectories = example_trajectory_builder(fileName)

    # Set up the canvas and map projection
    dpi = 160
    figure = pyplot.figure(figsize=[20, 15])
    axes = figure.add_subplot(1, 1, 1)
    #(figure, axes) = initialize_matplotlib_figure([10, 7.5])
    (mymap, map_actors) = mapmaker.mapmaker(domain='terrestrial',
                                            map_name='region:conus',
                                            draw_coastlines=True,
                                            draw_countries=True,
                                            draw_states=True,
                                            draw_lonlat=True,
                                            fill_land=True,
                                            fill_water=True,
                                            land_fill_color='#101010',
                                            water_fill_color='#222222',
                                            land_zorder=0,
                                            water_zorder=0,
                                            lonlat_spacing=90,
                                            lonlat_color='#A0A0A0',
                                            lonlat_linewidth=0.2,
                                            lonlat_zorder=2,
                                            coastline_color='#808080',
                                            coastline_linewidth=1,
                                            coastline_zorder=5,
                                            country_color='#606060',
                                            country_fill_color='#FFFF80',
                                            country_linewidth=0.5,
                                            country_zorder=5,
                                            state_color='#404040',
                                            state_fill_color='none',
                                            state_linewidth=0.3,
                                            state_zorder=2,
                                            draw_largest_cities=50,
                                            draw_cities_larger_than=None,
                                            city_label_size=12,
                                            city_dot_size=2,
                                            city_dot_color='white',
                                            city_label_color='white',
                                            city_zorder=6,
                                            border_resolution='110m',
                                            axes=axes,
                                            map_projection='PlateCarree')

    color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1)
    render_trajectories(mymap, trajectories, trajectory_linewidth=2)

    print("STATUS: Saving figure to file")
    pyplot.savefig('./Example_Trajectory_Rendering_CONUS.png',
                   dpi=dpi,
                   facecolor='black')

    pyplot.close()


# ----------------------------------------------------------------------

def initialize_matplotlib_figure(figure_size_in_inches,
                                 axis_span=[0, 0, 1, 1],
                                 facecolor='black',
                                 edgecolor='black'):
    """Initialize a figure for Matplotlib to draw into.

    Args:
       figure_size_in_inches: 2-tuple of floats (width, height)
       axis_span: list of 4 floats (left, bottom, width, height) with size of axes in figure.
           Quantities are in fractions of figure width and height.
       facecolor: string (default 'black') - what's the background color of the plot?
       edgecolor: string (default 'black') - color of edge aroudn the figure

    Returns:
       (figure, axes) - both Matplotlib data structures
    """

    figure = pyplot.figure(figsize=figure_size_in_inches,
                           facecolor='black',
                           edgecolor='black')
    axes = figure.add_axes([0, 0, 1, 1], frameon=False, facecolor='black')
    axes.set_frame_on(False)

    return (figure, axes)

# ----------------------------------------------------------------------

def make_constant_colormap(color):
    colormap = matplotlib.colors.ListedColormap([color], 'dummy colormap')
    return colormap

# ----------------------------------------------------------------------

def render_trajectories(basemap,
                        trajectory_source,
                        trajectory_color_type="scalar",
                        trajectory_color="progress",
                        trajectory_colormap="gist_heat",
                        trajectory_zorder=10,
                        decorate_trajectory_head=False,
                        trajectory_head_dot_size=2,
                        trajectory_head_color="white",
                        trajectory_linewidth=0.5,
                        trajectory_initial_linewidth=0.5,
                        trajectory_final_linewidth=0.01,
                        scalar_min=0,
                        scalar_max=1,
                        axes=None):
    """Render decorated trajectories onto a map instance.

    Given a map instance (usually axes from Cartopy) and an iterable
    containing trajectories, draw the trajectories onto the map with
    the specified appearance parameters.  You can control the trajectory
    color, linewidth, z-order and whether or not a dot is drawn at the
    head of each path.

    Args:
       basemap:                  Basemap instance to draw into
       trajectory_source:        Iterable of Trajectory objects
       trajectory_color_type:    String, either 'scalar' or 'constant'
       trajectory_color:         Name of an annotation function if trajectory_color_type
                                 is 'scalar'; name/hex string of a color if it's 'constant'
       trajectory_colormap:      Colormap to map between scalars and colors if
                                 trajectory_color_type is 'scalar'
       trajectory_zorder:        Image layer for trajectory geometry -- higher layers
                                 occlude lower ones
       decorate_trajectory_head: Whether or not to draw a dot at the head of each trajectory
       trajectory_head_dot_size: Size (in points) for the dot at the head of each trajectory
       trajectory_head_color:    Name/hex string for color of trajectory dots
       trajectory_linewidth:     Trajectory linewidth in points
       trajectory_initial_linewidth: If trajectory_linewidth is 'taper', lines will be this
                                 wide at the head of the trajectory
       trajectory_final_linewidth: If trajectory_linewidth is 'taper', lines will be this
                                 wide at the tail of the trajectory
       axes:                     Artists will be added to this Axes instance instead of the default

    Raises:
       KeyError: trajectory_color_type is 'scalar' and the specified
                 trajectory scalar generator was not found in
                 tracktable.features.available_annotations()

    Returns:
       A list of the artists added to the basemap


    NOTE: This function is an adapter between the trajectory_rendering
    argument group and the draw_traffic() function in the
    tracktable.render.paths module.
    """

    trajectories_to_render = None

    if trajectory_color_type == 'scalar':
        annotator = annotations.retrieve_feature_function(trajectory_color)

        def annotation_generator(traj_source):
            for trajectory in traj_source:
                yield(annotator(trajectory))

        trajectories_to_render = annotation_generator(trajectory_source)
        scalar_generator = annotations.retrieve_feature_accessor(trajectory_color)
        colormap = trajectory_colormap

    else:
        def dummy_scalar_retrieval(trajectory):
            scalar = numpy.zeros(len(trajectory))
            return scalar

        def dummy_generator(things):
            for thing in things:
                yield(thing)

        trajectories_to_render = dummy_generator(trajectory_source)
        scalar_generator = dummy_scalar_retrieval
        colormap = make_constant_colormap(trajectory_color)

    return render_annotated_trajectories(basemap,
                                         trajectories_to_render,
                                         trajectory_scalar_accessor=scalar_generator,
                                         trajectory_colormap=colormap,
                                         trajectory_zorder=trajectory_zorder,
                                         decorate_trajectory_head=decorate_trajectory_head,
                                         trajectory_head_dot_size=trajectory_head_dot_size,
                                         trajectory_head_color=trajectory_head_color,
                                         trajectory_linewidth=trajectory_linewidth,
                                         trajectory_initial_linewidth=trajectory_initial_linewidth,
                                         trajectory_final_linewidth=trajectory_final_linewidth,
                                         scalar_min=scalar_min,
                                         scalar_max=scalar_max,
                                         axes=axes)

# ----------------------------------------------------------------------

def _dummy_accessor(trajectory):
    return numpy.zeros(len(trajectory))

def render_annotated_trajectories(basemap,
                                  trajectory_source,
                                  trajectory_scalar_accessor=_dummy_accessor,
                                  trajectory_colormap="gist_heat",
                                  trajectory_zorder=10,
                                  decorate_trajectory_head=False,
                                  trajectory_head_dot_size=2,
                                  trajectory_head_color="white",
                                  trajectory_linewidth=0.5,
                                  trajectory_initial_linewidth=0.5,
                                  trajectory_final_linewidth=0.01,
                                  scalar_min=0,
                                  scalar_max=1,
                                  axes=None):

    """Render decorated trajectories (with scalars) onto a map instance.

    Given a map instance and an iterable containing trajectories,
    draw the trajectories onto the map with the specified appearance
    parameters.  You can control the trajectory color, linewidth,
    z-order and whether or not a dot is drawn at the head of each
    path.

    Args:
       basemap:                  Map instance to draw into
       trajectory_source:        Iterable of Trajectory objects
       trajectory_scalar_accessor: Return a list of scalars for a trajectory
       trajectory_colormap:      Colormap to map between scalars and colors
       trajectory_zorder:        Image layer for trajectory geometry -- higher layers
                                 occlude lower ones
       decorate_trajectory_head: Whether or not to draw a dot at the head of each trajectory
       trajectory_head_dot_size: Size (in points) for the dot at the head of each trajectory
       trajectory_head_color:    Name/hex string for color of trajectory dots
       trajectory_linewidth:     Trajectory linewidth in points
       trajectory_initial_linewidth: If trajectory_linewidth is 'taper', lines will be this
                                 wide at the head of the trajectory
       trajectory_final_linewidth: If trajectory_linewidth is 'taper', lines will be this
                                 wide at the tail of the trajectory
       axes:                     Artists will be added to this Axes instance instead of the default
       scalar_min (float):       Scalar value to map to bottom of color map
       scalar_max (float):       Scalar value to map to top of color map

    Returns:
       A list of the artists added to the basemap


    NOTE: This function is an adapter between the trajectory_rendering
    argument group and the draw_traffic() function in the
    tracktable.render.paths module.

    """

    if trajectory_linewidth == 'taper':
        linewidth_generator = _make_tapered_linewidth_generator(trajectory_initial_linewidth,
                                                                trajectory_final_linewidth)
    else:
        linewidth_generator = _make_constant_linewidth_generator(trajectory_linewidth)

    if decorate_trajectory_head:
        dot_size = trajectory_head_dot_size
        dot_color = trajectory_head_color
    else:
        dot_size = 0
        dot_color = 'white'

    return paths.draw_traffic(basemap,
                              trajectory_source,
                              color_map=trajectory_colormap,
                              trajectory_scalar_generator=trajectory_scalar_accessor,
                              trajectory_linewidth_generator=linewidth_generator,
                              zorder=trajectory_zorder,
                              color_scale=matplotlib.colors.Normalize(vmin=scalar_min, vmax=scalar_max),
                              dot_size=dot_size,
                              dot_color=dot_color,
                              axes=axes)


# ----------------------------------------------------------------------


def _make_tapered_linewidth_generator(initial_linewidth,
                                      final_linewidth):

    """Create a function that will make a tapered line width for a trajectory

    In order to render tapered trajectories whose lines get thinner as
    they get older, we need to generate a scalar array with as many
    components as the trajectory has segments.  The first entry in
    this array (corresponding to the OLDEST point) should have the
    value 'final_linewidth'.  The last entry (corresponding to the
    NEWEST point) should have the value 'initial_linewidth'.

    Args:
       initial_linewidth:  Width (in points) at the head of the trajectory
       final_linewidth:    Width (in points) at the tail of the trajectory

    Returns:
       A function that takes in a trajectory as an argument and
       returns an array of linewidths

    NOTE: There might be an off-by-one error in here: we generate
    len(trajectory) scalars but the geometry has len(trajectory)-1
    segments.  Check to see if draw_traffic in paths.py corrects for
    this.
    """

    def linewidth_generator(trajectory):
        return numpy.linspace(final_linewidth, initial_linewidth, len(trajectory))

    return linewidth_generator

# ----------------------------------------------------------------------

def _make_constant_linewidth_generator(linewidth):

    """Create a function that will make a constant line width for a trajectory

    Args:
       linewidth:  Width (in points) along the trajectory

    Returns:
       A function that takes in a trajectory as an argument and
       returns an array of linewidths

    NOTE: There might be an off-by-one error in here: we generate
    len(trajectory) scalars but the geometry has len(trajectory)-1
    segments.  Check to see if draw_traffic in paths.py corrects for
    this.
    """

    def linewidth_generator(trajectory):
        scalars = numpy.zeros(len(trajectory))
        scalars += float(linewidth)
        return scalars

    return linewidth_generator

if __name__ == '__main__':
    sys.exit(example_trajectory_rendering())
