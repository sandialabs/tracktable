#
# Copyright (c) 2014-2021 National Technology and Engineering
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

"""heatmap_from_points.py - Example of how to render a 2D geographic heatmap using points in a CSV file


This is both an example of how to use the library and a convenient
script that you can use to get started quickly.  You must provide as
input a delimited text file with at least 4 columns: object_id,
timestamp, longitude, latitude.  (All columns beyond those first four
will be ignored.)  The points in this file will be rendered onto a map
of part of the world.

You can control the following aspects of the rendering:

- Which part of the world is displayed in the map.  This defaults to
  the whole world but can be changed with the --map argument.  Your
  options are 'world', 'conus' (continental US), 'north_america' and
  'europe'.

- Which colormap is used to render the colors.  This defaults to the
  'gist_heat' thermal scale built into matplotlib.  You may specify
  the name of another if you prefer.  Note that you can only use the
  predefined colormaps here.  If you need a custom colormap, use this
  script as a starting point for your own code.

- The mapping from point density to color.  This defaults to 'linear'
  but you may also specify 'logarithmic' (or 'log' for short).

- The size of each histogram bin.  To create bins that are 0.5 degree
  on a side you would say '--histogram-bin-size 0.5'.

- The resolution of the output image with '--resolution 800 600' or
  whatever you choose.

- The output format.  This is automatically deduced from the output
  filename.

- The DPI of the output image.  Defaults to 72 (typical screen
  resolution).  Note that this will affect things like line thickness
  for borders: matplotlib sizes those things in points rather than
  pixels.

- Whether to draw continent boundaries, country borders,
  latitude/longitude graticules and (within North America) state
  borders.  By default all four are turned on.  Use
  '--omit-continents', '--omit-countries', '--omit-states' and
  '--omit-lonlat' to turn them off.  These will by default be drawn
  over the top of the histogram.

- The delimiter used to separate columns in the text file.  You can
  specify any single character to the '--delimiter' option or the
  magic strings 'tab' or '\t'.  (If it's easy for you to type in a
  literal tab then go ahead.  Just be sure to quote it.)

- Whether or not to draw cities, either with --draw-largest-cities
  or --draw-cities-above-size.

"""

from __future__ import print_function

# Tell Matplotlib to use the non-interactive backend so that we can
# run this script without a window system.  We do this before anything
# else so that we can be sure that no other package can initialize
# Matplotlib to default to a window system.
import matplotlib
if __name__ == '__main__':
    print("STATUS: Matplotlib will use Agg backend.")
    matplotlib.use('Agg')

import numpy
import pprint
import sys
import itertools

from tracktable.core import geomath
from tracktable.render import colormaps, histogram2d, mapmaker, projection
from tracktable.domain.cartesian2d import BasePoint as Point2D
from tracktable.domain.cartesian2d import BoundingBox as BoundingBox2D
from tracktable.examples import generate_heatmap_sample_data as gen_sample

from matplotlib import pyplot

# ----------------------------------------------------------------------

def example_heatmap_rendering():

    #Sample code to render heatmap of points

    # In this example, data points are filtered and only a set number of cities are represented.
    num_cities = 40
    num_points_per_city = 1000
    cities = gen_sample.n_largest_cities(num_cities)

    all_sources = [ gen_sample.points_near_city(city, num_points_per_city)
                   for city in cities ]
    all_points = list(itertools.chain(*all_sources))

    #The type of map, colors, scaling can be customised depending the on the desired look and feel of the finished map.
    (figure, axes) = initialize_matplotlib_figure([20, 15])
    (mymap, map_actors) = mapmaker.mapmaker(domain='terrestrial',
                                            map_name='region:world')

    render_histogram(mymap,
        domain='terrestrial',
        point_source=all_points,
        bin_size=0.25,
        color_map='gist_heat',
        scale_type='logarithmic')

    print("STATUS: Saving figure to file")
    savefig_kwargs = {
                       }
    pyplot.savefig('Example_Heatmap_Rendering.png',
        dpi=72,
        facecolor='black'
        )

    pyplot.close()

    return 0

# ----------------------------------------------------------------------

def render_histogram(mymap,
                     domain,
                     point_source,
                     bounding_box=None,
                     bin_size=2,
                     color_map='gist_gray',
                     scale_type='linear',
                     zorder=8):
    """Compile all the points in a source into a 2D histogram, then render
    that histogram onto an already-prepared map."""

    if scale_type.lower() == 'linear':
        scale = matplotlib.colors.Normalize()
    elif scale_type.lower() in [ 'log', 'logarithmic' ]:
        scale = matplotlib.colors.LogNorm()
    else:
        raise ValueError("ERROR: Unknown scale type '{}'.  Legal values are 'linear', 'log' and 'logarithmic'.".format(scale_type))


    if domain == 'terrestrial':
        # Deduce bounding box from map.  Whatever the user requested
        # has already been figured out there.
        from tracktable.domain.terrestrial import BasePoint, BoundingBox
        extent = mymap.get_extent()
        min_corner = BasePoint(extent[0], extent[2])
        max_corner = BasePoint(extent[1], extent[3])
        bounding_box = BoundingBox(min_corner, max_corner)

        return histogram2d.render_histogram(map_projection=mymap,
                                            point_source=point_source,
                                            bounding_box=bounding_box,
                                            bin_size=bin_size,
                                            colormap=color_map,
                                            colorscale=scale,
                                            zorder=zorder)
    elif domain == 'cartesian2d':
        # TODO: Bounding box should have been attached to map projection.
        print("DEBUG: Data bounds: {}".format(bounding_box))
        return histogram2d.render_histogram(mymap,
                                            point_source=point_source,
                                            bounding_box=bounding_box,
                                            bin_size=bin_size,
                                            colormap=color_map,
                                            colorscale=scale,
                                            zorder=zorder)
    else:
        raise AttributeError('Domain {} does not yet have histogram support.'.format(domain))


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

if __name__ == '__main__':
    sys.exit(example_heatmap_rendering())
