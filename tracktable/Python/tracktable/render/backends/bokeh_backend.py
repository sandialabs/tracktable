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
tracktable.render.bokeh - render trajectories in using the bokeh backend
"""

from tracktable.render.map_processing import common_processing
from tracktable.render.map_decoration import coloring

def render_trajectories(trajectories,
                              map_canvas = None,
                              obj_ids = [],
                              line_color = '',
                              show_lines = True,
                              show_points = False,
                              gradient_hue = None,
                              color_map = '',
                              **kwargs):
    """Render a list of trajectories using the bokeh backend

        For documentation on the parameters, please see render_trajectories

        Currently not officially supported. Just for experimentation!
    """
    # Don't require dependencies unless using this backend
    from bokeh.io import output_notebook
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.plotting import figure, show
    from bokeh.tile_providers import Vendors, get_provider
    from pyproj import Proj, transform


    tile_provider = get_provider(Vendors.CARTODBPOSITRON)

    trajectories, line_color, color_map, gradient_hue = \
        common_processing.common_processing(trajectories, obj_ids, line_color,
                          color_map, gradient_hue)
    if not trajectories:
        return

    if common_processing.in_notebook():
        output_notebook()

    p = figure(x_axis_type="mercator", y_axis_type="mercator")
    p.add_tile(tile_provider)

    for trajectory in trajectories:
        data = {}
        data['x_values'] = []
        data['y_values'] = []
        data['timestamps'] = []
        for point in trajectory:
            wm_point = transform(Proj(init='epsg:4326'),
                                 Proj(init='epsg:3857'),
                                 point[0], point[1])
            data['x_values'].append(wm_point[0])
            data['y_values'].append(wm_point[1])
            fmt_str='%H:%M:%S'
            data['timestamps'].append(point.timestamp.strftime(fmt_str))
        source = ColumnDataSource(data=data)
        color = coloring.random_color()

        if show_lines:
            #could plot multilines instead? (may be faster?)
            line = p.line('x_values', 'y_values', source=source,
                          line_width=2, color=color)
            #may need to rework with multiple trajectories? TODO
            hover_tool = HoverTool(tooltips=trajectory[0].object_id,
                                   renderers=[line])
            p.tools.append(hover_tool)
        if show_points:
            points = p.circle(x='x_values', y='y_values', source=source,
                              size=3, color=color)
            #may need to rework with multiple trajectories? TODO
            hover_tool_point = HoverTool(tooltips='@timestamps',
                                         renderers=[points])
            p.tools.append(hover_tool_point)

    show(p)