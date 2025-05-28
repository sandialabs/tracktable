#
# Copyright (c) 2014-2023 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
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

"""
tracktable.render.cartopy - render trajectories in using the cartopy backend
"""

import itertools
from datetime import datetime
import logging

import cartopy
import cartopy.crs
import matplotlib
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy
from numpy import ma as masked_array

from tracktable.core.geomath import compute_bounding_box
from tracktable.domain.cartesian2d import BasePoint as Point2D
from tracktable.domain.cartesian2d import BoundingBox as BoundingBox2D
from tracktable.domain.cartesian2d import identity_projection
from tracktable.render import render_map
from tracktable.render.map_decoration import coloring
from tracktable.render.map_processing import common_processing, paths

LOG = logging.getLogger(__name__)

IPYTHON_AVAILABLE = False
try:
    from IPython import get_ipython
    IPYTHON_AVAILABLE = True
except ImportError:
    # This is not necessarily a problem.  It just means that
    # we won't be able to call '%matplotlib inline', which might
    # affect how figures are rendered in notebooks.
    pass


def render_trajectories(trajectories,

                        #common arguments
                        map_canvas = None,
                        obj_ids = [],
                        map_bbox = [],
                        region_size=(200,200),
                        show_lines = True,
                        gradient_hue = None,
                        color_map = '',
                        line_color = '',
                        linewidth = 0.8,
                        show_points = False,
                        point_size = 0.2,
                        point_color = '',
                        show_dot = True,
                        dot_size = 0.23,
                        dot_color = 'white',
                        trajectory_scalar_generator = common_processing.path_length_fraction_generator,
                        trajectory_linewidth_generator = None,
                        color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1),
                        show = True,
                        save = False,
                        filename = '',
                        tiles=None,
                        show_distance_geometry = False,
                        distance_geometry_depth = 4,
                        zoom_frac = [0,1], #undocumented feature, for now
                        draw_airports=False,
                        draw_ports=False,
                        draw_shorelines=False,
                        draw_rivers=False,
                        draw_borders=False,

                        #cartopy specific arguments
                        draw_lonlat=True,
                        fill_land=True,
                        fill_water=True,
                        draw_coastlines=True,
                        draw_countries=True,
                        draw_states=True,
                        draw_cities=False,
                        map_projection = None,
                        transform = cartopy.crs.PlateCarree(),
                        figsize=(4,2.25),
                        dpi=300,
                        bbox_buffer=(.3,.3),
                        **kwargs): #kwargs are for render_map
    """Render a list of trajectories using the cartopy backend

        For documentation on the parameters, please see render_trajectories
    """
    #tiles override cartopy map features
    if tiles != None:
        fill_land=False
        fill_water=False
        draw_coastlines=False
        draw_countries=False
        draw_states=False

    trajectories, line_color, color_map, gradient_hue = \
        common_processing.common_processing(trajectories, obj_ids, line_color, color_map,
                          gradient_hue)
    if not trajectories:
        return

    if not show_dot:
        dot_size = 0

    if common_processing.in_notebook():
        if show:
            # below effectively does %matplotlib inline (display inline)
            pass
            #get_ipython().magic("matplotlib inline")   # TODO may casue issues may want to remove

            # TODO figure out how to get matplotlib not to show
            # after executing code a second time.
            #
            # If you're talking about how to update a figure after
            # it's been rendered, there are two ways.  The first
            # is to use IPython.display.clear_output() as described
            # on https://discourse.matplotlib.org/t/updating-a-figure/23572/3
            # and the second is to install `ipympl` and use
            # "%matplotlib widget".

    figure = plt.figure(dpi=dpi, figsize=figsize)
    if not map_bbox: #if it's empty
        if zoom_frac != [0,1]:
            sub_trajs = common_processing.sub_trajs_from_frac(trajectories, zoom_frac)
            map_bbox = compute_bounding_box(itertools.chain(*sub_trajs),
                                            buffer=bbox_buffer)
        else:
            map_bbox = compute_bounding_box(itertools.chain(*trajectories),
                                            buffer=bbox_buffer)
    if not show_lines:
        linewidth=0

    color_maps = []

    for i, trajectory in enumerate(trajectories):
        if line_color != '':
            # call setup colors here insead at some point
            if isinstance(line_color, list):
                color_maps.append(coloring.get_constant_color_cmap(line_color[i]))
            else:
                color_maps.append(coloring.get_constant_color_cmap(line_color))
        elif color_map != '':
            if isinstance(color_map, list):
                color_maps.append(color_map[i])
            else:
                color_maps.append(color_map)
        elif gradient_hue != None:
            if isinstance(gradient_hue, list):
                color_maps.append(coloring.hue_gradient_cmap(gradient_hue[i]))
            else:
                color_maps.append(coloring.hue_gradient_cmap(gradient_hue))
        else:
           color_maps.append(coloring.hue_gradient_cmap(common_processing.hash_short_md5(trajectory[0].object_id)))

    if map_canvas == None:
        (map_canvas, map_actors) = render_map.render_map(domain='terrestrial',
                                            map_name='custom',
                                            map_bbox=map_bbox,
                                            map_projection = map_projection,
                                            region_size=region_size,
                                            draw_lonlat=draw_lonlat,
                                            draw_coastlines=draw_coastlines,
                                            draw_countries=draw_countries,
                                            draw_states=draw_states,
                                            draw_airports=draw_airports,
                                            draw_ports=draw_ports,
                                            draw_shorelines=draw_shorelines,
                                            draw_rivers=draw_rivers,
                                            draw_borders=draw_borders,
                                            draw_cities=draw_cities,
                                            fill_land=fill_land,
                                            fill_water=fill_water,
                                            tiles=tiles,
                                            **kwargs)

    # `dot_size*15` and `inewidth*0.8` below accounts for differing units between folium and cartopy
    paths.draw_traffic(traffic_map = map_canvas,
                       trajectory_iterable = trajectories,
                       color_map = color_maps,
                       color_scale = color_scale,
                       trajectory_scalar_generator = trajectory_scalar_generator,
                       trajectory_linewidth_generator=trajectory_linewidth_generator,
                       linewidth=linewidth*0.8,
                       dot_size=dot_size*15,
                       dot_color=dot_color,
                       show_points = show_points,
                       point_size = point_size*15,
                       point_color=point_color,
                       show_lines=show_lines,
                       transform=transform)
    # Don't support: label_objects, label_generator, label_kwargs, axes, zorder

    if show_distance_geometry:
        common_processing.render_distance_geometry('cartopy', distance_geometry_depth,
                                 trajectory, map_canvas)

    if not common_processing.in_notebook() or save:
        if filename:
            #plt.tight_layout()  #was giving warnings
            plt.savefig(filename)
        else:
            datetime_str = datetime.now().strftime("%Y-%m-%dT%H%M%S-%f")
            #plt.tight_layout()
            plt.savefig("trajs-"+datetime_str+".png")
    return map_canvas

