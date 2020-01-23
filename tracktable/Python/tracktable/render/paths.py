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


"""
tracktable.render.paths - Functions to render trajectories as curves on a map

If you're trying to figure out how to render a bunch of trajectories,
take a look at draw_traffic and at
tracktable/examples/render_trajectories_from_csv.py.  Those will get you
pointed in the right direction.

"""

from __future__ import print_function, absolute_import, division

from tracktable.core import logging

import math
import sys
import matplotlib
import matplotlib.collections
import matplotlib.colors
from io import StringIO
from matplotlib.collections import LineCollection
from six.moves import range
import numpy


# ----------------------------------------------------------------------

def remove_duplicate_points(trajectory):
    """Create a new trajectory with no adjacent duplicate points

    Duplicate positions in a trajectory lead to degenerate line
    segments.  This, in turn, gives some of the back-end renderers
    fits.  The cleanest thing to do is to use the input trajectory to
    compute a new one s.t. no segments are degenerate.

    There's still one problem case: if the entire trajectory is a
    single position, you will get back a trajectory where the only two
    points (beginning and end) are at the same position.

    Args:
       trajectory (tracktable.core.Trajectory): trajectory to de-duplicate

    Returns:
       New trajectory with some of the points from the input
    """

    new_points = []
    last_point = None
    for point in trajectory:
        if ((not last_point) 
                or (point[1] != last_point[1]) 
                or (point[0] != last_point[0])):
            new_points.append(point)
            last_point = point

    if len(new_points) == 1:
        new_points.append(trajectory[-1])

    logger = logging.getLogger(__name__)
    logger.debug(("remove_duplicate_points: old trajectory has length {}, "
                  "new trajectory has length {}").format(
                        len(trajectory), len(new_points)))

    return type(trajectory).from_position_list(new_points)

# ----------------------------------------------------------------------

def points_to_segments(point_list, maximum_distance=None):

    """points_to_segments(point_list, maximum_distance=None) -> segment_list

    Given a list of N points, create a list of the N-1 line segments
    that connect them.  Each segment is a list containing two points.
    If a value is supplied for maximum_distance, any segment longer than
    that distance will be ignored.

    In English: We discard outliers.
    """

    def cart2_distance(point1, point2):
        """Cartesian distance between points defined as tuples"""
        return math.sqrt(
            (point2[0]-point1[0])*(point2[0]-point1[0]) +
            (point2[1]-point1[1])*(point2[1]-point1[1])
        )

    # Now that we know the thresholds, we can go through and build the 
    # actual segments.
    segments = []
    logger = None

    # Python 3: An object of type zip does not have a len() so we need
    # to turn this into an actual list
    point_list = list(point_list)
    for i in range(len(point_list) - 1):
        point1 = point_list[i]
        point2 = point_list[i+1]
        segment_length = cart2_distance(point_list[i], point_list[i+1])
        if maximum_distance and segment_length > maximum_distance:
            if logger is None:
                logger = logging.getLogger(__name__)
            logger.debug(
                ("WARNING: Discarding outlier line segment with length {}, {} "
                 "times the maximum length of {}.").format(
                     segment_length,
                     segment_length/maximum_distance, 
                     maximum_distance))
            segments.append((point1, point1))
        else:
            segments.append((point1, point2))

    return segments


# ----------------------------------------------------------------------

