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
of heatmaps. A user should be able to simply use the function
render_heatmap(points) passing a single parameter that is a list
of points and get a rendering of those points, whether
running as an interactive map inside of a notebook or from the command
line and saved as a static image to a file.
"""

import logging

from tracktable.core.geomath import simplify
from tracktable.render.backends import cartopy_backend, folium_backend
from tracktable.render.map_processing import common_processing

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------

def render_heatmap(points, backend='', trajectories=None, **kwargs):
    """Render a list of trajectories interactively or as a static image

    This function will render a list of trajectories using Folium (for
    interactive display) if you are in a Jupyter notebook or using Cartopy
    (for a static image) if you are running from a script.

    Args:
        points (single points or list of points):
            Points to render

    Keyword Arguments:
        backend (str): Which back end to use.  This can be 'folium' to force
            Folium interactive rendering or 'cartopy' to force static images.
            Defaults to None, which lets the renderer select automatically.
        trajectories (Trajectory): list of trajectories corresponding to the points,
            render trajectories if provided. (Default: None)
        simplify_traj (bool): Simplify trajectories prior to rendering them
        simplify_tol (float): Tolerance to use when simplifying trajectories,
            default is 0.0001
        weights: (list) list of weights associated with each point (Default: None)
        color_map: (str) name of matplotlib colormap to use for the heatmap (Default: 'viridis')
        tiles (str): name of map tiling to use (Default: 'cartodbdark_matter')
        attr (str): folium specific parameter (Default: '.')
        crs (str): folium specific parameter (Default: "EPSG3857")
        show (bool): whether or not to show the result (if possible)
            (default: True) if saving to a file, might not want to view.
        save (bool): whether or not to save the result to a file.
            For folium the results can be saved to an html file. For
            cartopy the results can be saved as an image. If no filename
            is given, a default filename including the timestamp is used.
            (default: False)
        filename (str): Path and filename to save the results to, if
            save is set to True. If no filename is given, a default
            filename including the timestamp is used.
        map_projection (GeoAxes): Map to render onto
        point_source (iterable): Sequence of 2D points. This will
          be traversed only once.
        bounding_box (point2d): Bounding box of area to generate histogram
        bin_size (int): Boundary size for bins (Default: 1)
        colormap (str or Colormap): Colors to use for histogram (Default: 'gist_heat')
        colorscale (matplotlib.colors.Normalize or subclass): Mapping from bin counts to color. Useful values are matplotlib.colors.Normalize() and matplotlib.colors.LogNorm(). (Default: matplotlib.colors.Normalize())
        zorder (int): Image priority for rendering. Higher values will be rendered on top of actors with lower z-order. (Default: 10)

    """

    render_function = folium_backend.render_heatmap

    if backend == 'folium':
        render_function = folium_backend.render_heatmap
    elif backend == 'cartopy':
        render_function = cartopy_backend.render_heatmap
    elif backend == 'ipyleaflet': # currently not implemented
        raise NotImplementedError("ipyleaflet heatmap rendering backend is currently unavailable.")
    elif backend == 'bokeh':  # currently not implemented
        raise NotImplementedError("Bokeh heatmap rendering backend is currently unavailable.")
    else:
        if backend != '':
            logger.error("Error: Invalid backend specified in",
                  "render_heatmap.",
                  "Valid backends include: folium, and cartopy.",
                  "Defauting to folium backend")
        if common_processing.in_notebook():
            if type(trajectories) is not list or len(trajectories) <= 10000:
                render_function = folium_backend.render_heatmap
            else:
                logger.warn("Too many trajectories to plot with folium. Reverting to non-interactive backend. Override with backend='folium'")
                render_function = cartopy_backend.render_heatmap
        else:
            render_function = cartopy_backend.render_heatmap

    return render_function(points, **kwargs)