# ----------------------------------------------------------------------

def render_heatmap(points,
                   trajectories=None,
                   map_canvas = None,
                   map_bbox=[],
                   bin_size=1,
                   colormap='gist_heat',
                   colorscale=matplotlib.colors.Normalize(),
                   zorder=10,
                   draw_lonlat=True,
                   fill_land=True,
                   fill_water=True,
                   draw_coastlines=True,
                   draw_countries=True,
                   draw_states=True,
                   draw_airports=False,
                   draw_ports=False,
                   draw_shorelines=False,
                   draw_rivers=False,
                   draw_borders=False,
                   draw_cities=False,
                   map_projection = None,
                   transform = cartopy.crs.PlateCarree(),
                   figsize=(4,2.25),
                   dpi=300,
                   bbox_buffer=(.3,.3),
                   tiles=None,
                   save = False,
                   filename = '',
                   **kwargs):
    """Render a histogram for the given map projection.

       For documentation on the parameters, please see render_trajectories
    """
    #tiles override cartopy map features
    if tiles != None:
        fill_land=False
        fill_water=False
        draw_coastlines=False
        draw_countries=False
        draw_states=False

    if not map_bbox: #if it's empty
        # bounding_box = compute_bounding_box(itertools.chain(*points),
        bounding_box = compute_bounding_box(points,
                                            buffer=bbox_buffer)
    else:
        bounding_box = BoundingBox2D(Point2D(map_bbox[0],
                                             map_bbox[1]),
                                     Point2D(map_bbox[2],
                                             map_bbox[3]))

    if map_canvas == None:
        (map_canvas, map_actors) = render_map.render_map(domain='terrestrial',
                                            map_name='custom',
                                            map_bbox=bounding_box,
                                            map_projection = map_projection,
                                            draw_lonlat=draw_lonlat,
                                            draw_coastlines=draw_coastlines,
                                            draw_countries=draw_countries,
                                            draw_states=draw_states,
                                            draw_airports=draw_airports,
                                            draw_ports=draw_ports,
                                            draw_shorelines=draw_shorelines,
                                            draw_rivers=draw_rivers,
                                            draw_borders=draw_borders,
                                            draw_cities=draw_cities,
                                            fill_land=fill_land,
                                            fill_water=fill_water,
                                            tiles=tiles,
                                            **kwargs)

    x_bin_boundaries = []
    y_bin_boundaries = []

    # Set up the boundaries for the latitude and longitude bins
    next_boundary = bounding_box.min_corner[0]
    while next_boundary < bounding_box.max_corner[0]:
        x_bin_boundaries.append(next_boundary)
        next_boundary += bin_size
    x_bin_boundaries.append(bounding_box.max_corner[0])

    next_boundary = bounding_box.min_corner[1]
    while next_boundary < bounding_box.max_corner[1]:
        y_bin_boundaries.append(next_boundary)
        next_boundary += bin_size
    y_bin_boundaries.append(bounding_box.max_corner[1])

    # This looks backwards, I know, but it's correct -- the first
    # dimension is rows, which corresponds to Y, which means latitude.
    density = numpy.zeros( shape = (len(y_bin_boundaries) - 1, len(x_bin_boundaries) - 1) )

    def point_to_bin(point):
        dx = point[0] - bounding_box.min_corner[0]
        dy = point[1] - bounding_box.min_corner[1]

        x_bucket = int(dx / bin_size)
        y_bucket = int(dy / bin_size)

        return (x_bucket, y_bucket)

    for point in points:
        try:
            (x, y) = point_to_bin(point)
            if (x >= 0 and x < len(x_bin_boundaries)-1 and
                y >= 0 and y < len(y_bin_boundaries)-1):
                density[y, x] += 1
        except ValueError: # trap NaN
            pass

    masked_density = masked_array.masked_less_equal(density, 0)

    # And finally render it onto the map.
    density_array = common_processing.draw_density_array(masked_density,
                                                x_bin_boundaries,
                                                y_bin_boundaries,
                                                map_canvas,
                                                bounding_box,
                                                colormap=colormap,
                                                colorscale=colorscale,
                                                zorder=zorder,
                                                axes=map_canvas)

    if not common_processing.in_notebook() or save:
            if filename:
                #plt.tight_layout()  #was giving warnings
                plt.savefig(filename)
            else:
                datetime_str = datetime.now().strftime("%Y-%m-%dT%H%M%S-%f")
                #plt.tight_layout()
                plt.savefig("heatmap-"+datetime_str+".png")
    return density_array

