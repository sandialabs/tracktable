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
tracktable.render.coloring - Collection of functions for coloring trajectories
"""

import random

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, hsv_to_rgb, rgb_to_hsv, to_rgb
from tracktable.render.map_processing import common_processing


def get_constant_color_cmap(color):
    """Returns a colormap containing the single color given

    Args:
        color (str): Color to get colormap from
    Returns:
        Returns a colormap containing the single color given

    """

    if isinstance(color, str):
        return ListedColormap(np.array(matplotlib.colors.to_rgba(color)))
    else:
        return ListedColormap(np.array(color)) #TODO handle errors

# ----------------------------------------------------------------------

def get_color_mapper(color_scale, color_map):
    """Returns an object that can translate scalars into colors
       Returns an object that can produce for any scalar the correct RGBA
       color from the given color_map using the given color_scale.

    Args:
        color_scale (matplotlib.colors.Normalize() or LogNorm()): Linear or logarithmic scale
        color_map (name of standard colormap as string or matplotlib
            color_map object or list of either): The color map to use
            in rendering the segments of each trajectory.

    Returns:
       An object that can translate scalars into colors
       and an object that can produce for any scalar the correct RGBA
       color from the given color_map using the given color_scale.

    """
    cmap = plt.get_cmap(color_map)
    return matplotlib.cm.ScalarMappable(norm=color_scale, cmap=cmap)

# ----------------------------------------------------------------------

def hue_gradient_cmap(hue, chop_frac=.29):
    """Returns a color map which progresses from dark to light given a
       specific hue

    Args:
       hue (str or float): the hue to generate the color map for. (0 to 1)
       chop_frac (float): the fraction of the beginning and end of the total
           gradient to chop off so as to not be too light or dark.

    Returns:
       color map object which can be passed to matplotlib's cmap param
           or render_trajectories color_map
    """
    if isinstance(hue, str):
        hue = rgb_to_hsv(to_rgb(hue))[0]
    rgb = hsv_to_rgb([hue, 1.0, 1.0])
    N = 128
    vals = np.ones((N*2, 4))
    vals[:, 0] = np.concatenate([np.linspace(rgb[0]*chop_frac, rgb[0], N), np.linspace(rgb[0], 1.0-((1.0-rgb[0])*chop_frac), N)])
    vals[:, 1] = np.concatenate([np.linspace(rgb[1]*chop_frac, rgb[1], N), np.linspace(rgb[1], 1.0-((1.0-rgb[1])*chop_frac), N)])
    vals[:, 2] = np.concatenate([np.linspace(rgb[2]*chop_frac, rgb[2], N), np.linspace(rgb[2], 1.0-((1.0-rgb[2])*chop_frac), N)])
    return ListedColormap(vals)

# ----------------------------------------------------------------------

# TODO some of this processing can be moved outside of the loop!
def setup_colors(line_color, color_map, gradient_hue, point_color,
                 color_scale, objid, i, linewidth_generator):
    """ Processes the color optins and returns the current color maps
    This function determines what the current color map should be for
    lines and points given the various releated parameters and returns
    color maps for points and for lines.

    Args:
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
        point_color = (name of standard color as string, hex color string
            or matplotlib color object, or list of any of these): The
            single color to use for all the points in each trajectory.
            Can be a list of matplotlib color name strings, hex color
            strings or matplotlib color objects the same length as the
            length of the list of trajectories. If not specified, the
            color matches the segment incident at the point.
        color_scale (matplotlib.colors.Normalize() or LogNorm()): Linear or logarithmic scale
        objid (str): ID used for MD5 Hash
        i (int): Index for lists
        linewidth_generator (function): Function to generate
            linewidths

    Returns:
        Current color maps

    """

    if line_color != '' and line_color != []:
        if isinstance(line_color, list):
            current_cmap = ListedColormap([line_color[i]])
        else:
            current_cmap = ListedColormap([line_color])
    elif color_map != '' and color_map != []:
        if isinstance(color_map, list):
            current_cmap = color_map[i]
        else:
            current_cmap = color_map
    elif gradient_hue != None and gradient_hue != []:
        if isinstance(gradient_hue, list):
            current_cmap = hue_gradient_cmap(gradient_hue[i])
        else:
            current_cmap = hue_gradient_cmap(gradient_hue)
    else:
        current_cmap = hue_gradient_cmap(common_processing.hash_short_md5(objid))

    if point_color != '':
        if isinstance(point_color, list):
            current_point_cmap = ListedColormap([point_color[i]])
        else:
            current_point_cmap = ListedColormap([point_color])
    else:
        current_point_cmap = hue_gradient_cmap(common_processing.hash_short_md5(objid))

    # make color mapper if needed
    mapper = None
    point_mapper = None
    if type(current_cmap) is not ListedColormap \
       or len(current_cmap.colors) != 1 or linewidth_generator != None:
        mapper = get_color_mapper(color_scale, current_cmap)
    if type(current_point_cmap) is not ListedColormap \
       or len(current_point_cmap.colors) != 1:
        point_mapper = get_color_mapper(color_scale,
                                        current_cmap)

    return current_cmap, current_point_cmap, mapper, point_mapper

# ----------------------------------------------------------------------

def random_hue():
    """Returns a random hue value (0 to 1)
    """
    return random.uniform(0,1)

# ----------------------------------------------------------------------

def random_color():
    """Returns a random RGB color in hex string format
    """
    r = lambda: random.randint(0,255)
    return '#{:02x}{:02x}{:02x}'.format(r(), r(), r())

# ----------------------------------------------------------------------

def matplotlib_cmap_to_dict(colormap_name,
                            num_colors=16):
    """Convert a Matplotlib colormap into a dict for Folium

    Folium expects its color maps as a dictionary whose keys
    are floats between zero and one and whose values are the
    color to which that value should be mapped.

    Arguments:
        colormap_name (string): Name of one of Matplotlib's built-in
            color maps.

    Keyword Arguments:
        num_colors (int): How many entries to put into the output.
            Defaults to 16.

    Returns:
        Colormap in dictionary format

    Raises:
        ValueError: no such color map exists

    Note:
        It would be easy to extend this function to fit the
        color map to a range other than [0, 1] or to make it use a
        logarithmic scale (or any other scale) instead of linear.
        Ask, or just do it, if you'd like this.
    """

    mpl_cmap = matplotlib.pyplot.get_cmap(colormap_name)
    sample_points = np.linspace(0, 1, num_colors)
    output = dict()
    for sample_value in sample_points:
        output[str(float(sample_value))] = matplotlib.colors.to_hex(
            mpl_cmap(sample_value)
        )
    return output