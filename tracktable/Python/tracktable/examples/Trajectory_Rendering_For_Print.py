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
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

"""
Trajectory Readering For Print Example

Purpose: Demonstrate plotting trajectory figures for use in printed media / papers.
"""

import os.path
from datetime import timedelta

import cartopy
import cartopy.crs
from tracktable.analysis.assemble_trajectories import \
    AssembleTrajectoryFromPoints
#from tracktable.analysis.dbscan import compute_cluster_labels
from tracktable.core import data_directory
from tracktable.domain.terrestrial import TrajectoryPointReader
from tracktable.render.render_trajectories import (
    render_trajectories_for_print, render_trajectories_for_print_using_tiles)

data_filename = os.path.join(data_directory(), 'SampleFlightsUS.csv')
inFile = open(data_filename, 'r')
reader = TrajectoryPointReader()
reader.input = inFile
reader.comment_character = '#'
reader.field_delimiter = ','
reader.object_id_column = 0
reader.timestamp_column = 1
reader.coordinates[0] = 2
reader.coordinates[1] = 3

builder = AssembleTrajectoryFromPoints()
builder.input = reader
builder.minimum_length = 5
builder.separation_time = timedelta(minutes=10)

all_trajectories = list(builder)

# Default behavior:
# Give it a list of trajectories and a filename.  Extension can be png, pdf, etc and it will output in correct format.
render_trajectories_for_print(all_trajectories[0], "myfig0.pdf")

#can change colormap to any supported by matplotlib.  We recommend default (viridis) or this one (cividis)
render_trajectories_for_print(all_trajectories[0], "myfig0.png", color_map='cividis')

#Depending on your track(s) you may need to adjust linewidth until it's wide enough to see well, but not too thick.
render_trajectories_for_print(all_trajectories[1], "myfig1.pdf", linewidth=1.5)

# There are multiple boarders (state and coastlines) that converge at the seashore.  You may want to turn off coastlines
render_trajectories_for_print(all_trajectories[4], "myfig4.pdf", draw_coastlines=False)
#other things you can tweak:
#                     draw_countries=True,
#                     draw_states=True,
#                     fill_land=True,
#                     fill_water=True,
#                     land_fill_color='#101010',
#                     water_fill_color='#000000',
#                     land_zorder=4,
#                     water_zorder=4,
#                     lonlat_spacing=10,
#                     lonlat_color='#A0A0A0',
#                     lonlat_linewidth=0.2,
#                     lonlat_zorder=6,
#                     coastline_color='#808080',
#                     coastline_linewidth=1,
#                     coastline_zorder=5,
#                     country_color='#606060',
#                     country_fill_color='#303030',
#                     country_linewidth=0.5,
#                     country_zorder=3,
#                     state_color='#404040',
#                     state_fill_color='none',
#                     state_linewidth=0.3,
#                     state_zorder=2,
#                     draw_largest_cities=None,
#                     draw_cities_larger_than=None,
#                     city_label_size=12,
#                     city_dot_size=2,
#                     city_dot_color='white',
#                     city_label_color='white',
#                     city_zorder=6,
#                     country_resolution='10m',
#                     state_resolution='10m',
#                     coastline_resolution='50m',
#                     land_resolution='110m',
#                     ocean_resolution='110m',
#                     lake_resolution='110m',
#                     map_bbox=None,
#                     map_projection=None,
#                     map_scale_length=None,
#                     region_size=None

#can turn off Lat/Lon lines
render_trajectories_for_print(all_trajectories[11], "myfig11.pdf", linewidth=1.4, draw_lonlat=False)

#You can set the size of the figure in inches (width,height) dpi defaults to 300
#unfortunately in this case the map will remain skinny, while the figure will be wide with lots of
#whitespace on both sides. (you may need to look at the output pdf to see the whitespace.)
render_trajectories_for_print(all_trajectories[13], "myfig13a.pdf", linewidth=.9, figsize=(3,2), draw_coastlines=False)

#To fix that extra whitespace (unless you manually crop) you can either adjust the figsize (see pdfs for comparison)
render_trajectories_for_print(all_trajectories[13], "myfig13b.pdf", linewidth=.9, figsize=(1,2), draw_coastlines=False)

#Or, add extra "bounding box buffer" (width, height) to the map such that more map is shown.  (we hope to automate this at some point)
render_trajectories_for_print(all_trajectories[13], "myfig13c.pdf", linewidth=.9, figsize=(3,2), bbox_buffer=(2.7,.1), draw_coastlines=False)

#If you wish to show multiple trajectories with different coloring here are some options:  Multiple color_maps (_r reverses the map)
render_trajectories_for_print(all_trajectories[14:16], "myfig14a.pdf", color_map=['viridis','YlOrRd_r'], linewidth=1.2)

#you may specify the hue for a gradient (dark -> light) using a number (0-1) or a color name or a #RRGGBB color specification (see render_trajectories() for mor info)
render_trajectories_for_print(all_trajectories[14:16], "myfig14b.pdf", gradient_hue=['blue',.3], linewidth=1.2)

#you may specify a solid color for the lines
render_trajectories_for_print(all_trajectories[14:16], "myfig14c.pdf", line_color=['blue','red'], linewidth=1.2)

# You can specify a specific bounding box.  In this case entire world.
render_trajectories_for_print(all_trajectories[15:25], "myfig15a.pdf", map_bbox=[-180,-90,180,90], linewidth=.3, coastline_linewidth=.15, draw_countries=False, draw_states=False, dot_size=.05)

#You can specify a projection (LambertCylindrical)
# See options here: https://scitools.org.uk/cartopy/docs/latest/crs/projections.html
render_trajectories_for_print(all_trajectories[15:25], "myfig15b.pdf", map_projection=cartopy.crs.LambertCylindrical, map_bbox=[-180,-90,180,90], linewidth=.3, coastline_linewidth=.15, draw_countries=False, draw_states=False, dot_size=.05)

#if using a "global" projection and you want to see all of it, set map_global=True to use the limites of the projection
render_trajectories_for_print(all_trajectories[15:25], "myfig15c.pdf", map_global=True, map_projection=cartopy.crs.Robinson, linewidth=.3, coastline_linewidth=.15, draw_countries=False, draw_states=False, dot_size=.05)

# You can add labels for lon/lat, only with certain projections.
# Only PlateCarree and Mercator plots currently support drawing labels for lon/lats.
#Recommended projection (Miller) does not support automatically drawing labels.
render_trajectories_for_print(all_trajectories[17], "myfig17.pdf", lonlat_labels=True, map_projection=cartopy.crs.Mercator)

# The border resolution can be adjusted. (Low res)
#110m = low res, 50m = med res, 10m high res
render_trajectories_for_print(all_trajectories[25], "myfig25a.pdf", linewidth=1.2, border_resolution='110m')

# The border resolution can be adjusted. (High res)
render_trajectories_for_print(all_trajectories[25], "myfig25b.pdf", linewidth=1.2, border_resolution='10m')

#using this method you can use map tiles instead of Cartopy geometry.
render_trajectories_for_print_using_tiles(all_trajectories[25], "myfig25c.pdf", linewidth=1.2)

# You can change the zoom level
render_trajectories_for_print_using_tiles(all_trajectories[25], "myfig25d.pdf", linewidth=1.2, tiles_zoom_level=2)

# And should adjust the zoom level until the label font is correclty sized.
render_trajectories_for_print_using_tiles(all_trajectories[25], "myfig25e.pdf", linewidth=1.2, tiles_zoom_level=7)