def draw_traffic(traffic_map,
                 trajectory_iterable,
                 color_map='BrBG',
                 color_scale=matplotlib.colors.Normalize(),
                 trajectory_scalar_generator=None,
                 trajectory_linewidth_generator=None,
                 linewidth=1,
                 dot_size=2,
                 dot_color='white',
                 label_objects=False,
                 label_generator=None,
                 label_kwargs=dict(),
                 axes=None,
                 zorder=8):
    """Draw a set of (possibly decorated trajectories.

    Args:
       traffic_map: Map projection (Basemap or Cartesian)
       color_map: String (colormap name) or Matplotlib colormap object
       color_scale: Linear or logarithmic scale (matplotlib.colors.Normalize() or LogNorm())
       trajectory_scalar_generator: Function to generate scalars for a trajectory (default None)
       trajectory_linewidth_generator: Function to generate path widths for a trajectory (default None)
       linewidth: Constant linewidth if no generator is supplied (default 0.1, measured in points)
       dot_size: Radius (in points, default 2) of spot that will be drawn at the head of each trajectory
       dot_color: Color of spot that will be drawn at the head of each trajectory
       label_objects: Boolean (default False) deciding whether to draw object_id at head of each trajectory
       label_generator: Function to generate label for a trajectory (default None)
       label_kwargs: Dictionary of arguments to be passed to labeler (FIXME)
       axes: Matplotlib axes object into which trajectories will be rendered
       zorder: Layer into which trajectories will be drawn (default 8).

    Returns:
       List of Matplotlib artists



    Parameters in more detail:


    ``traffic_map``: Map instance (no default)

    Cartopy GeoAxes instance of the space in which trajectories will be
    rendered.  We don't actually render into this object.  Instead we
    use it to project points from longitude/latitude space down into
    the map's local coordinate system.  Take a look at
    tracktable.render.maps for several ways to create this map including
    a few convenience functions for common regions.

    ``trajectory_iterable``: iterable(Trajectory) (no default)

    Sequence of Trajectory objects.  We will traverse this exactly
    once.  It can be any Python iterable.

    ``color_map``: Matplotlib color map or string (default 'BrBG')

    Either a Matplotlib color map object or a string denoting the name
    of a registered color map.  See the Matplotlib documentation for
    the names of the built-ins and the tracktable.render.colormaps
    module for several more examples and a way to create your own.

    ``color_scale``: Matplotlib color normalizer (default Normalize())

    Object that maps your scalar range onto a colormap.  This will
    usually be either matplotlib.colors.Normalize() or
    matplotlib.colors.LogNorm() for linear and logarithmic mapping
    respectively.

    ``trajectory_scalar_generator``: function(Trajectory) -> list(float)

    You can color each line segment in a trajectory with your choice
    of scalars.  This argument must be a function that computes those
    scalars for a trajectory or else None if you don't care.  The
    scalar function should take a Trajectory as its input and return a
    list of len(trajectory) - 1 scalars, one for each line segment to
    be drawn.

    ``trajectory_linewidth_generator``: function(Trajectory) -> list(float)

    Just as you can generate a scalar (and thus a color) for each line
    segment, you can also generate a width for that segment.  If you
    supply a value for this argument then it should take a Trajectory
    as its input and return a list of len(trajectory)-1 scalars
    specifying the width for each segment.  This value is measured in
    points.  If you need a single linewidth all the way through use
    the 'linewidth' argument.

    ``linewidth``: float (default 0.1)

    This is the stroke width measured in points that will be used to
    draw the line segments in each trajectory.  If you need different
    per-segment widths then use trajectory_linewidth_generator.

    ``dot_size``: float (default 2)

    If this value is non-zero then a dot will be drawn at the head of
    each trajectory.  It will be dot_size points in radius and will be
    colored with whatever scalar is present at the head of the
    trajectory.

    TODO: Add a dot_size_generator argument to allow programmatic
    control of this argument.

    ``label_objects``: boolean (default False)

    You can optionally label the head of each trajectory.  To do so
    you must supply 'label_objects=True' and also a function for the
    label_generator argument.

    ``label_generator``: function(TrajectoryPoint) -> string

    Construct a label for the specified trajectory.  The result must
    be a string.  This argument is ignored if label_objects is False.

    TODO: Test whether Unicode strings will work here.

    ``label_text_kwargs``: dict (default empty)

    We ultimately render labels using matplotlib.axes.Text().  If you
    want to pass in arguments to change the font, font size, angle or
    other parameters, specify them here.

    ``axes``: matplotlib.axes.Axes (default pyplot.gca())

    This is the axis frame that will hold the Matplotlib artists that
    will render the trajectories.  By default it will be whatever
    pyplot thinks the current axis set is.

    ``zorder``: int (default 8)

    Height level where the trajectories will be drawn.  If you want
    them to be on top of the map and anything else you draw on it then
    make this value large.  It has no range limit.
    """

    logger = logging.getLogger(__name__)
    all_artists = []

    lead_point_scalars = []
    lead_point_x = []
    lead_point_y = []
    lead_point_labels = []

    # If the user hasn't specified a custom linewidth function then we
    # use the value of the linewidth argument throughout.
    if trajectory_linewidth_generator is None:
        trajectory_linewidth_generator = lambda trajectory: [ linewidth ] * len(trajectory)

    # If there is no scalar generator then we will automatically
    # generate scalars for each trajectory that begin at 0 and end at
    # 1.
    if trajectory_scalar_generator is None:
        trajectory_scalar_generator = lambda trajectory: numpy.linspace(0, 1, len(trajectory))

    if label_generator is None:
        if label_objects:
            logger.warning(("Object labels requested in draw_traffic but no "
                            "label formatter is present.  Labels will look "
                            "weird."))
            label_generator = lambda thing: thing

    if axes is None:
        axes = matplotlib.pyplot.gca()

    trajectory_number = 0
    total_points = 0
    max_batch_size = 1000

    current_batch_paths = []
    current_batch_scalars = []
    current_batch_linewidths = []

    # We want to ignore individual segments that span most of the way across 
    # the map.  These are almost always errors in the data, especially where
    # segments cross the limb of the map.
    if hasattr(traffic_map, 'get_extent'):
        map_extent = traffic_map.get_extent()
        x_span = map_extent[2] - map_extent[0]
        y_span = map_extent[3] - map_extent[1]
        max_segment_length = 0.5 * max(x_span, y_span)
    else:
        # The above kluge is really only there for terrestrial maps so
        # that we can detect and ignore points that cross the map
        # discontinuity.  If we're in Cartesian-land then it's not a
        # problem.
        max_segment_length = None

    num_trajectories_rendered = 0
    num_trajectories_examined = 0

    for trajectory in trajectory_iterable:
        num_trajectories_examined += 1

        if len(trajectory) < 2:
            continue

        trajectory = remove_duplicate_points(trajectory)

        local_x = numpy.zeros(len(trajectory))
        local_y = numpy.zeros(len(trajectory))

        trajectory_number += 1
        num_trajectories_rendered += 1

        total_points += len(trajectory)

        # First we convert the longitude/latitude points in the
        # trajectory to coordinates in the map projection's native
        # space
        for i in range(len(trajectory)):
            local_x[i] = trajectory[i][0]
            local_y[i] = trajectory[i][1]

        # Now we turn that list of n points into a list of n-1 line
        # segments.  We shouldn't have any degenerate segments because
        # of the call to remove_duplicate_points() earlier.

        local_segments = points_to_segments(
            zip(local_x, local_y), 
            maximum_distance=max_segment_length)

        if len(local_segments) > 0:
            # Save the line segments, linewidths, scalars for the
            # whole path -- we'll render a bunch of them together in a
            # batch
            local_scalars = trajectory_scalar_generator(trajectory)
            current_batch_linewidths.append(
                trajectory_linewidth_generator(trajectory)[0:-1])
            current_batch_paths.append(local_segments)
            current_batch_scalars.append(local_scalars[0:-1])

            # The lead point is the last point in the trajectory
            if label_generator is not None:
                lead_point_labels.append(label_generator(trajectory[-1]))
            lead_point_x.append(local_x[-1])
            lead_point_y.append(local_y[-1])
            lead_point_scalars.append(local_scalars[-1])

        if len(current_batch_paths) >= max_batch_size:
            # Now we've processed some traffic and made it into line
            # segments.  Time to create the line segment collection that we
            # can plot.
            segment_collection = LineCollection(numpy.vstack(
                                                    current_batch_paths),
                                                norm=color_scale,
                                                cmap=color_map,
                                                linewidth=numpy.hstack(
                                                    current_batch_linewidths),
                                                zorder=zorder)

            stacked_scalars = numpy.hstack(current_batch_scalars)
            segment_collection.set_array(stacked_scalars)

            all_artists.append(segment_collection)
            axes.add_collection(segment_collection)

            current_batch_scalars = []
            current_batch_linewidths = []
            current_batch_paths = []

    # one more batch now that we're done
    if len(current_batch_paths) > 0:
        segment_collection = LineCollection(numpy.vstack(current_batch_paths),
                                            norm=color_scale,
                                            cmap=color_map,
                                            linewidth=numpy.hstack(
                                                current_batch_linewidths),
                                            zorder=zorder)

        stacked_scalars = numpy.hstack(current_batch_scalars)
        segment_collection.set_array(stacked_scalars)

        all_artists.append(segment_collection)

        axes.add_collection(segment_collection)

        current_batch_scalars = []
        current_batch_linewidths = []
        current_batch_paths = []

    if len(lead_point_x) > 0:
        if dot_size:
            if zorder:
                dot_zorder = zorder+1
            else:
                dot_zorder = None

            if dot_color == 'body':
                dot_color_kwargs = {'cmap': color_map,
                                    'c': lead_point_scalars}
            else:
                dot_color_kwargs = {'c': dot_color}

            dot_collection = traffic_map.scatter(lead_point_x, lead_point_y,
                                                 s=dot_size,
                                                 linewidth=0,
                                                 marker='o',
                                                 zorder=dot_zorder,
                                                 **dot_color_kwargs)
            all_artists.append(dot_collection)

        if label_objects:
            for (x, y, label) in zip(
                    lead_point_x, lead_point_y, lead_point_labels):
                all_artists.append(axes.text(x, y, label, **label_kwargs))

    return all_artists


def unwrap_path(locs):
    """
    Function:
        Inspects a list of [lat, lon] coordinates. If the trajectory crosses 
	the antimeridian (180 deg. Long), 'unwrap' the trajectory by projecting
	longitudinal values onto >+180 or <-180. This will prevent horizontal
	lines from streaking across a mercator projection, when plotting the
	trajectory in mapping packages like Folium. Operates by comparing pairs
	of elements (coord. point tuples) for the entire list.
    
    Input:
        locs: a list of (lat,lon) tuples

    Output: 
        None
        modifies the locs[] list in-place.
    """

    # 't' is an arbitrary threshold for comparing suqsequent points. If they are 'far enough' apart, 
    #   then we assume they must be on opposite sides of the antimeridian.
    t = 320
    for i in range(1,len(locs)):
        if abs(locs[i][1] - locs[i-1][1]) > t:
            if locs[i-1][1] < 0:
                # i-1 point in Western Hemisphere
                locs[i] = (locs[i][0],locs[i][1]-360)
            else:
                # i-1 point in Eastern Hemisphere
                locs[i] = (locs[i][0],locs[i][1]+360)
    
    return

