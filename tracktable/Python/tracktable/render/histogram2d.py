#
# Copyright (c) 2014-2017 National Technology and Engineering
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
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


from __future__ import print_function, division, absolute_import

from tracktable.domain.cartesian2d import BasePoint as Point2D
from tracktable.domain.cartesian2d import BoundingBox as BoundingBox2D
from tracktable.domain.cartesian2d import identity_projection

# from ..core.geomath import latitude, longitude


import matplotlib.colors
import matplotlib.pyplot
import numpy
from numpy import ma as masked_array
from six.moves import range

def render_histogram(map_projection,
                     point_source,
                     bounding_box,
                     bin_size=1,
                     colormap='gist_heat',
                     colorscale=matplotlib.colors.Normalize(),
                     zorder=10,
                     axes=None):

    # This should wind up as a 2-dimensional point type
    try:
        bbox_span = bounding_box.max_corner - bounding_box.min_corner
    except AttributeError: # it might be a list
        bounding_box = BoundingBox2D(Point2D(bounding_box[0],
                                             bounding_box[1]),
                                     Point2D(bounding_box[2],
                                             bounding_box[3]))
        bbox_span = bounding_box.max_corner - bounding_box.min_corner

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


    for point in point_source:
        try:
            (x, y) = point_to_bin(point)
            if (x >= 0 and x < len(x_bin_boundaries)-1 and
                y >= 0 and y < len(y_bin_boundaries)-1):
                density[y, x] += 1
        except ValueError: # trap NaN
            pass

    x_bins_2d, y_bins_2d = numpy.meshgrid(x_bin_boundaries,
                                          y_bin_boundaries)

    masked_density = masked_array.masked_less_equal(density, 0)

    # And finally render it onto the map.
    return draw_density_array(masked_density,
                              map_projection,
                              bounding_box,
                              colormap=colormap,
                              colorscale=colorscale,
                              zorder=zorder)


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
    you supply a bounding box.  Any points outside this bounding
    box will be ignored.

    Args:
       point_source (iterable): Sequence of 2D points.  This will
          be traversed only once.
       bbox_lowerleft (point2d): Lower left corner of bounding box
          for histogram
       bbox_upperright (point2d): Upper right corner of bounding box

    Keyword Args:
       resolution (two integers): Resolution for histogram
       colormap (string or Colormap): Colors to use for histogram
       colorscale (matplotlib.colors.Normalize or subclass): Mapping from bin counts to color.  Useful values are matplotlib.colors.Normalize() and matplotlib.colors.LogNorm().
       axes (matplotlib.axes.Axes): Axes to render into.  Defaults to "current axes" as defined by Matplotlib.
       zorder (integer): Image priority for rendering.  Higher values will be rendered on top of actors with lower z-order.

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
    # box.  Since numpy.histogram2d does not follow the Cartesian
    # convention of x-before-y (as documented in the numpy.histogram2D
    # docs) we have to supply (y, x) rather than (x, y).
    density, x_shape, y_shape = numpy.histogram2d(y_coords, x_coords,
                                                  [ y_bins, x_bins ])



    bbox = BoundingBox(bbox_lowerleft, bbox_upperright)

    return draw_density_array(density,
                              identity_projection,
                              bbox,
                              colormap=colormap,
                              colorscale=colorscale,
                              zorder=zorder)


# ----------------------------------------------------------------------

def geographic(map_projection,
               point_source,
               bin_size=1,
               colormap='gist_heat',
               colorscale=matplotlib.colors.Normalize(),
               zorder=10,
               axes=None):
    """Render a 2D histogram (heatmap) onto a geographic map

    Args:
      mymap (Basemap): Map to render onto
      point_source (iterable): Sequence of TrajectoryPoint objects

    Kwargs:
      bin_size (float): Histogram bins will be this many degrees on
         each size.  Defaults to 1.
      colormap (string or Matplotlib colormap): Color map for
         resulting image.  Defaults to 'gist_heat'.
      colorscale (matplotlib.colors.Normalize or subclass): Mapping
         from histogram bin count to color.  Defaults to a linear
         mapping (matplotlib.colors.Normalize().  The other useful
         value is matplotlib.colors.LogNorm() for a logarithmic
         mapping.  You can specify a range if you want to but by
         default it will be adapted to the data.
      zorder (integer): Rendering priority for the histogram.  Objects
         with higher priority will be rendered on top of those with
         lower priority.  Defaults to 2 (probably too low).
      axes (matplotlib.axes.Axes): Axes instance to render into.  If
         no value is specified we will use the current axes as returned
         by pyplot.gca().

    Returns:
      List of actors added to the axes

    Side Effects:
      Actors for the histogram will be added to the current Matplotlib
      figure.

    Known Bugs:
      * The interface does not match the one for the Cartesian
        histogram.  Most notably, you specify resolution explicitly
        for the Cartesian histogram and implicitly (via box size) for
        this one.

      * You can't specify a histogram area that encloses the north or
        south pole.

      * You can't specify a histogram area that crosses the longitude
        discontinuity at longitude = +/- 180.  This should be relatively
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

    x_bins_2d, y_bins_2d = numpy.meshgrid(x_bin_boundaries,
                                          y_bin_boundaries)

    # Use basemap to convert the bin coordinates into world
    # (geographic) coordinates
#    xcoords, ycoords = map_projection(x_bins_2d, y_bins_2d)

#    pdb.set_trace()

    masked_density = masked_array.masked_less_equal(density, 0)

    bbox = BoundingBox(bbox_lowerleft, bbox_upperright)

    return draw_density_array(masked_density,
                              map_projection,
                              bbox,
                              colormap=colormap,
                              colorscale=colorscale,
                              zorder=zorder)

   
# ----------------------------------------------------------------------

def save_density_array(density, outfile):
    outfile.write('{} {}\n'.format(density.shape[0], density.shape[1]))
    rows = density.shape[0]
    columns = density.shape[1]

    for row in range(rows):
        for col in range(columns):
            outfile.write("{} ".format(density[row, col]))
        outfile.write("\n")

# ----------------------------------------------------------------------

def load_density_array(infile):
    first_line = infile.readline()
    words = first_line.strip().split(' ')
    dims = [ int(word) for word in words ]

    density = numpy.zeros(shape=(dims[0], dims[1]), dtype=numpy.int32)

    rows = dims[0]
    columns = dims[1]

    for row in range(rows):
        line = infile.readline()
        words = line.strip().split(' ')
        nums = [ int(word) for word in words ]
        for col in range(columns):
            density[row, col] = nums[col]

    return density

# ----------------------------------------------------------------------

def draw_density_array(density,
                       map_projection,
                       bounding_box,
                       colormap=None,
                       colorscale=None,
                       zorder=10,
                       axes=None):


    # Yes, it looks like we've got the indices backwards on
    # density.shape[].  Recall that the X coordinate refers to
    # columns, typically dimension 1, while the Y coordinate refers to
    # rows, typically dimension 0.
    x_bins = numpy.linspace(bounding_box.min_corner[0],
                            bounding_box.max_corner[0],
                            density.shape[1] + 1)

    y_bins = numpy.linspace(bounding_box.min_corner[1],
                            bounding_box.max_corner[1],
                            density.shape[0] + 1)

    x_bins_mesh, y_bins_mesh = numpy.meshgrid(x_bins, y_bins)

    # And finally render it onto the map.
    return [ matplotlib.pyplot.pcolormesh(x_bins_mesh,
                                          y_bins_mesh,
                                          density,
                                          cmap=colormap,
                                          norm=colorscale,
                                          zorder=zorder,
                                          axes=axes) ]

