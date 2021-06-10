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

import logging

from tracktable.core.geomath import simplify
from tracktable.render.backends import cartopy_backend, folium_backend
from tracktable.render.map_processing import common_processing

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------

def render_heatmaps(points, backend='', trajectories=None, simplify_traj=False, simplify_tol=0.0001, **kwargs):
    render_function = folium_backend.render_heatmaps

    if backend == 'folium':
        render_function = folium_backend.render_heatmaps
    elif backend == 'cartopy':
        render_function = cartopy_backend.render_heatmaps
    elif backend == 'ipyleaflet': # currently not implemented
        raise NotImplementedError("ipyleaflet rendering backend for heatmaps is currently unavailable.")
    elif backend == 'bokeh':  # currently not implemented
        raise NotImplementedError("Bokeh rendering backend for heatmaps is currently unavailable.")
    else:
        if backend != '':
            logger.error("Error: Invalid backend specified in",
                  "render_heatmaps.",
                  "Valid backends include: folium, and cartopy")
        if common_processing.in_notebook():
            if type(trajectories) is not list or len(trajectories) <= 10000:
                render_function = folium_backend.render_heatmaps
            else:
                logger.warn("Too many trajectories to plot with folium. Reverting to non-interactive backend. Override with backend='folium'")
                render_function = cartopy_backend.render_heatmaps
        else:
            render_function = cartopy_backend.render_heatmaps

    if simplify_traj:
        if type(trajectories) is not list:
            trajectories = simplify(trajectories, simplify_tol)
        else:
            for index, traj in enumerate(trajectories):
                trajectories[index] = simplify(traj, simplify_tol)

    return render_function(trajectories, **kwargs)
