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
tracktable.render.heatmaps - render heatmaps in python

This is a set of functions that intend to allow user-friendly rendering
of heatmaps. A user should be able to simply use the funection
interactive_heatmap(points) passing a single parameter that is a list
of points and get a rendering of those points, whether
running as an interactive map inside of a notebook or from the command
line and saved as a static image to a file.
"""

from datetime import datetime

import folium as fol
import matplotlib
import numpy as np
from folium.plugins import HeatMap
from tracktable.render import render_trajectories

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
        output[sample_value] = matplotlib.colors.to_hex(
            mpl_cmap(sample_value)
        )
    return output

# ----------------------------------------------------------------------


def interactive_heatmap(points,
                        trajectories=None,
                        weights=None,
                        color_map='viridis',
                        tiles='cartodbdark_matter',
                        attr='.',
                        crs="EPSG3857",
                        show = False,
                        save = False,
                        filename = ''):
    """Creates an interactive heatmap vizulization

    Args:
        points (list): list of points

    Keyword Arguments:
        trajectories: (Trajectoies) list of trajectories corresponding to the points,
            render trajectories if provided (Default: None)
        weights: (list) list of weights associated with each point (Default: None)
        color_map: (str) name of matplotlib colormap to use for the heatmap (Default: 'viridis')
        tiles (str): name of map tiling to use (Default: 'cartodbdark_matter')
        attr (str): folium specific parameter (Default: '.')
        crs (str): folium specific parameter (Default: "EPSG3857")
        show (bool): whether or not to show the result (if possible)
            (default True) if saving to a file, might not want to view.
        save (bool): whether or not to save the result to a file.
            For folium the results can be saved to an html file. For
            cartopy the results can be saved as an image. If no filename
            is given, a default filename including the timestamp is used.
            (default False)
        filename (str): Path and filename to save the results to, if
            save is set to True. If no filename is given, a default
            filename including the timestamp is used.

    Returns: an interactive heatmap
    """

    # lat, long, (optional weight) of points to render
    if weights is None:
        display_points = [[point[1], point[0]] for point in points]
    else:
        display_points = [[point[1], point[0], weight] for point, weight in zip(points, weights)]

    # create the heat map
    heat_map = fol.Map(tiles=tiles, zoom_start=4)
    gradient = matplotlib_cmap_to_dict(color_map)
    if trajectories is not None:
        heat_map = render_trajectories(trajectories, map=heat_map, backend='folium',
                                       line_color='grey', linewidth=0.5,
                                       tiles=tiles, attr=attr, crs=crs)
    HeatMap(display_points, gradient=gradient).add_to(heat_map)
    if save:  # saves as .html document
        if not filename:
            datetime_str = datetime.now().strftime("%Y-%m-%dT%H%M%S-%f")
            filename = "heatmap-"+datetime_str+'.html'
        heat_map.save(filename)
    if show:
        display(heat_map)
    return heat_map