# ----------------------------------------------------------------------

# TODO (mjfadem): This appears to be OBE, may need to remove it
def geographic(map_projection,
               point_source,
               bin_size=1,
               colormap='gist_heat',
               colorscale=matplotlib.colors.Normalize(),
               zorder=10,
               axes=None):
    """Render a 2D histogram (heatmap) onto a geographic map

    Args:
      map_projection (Basemap): Map to render onto
      point_source (iterable): Sequence of TrajectoryPoint objects

    Keyword Args:
      bin_size (float): Histogram bins will be this many degrees on
         each size. Defaults to 1. (Default: 1)
      colormap (str or Matplotlib colormap): Color map for
         resulting image. Defaults to 'gist_heat'. (Default: 'gist_heat')
      colorscale (matplotlib.colors.Normalize or subclass): Mapping
         from histogram bin count to color. Defaults to a linear
         mapping (matplotlib.colors.Normalize(). The other useful
         value is matplotlib.colors.LogNorm() for a logarithmic
         mapping. You can specify a range if you want to but by
         default it will be adapted to the data. (Default: matplotlib.colors.Normalize())
      zorder (int): Rendering priority for the histogram. Objects
         with higher priority will be rendered on top of those with
         lower priority. Defaults to 2 (probably too low). (Default: 10)
      axes (matplotlib.axes.Axes): Axes instance to render into. If
         no value is specified we will use the current axes as returned
         by pyplot.gca(). (Default: None)

    Returns:
      List of actors added to the axes

    Side Effects:
      Actors for the histogram will be added to the current Matplotlib
      figure.

    Known Bugs:
      * The interface does not match the one for the Cartesian
        histogram. Most notably, you specify resolution explicitly
        for the Cartesian histogram and implicitly (via box size) for
        this one.

      * You can't specify a histogram area that encloses the north or
        south pole.

      * You can't specify a histogram area that crosses the longitude
        discontinuity at longitude = +/- 180. This should be relatively
        easy to fix.
    """

    bbox_lowerleft = Point2D(map_projection.llcrnrlon, map_projection.llcrnrlat)
    bbox_upperright = Point2D(map_projection.urcrnrlon, map_projection.urcrnrlat)

    span_x = ( bbox_upperright[0] - bbox_lowerleft[0] )
    span_y = ( bbox_upperright[1] - bbox_lowerleft[0] )

    if span_x < 0:
        span_x += 360
    if span_y < 0:
        span_y += 180

    x_bin_boundaries = []
    y_bin_boundaries = []

    # Set up the boundaries for the latitude and longitude bins
    next_boundary = bbox_lowerleft[0]
    while next_boundary < bbox_upperright[0]:
        x_bin_boundaries.append(next_boundary)
        next_boundary += bin_size
    x_bin_boundaries.append(bbox_upperright[0])

    next_boundary = bbox_lowerleft[1]
    while next_boundary < bbox_upperright[1]:
        y_bin_boundaries.append(next_boundary)
        next_boundary += bin_size
    y_bin_boundaries.append(bbox_upperright[1])

    # This looks backwards, I know, but it's correct -- the first
    # dimension is rows, which corresponds to Y, which means latitude.
    density = numpy.zeros( shape = (len(y_bin_boundaries) - 1, len(x_bin_boundaries) - 1) )

    def point_to_bin(point):
        x = point[0]
        y = point[1]

        dx = x - bbox_lowerleft[0]
        dy = y - bbox_lowerleft[1]

        x_bucket = int(dx / bin_size)
        y_bucket = int(dy / bin_size)

        return (x_bucket, y_bucket)


    for point in point_source:
        (x, y) = point_to_bin(point)
        if (x >= 0 and x < len(x_bin_boundaries)-1 and
            y >= 0 and y < len(y_bin_boundaries)-1):
            density[y, x] += 1

    masked_density = masked_array.masked_less_equal(density, 0)

    bbox = BoundingBox2D(bbox_lowerleft, bbox_upperright)

    return common_processing.draw_density_array(masked_density,
                              map_projection,
                              bbox,
                              colormap=colormap,
                              colorscale=colorscale,
                              zorder=zorder)

