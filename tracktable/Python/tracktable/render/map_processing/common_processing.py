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
tracktable.render.common_processing - Collection of functions that are commonly used across all of the rendering backends
"""

import hashlib
import logging
from math import ceil

import cartopy.mpl.geoaxes
import cartopy.crs
import folium as fol
import matplotlib
import matplotlib.colors
import matplotlib.pyplot
import numpy
import tracktable.domain.terrestrial as domain
from tracktable.core.geomath import distance, length, point_at_length_fraction
from tracktable.render.map_decoration import coloring

logger = logging.getLogger(__name__)

def common_processing(trajectories, obj_ids, line_color, color_map, gradient_hue):
    """Common processing functionality

    Args:
        trajectories (list): List of Trajectories
        obj_ids (list): List of IDs
        line_color (name of standard color as string, hex color string
            or matplotlib color object, or list of any of these): The
            single color to use for all the segments in each trajectory.
            Overrides color_map and gradient_hue values. Can be a list
            of matplotlib color name strings, hex color strings or
            matplotlib color objects the same length as the length of
            the list of trajectories.
        color_map (name of standard colormap as string or matplotlib
            color_map object or list of either): The color map to use
            in rendering the segments of each trajectory.
        gradient_hue (float or list of floats): hue or list of hues
            (one per trajectory) to be used in definig the gradient color
            map (dark to light) for the trajectories. Only used if
            line_color and color_map are not used (set to '').
            If line_color, color_map and gradient_hue are all unset the
            default behavior is to set the gradient_hue based on a hash
            of the object_id

    Returns:
        trajectories, line_color, color_map and gradient_hue

    """
    # handle a single traj as input
    if type(trajectories) is not list:
        trajectories = [trajectories]

    # filter trajectories list by obj_ids if specified
    if obj_ids != []:
        if type(obj_ids) is not list:
            trajectories = [traj for traj in trajectories \
                            if traj[0].object_id == obj_ids]
        else:
            filtered_trajs = []
            for obj_id in obj_ids:
                matched = [traj for traj in trajectories \
                            if traj[0].object_id == obj_id]
                filtered_trajs+=matched
            trajectories = filtered_trajs

    # now handle some color processing

    # translate strings into colormaps
    if type(color_map) is str and color_map != '':
        color_map = matplotlib.cm.get_cmap(color_map)
    elif type(color_map) is list:
        for i, cm in enumerate(color_map):
            if type(cm) is str:
                color_map[i] = matplotlib.cm.get_cmap(cm)

    # TODO make this into a function called 3 times
    # Handle too few colors
    if type(line_color) is list and len(trajectories) > len(line_color):
        times_to_repeat = ceil(len(trajectories)/len(line_color))
        line_color = line_color * times_to_repeat

    # Handle too few color maps
    if type(color_map) is list and len(trajectories) > len(color_map):
        times_to_repeat = ceil(len(trajectories)/len(color_map))
        color_map = color_map * times_to_repeat

    # Handle too few hues (say that 5 times fast) ;)
    if type(gradient_hue) is list and len(trajectories) > len(gradient_hue):
        times_to_repeat = ceil(len(trajectories)/len(gradient_hue))
        gradient_hue = gradient_hue * times_to_repeat

    return trajectories, line_color, color_map, gradient_hue

# ----------------------------------------------------------------------

def hash_short_md5(string):
    """Given any string, returns a number between 0 and 1. The same
       number is always returned given the same string. Internally uses
       hashlib.md5, but only uses the first quarter of the full hash

    Args:
        string (str): String to be hashed

    Returns:
        0 or 1
    """
    return int(hashlib.md5(string.encode('utf-8')).hexdigest()[:8],
               base=16)/((2**32)-1)
    # perceived brightness (may be useful later)
    # sqrt(R*R*.241 + G*G*.691 + B*B*.068)

# ----------------------------------------------------------------------

def path_length_fraction_generator(trajectory):
    """Generator to produce path length fraction scalars
    A genertor that given a trajectory will generate a scalar for each
    point such that each scalar represents the fraction of the total
    length along the path at the associated point.

    Arguments:
        trajectory (Trajectory): The trajectory to use for generating scaler values

    Returns:
        Fraction length scalar values for each point in the trajectory

    """

    dist_fractions = []
    prev_point = trajectory[0]
    cumulative_distance = 0
    for point in trajectory[1:]:
        cumulative_distance += distance(prev_point,point)
        dist_fractions.append(cumulative_distance)
        prev_point = point
    if cumulative_distance != 0:
        dist_fractions = [d / cumulative_distance for d in dist_fractions]
    return dist_fractions

# ----------------------------------------------------------------------

def progress_linewidth_generator(trajectory):
    """Generator to produce progress linewidth scalars
    A generator that given a trajectory will generate a scalar for each
    point such that each scalar represents a good width value for the
    fraction of points that come before that point in the trajectory.

    Arguments:
        trajectory (Trajectory): The trajectory to use for generating scaler values

    Returns:
        Linewidth scalar values for each point in the trajectory

    """
    widths = []
    tlen = len(trajectory)
    for i, point in enumerate(trajectory[1:]):
        widths.append((((i+1)/tlen)*5.0)+0.37)
    return widths
    # another way:
    # annotator = tracktable.feature.annotations.retrieve_feature_function('progress')
    # annotator(trajectory)

# ----------------------------------------------------------------------

def point_tooltip(current_point):
    """Formats the tooltip string for a point

    Args:
        current_point (point): Current point of the trajectory

    Returns:
        Current points timestamp

    """

    return current_point.timestamp.strftime("%H:%M:%S")

# ----------------------------------------------------------------------

def point_popup(current_point, point_popup_properties):
    """Formats the popup string for a point

    Args:
        current_point (point): Current point of the trajectory
        point_popup_properties (list): Point properties

    Returns:
        String of point properties

    """

    popup_str_point = str(current_point.object_id)+'<br>'+ \
        current_point.timestamp.strftime("%H:%M:%S")+'<br>Lat='+ \
        str(current_point[1])+'<br>Lon='+str(current_point[0])
    if point_popup_properties and point_popup_properties[0] == '*':
        for (name, value) in current_point.properties.items():
            popup_str_point += '<br>'+name+': '+str(value)
    else:
        for prop_str in point_popup_properties:
            if prop_str in current_point.properties:
                popup_str_point += '<br>'+prop_str+': '+ \
                    str(current_point.properties[prop_str])
    return popup_str_point

# ----------------------------------------------------------------------

def in_notebook():
    """Returns True if run within a Jupyter notebook, and false otherwise
    """
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip == None:
            return False
        if 'IPKernelApp' not in ip.config:
            return False
    except ImportError:
        return False
    return True

# ----------------------------------------------------------------------

def render_line(backend, map_canvas, line_coords, control_color, weight, tooltip):
    """Renders a line onto a cartopy or folium map

    Args:
        backend (str): Backend to use rendering into. Only supports 'cartopy' and 'folium'
        map_canvas (GeoAxes): The canvas where the line will be rendered
        line_coords (tuple): Lon lat coordinates where to render the line
        control_color (float): Color of the rendered line
        weight (int): Linewidth
        tooltip (str): Value to display for the line such as ``object_id``

    Returns:
        No return value

    """
    coords = list(zip(*line_coords))
    if backend=='cartopy':
        map_canvas.plot(coords[1], coords[0], color=control_color,
                        linewidth=weight, marker='o', ms=1, fillstyle='none',
                        transform=cartopy.crs.Geodetic())
    elif backend=="folium":
        fol.PolyLine(line_coords, color=control_color, weight=weight,
                 tooltip=tooltip).add_to(map_canvas)
    else:
        logger.error("Unsupported backend unable to render line.")

# ----------------------------------------------------------------------

def render_distance_geometry(backend, distance_geometry_depth,
                             traj, map_canvas):
    """Renders the distance geometry calculations to the folium map

    Args:
        backend (str): Backend to render with, either ``cartopy`` or ``folium``
        distance_geometry_depth (int): The depth of the distance geometry calculation
        traj (Trajectory): The trajectory
        map_canvas (GeoAxes): The canvas where distance geometry will be rendered

    Returns:
        No return value

    """
    #cp=control_point
    cp_colors = ['red', 'blue', 'yellow', 'purple']+ \
        [coloring.random_color() for i in range(4, distance_geometry_depth)]
    traj_length = length(traj)
    for num_cps in range(2,distance_geometry_depth+2):
        cp_increment = 1.0/(num_cps-1)
        cp_fractions = [cp_increment * i for i in range(num_cps)]
        cps = [point_at_length_fraction(traj, t) for t in cp_fractions]
        cp_coords = [(round(point[1],7), round(point[0],7)) for point in cps]
        for i, cp_coord in enumerate(cp_coords):
            normalization_term = traj_length*cp_increment
            control_color = cp_colors[num_cps-2]
            for j in range(len(cps)-1):
                line_coords = [(round(cps[j][1],7), round(cps[j][0],7)),
                               (round(cps[j+1][1],7), round(cps[j+1][0],7))]
                val = round(distance(cps[j], cps[j+1]) / normalization_term, 4)
                tooltip = str(j+1)+'/'+str(len(cps)-1)+' = '+str(val)
                if backend == 'cartopy':
                    render_line('cartopy', map_canvas, line_coords, control_color, .5, tooltip)
                else:
                    render_line('folium', map_canvas, line_coords, control_color, 1, tooltip)
            popup=str(traj[0].object_id)+'<br>'+ \
                traj[i].timestamp.strftime("%H:%M:%S")+'<br>Latitude='+ \
                str(round(traj[i][1],7))+'<br>Longitude='+str(round(traj[i][0],7))
            if backend != 'cartopy': #cartopy renders markers with lines
                fol.CircleMarker(cp_coord, radius=4, fill=True,
                                 color=control_color,
                                 tooltip=round(cp_fractions[i], 7),
                                 popup=popup).add_to(map_canvas)

# ----------------------------------------------------------------------

def sub_trajs_from_frac(trajectories, zoom_frac):
    """Create sub-trajectories from a given zoom fraction

    Args:
        trajectories (Trajectory): Trajectories to create sub-trajectories from
        zoom_frac (list): Fraction list to segment trajectories

    Returns:
        sub_trajs

    """
    # Eventually replace with common method to do this, for now manually create sub-traj from given fraction
    sub_trajs = []
    for traj in trajectories:
        # Make start and end points
        seg_start = point_at_length_fraction(traj, zoom_frac[0])
        seg_end = point_at_length_fraction(traj, zoom_frac[1])

        # Must be a better way to do this!
        first_in_mid = 0
        for j, point in enumerate(traj):
            if point.timestamp >= seg_start.timestamp:
                first_in_mid = j
                break

        last_in_mid = len(traj)
        for j, point in reversed(list(enumerate(traj))):
            if point.timestamp <= seg_end.timestamp:
                last_in_mid = j
                break

        points = [seg_start]
        for point in traj[first_in_mid:last_in_mid+1]:
            points.append(point)
        points.append(seg_end)

        traj_mid = domain.Trajectory.from_position_list(points)
        #traj_mid.set_property("id",
        sub_trajs.append(traj_mid)
    return sub_trajs

# ----------------------------------------------------------------------

def save_density_array(density, outfile):
    """Save and output the density array to a file.

    Args:
       density (tuple): Density to be saved to file
       outfile (str): Filename to save output

    Returns:
       No return value.

    """
    outfile.write('{} {}\n'.format(density.shape[0], density.shape[1]))
    rows = density.shape[0]
    columns = density.shape[1]

    for row in range(rows):
        for col in range(columns):
            outfile.write("{} ".format(density[row, col]))
        outfile.write("\n")

# ----------------------------------------------------------------------

def load_density_array(infile):
    """Load the density array from a file.

    Args:
       infile (str): Filename for input

    Returns:
       The density array in the file.

    """

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
                       x_bin_boundaries: numpy.ndarray,
                       y_bin_boundaries: numpy.ndarray,
                       map_projection,
                       bounding_box,
                       colormap=None,
                       colorscale=None,
                       zorder=10,
                       axes=None):
    """Render a histogram for the given map projection.

    Args:
       density (iterable): Density array that will be drawn onto the map
       x_bin_boundaries (NumPy array, 1xN): Boundaries of bins in X/longitude
       y_bin_boundaries (NumPy array, 1xM): Boundaries of bins in Y/latitude
       map_projection (Basemap): Map to render onto
       bounding_box (point2d): Bounding box of area to gdraw the

    Keyword Args:
       colormap (str or Colormap): Colors to use for histogram (Default: None)
       colorscale (matplotlib.colors.Normalize or subclass): Mapping from bin counts to color. Useful values are matplotlib.colors.Normalize() and matplotlib.colors.LogNorm(). (Default: None)
       zorder (int): Image priority for rendering. Higher values will be rendered on top of actors with lower z-order. (Default: 10)
       axes (matplotlib.axes.Axes): Axes to render into. Defaults to "current axes" as defined by Matplotlib. (Default:None)

    Returns:
       The density rendered onto the map.

    """

    # Yes, it looks like we've got the indices backwards on
    # density.shape[]. Recall that the X coordinate refers to
    # columns, typically dimension 1, while the Y coordinate refers to
    # rows, typically dimension 0.
    x_bins_mesh, y_bins_mesh = numpy.meshgrid(x_bin_boundaries, y_bin_boundaries)

    # And finally render it onto the map.
    if axes is None:
        axes = matplotlib.pyplot.gca()

    # Are we in a GeoAxes instance?  If so, we need to tell pcolormesh
    # how to transform the density map to whatever map projection
    # we're using.
    if isinstance(axes, cartopy.mpl.geoaxes.GeoAxes):
        projection_kwargs = {"transform": cartopy.crs.PlateCarree()}
    else:
        projection_kwargs = {}

    mesh = axes.pcolormesh(
        x_bins_mesh,
        y_bins_mesh,
        density,
        cmap=colormap,
        norm=colorscale,
        zorder=zorder,
        **projection_kwargs
    )

    return [mesh]