# ----------------------------------------------------------------------

# TODO (mjfadem): This appears to be OBE, may need to remove it
def cartesian(point_source,
              bbox_lowerleft,
              bbox_upperright,
              resolution=(400, 400),
              colormap='gist_heat',
              colorscale=matplotlib.colors.Normalize(),
              axes=None,
              zorder=2):
    """Draw a 2D histogram of points in a Cartesian space.

    For the purposes of this function, a 'point2d' is a tuple or list
    at least 2 elements long whose first two elements are numbers.

    Since we only traverse the point iterable once we require that
    you supply a bounding box. Any points outside this bounding
    box will be ignored.

    Args:
       point_source (iterable): Sequence of 2D points. This will
          be traversed only once.
       bbox_lowerleft (point2d): Lower left corner of bounding box
          for histogram
       bbox_upperright (point2d): Upper right corner of bounding box

    Keyword Args:
       resolution (two ints): Resolution for histogram (Default: (400, 400))
       colormap (str or Colormap): Colors to use for histogram (Default: 'gist_heat')
       colorscale (matplotlib.colors.Normalize or subclass): Mapping from bin counts to color. Useful values are matplotlib.colors.Normalize() and matplotlib.colors.LogNorm(). (Default: matplotlib.colors.Normalize())
       axes (matplotlib.axes.Axes): Axes to render into. Defaults to "current axes" as defined by Matplotlib. (Default: None)
       zorder (int): Image priority for rendering. Higher values will be rendered on top of actors with lower z-order. (Default: 2)

    Side Effects:
       Actors will be added to the supplied axes.

    Returns:
       A list of actors added to the Matplotlib figure.

    """

    x_coords = []
    y_coords = []

    for point in point_source:
        x_coords.append(point.x)
        y_coords.append(point.y)

    x_bins = numpy.linspace(bbox_lowerleft[0], bbox_upperright[0], resolution[0] + 1)
    y_bins = numpy.linspace(bbox_lowerleft[1], bbox_upperright[1], resolution[1] + 1)

    # Bin the latitude and longitude values to produce a count in each
    # box. Since numpy.histogram2d does not follow the Cartesian
    # convention of x-before-y (as documented in the numpy.histogram2D
    # docs) we have to supply (y, x) rather than (x, y).
    density, x_shape, y_shape = numpy.histogram2d(y_coords, x_coords,
                                                  [ y_bins, x_bins ])



    bbox = BoundingBox2D(bbox_lowerleft, bbox_upperright)

    return common_processing.draw_density_array(density,
                              identity_projection,
                              bbox,
                              colormap=colormap,
                              colorscale=colorscale,
                              zorder=zorder)
