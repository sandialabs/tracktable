# # Example: Rendering a heat map
# 

# Copyright (c) 2014-2019 National Technology and Engineering
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
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Purpose: Sample code to render heatmap of points

# Imports
from tracktable.domain.terrestrial import TrajectoryPointReader
from tracktable.render import mapmaker
from tracktable.examples import heatmap_from_points as heatmap


# First we set up our point source by reading points from a file. Then we dump the points to a list.    
# We do not care about extra data in this example, so we leave all the column fields as default.
points = []
with open('data/SampleHeatmapPoints.csv', 'r') as inFile:
    reader = TrajectoryPointReader()
    reader.input = inFile
    reader.comment_character = '#'
    reader.field_delimiter = ','
    for point in reader:
        points.append(point)


# Now we generate a map and create a heatmap from the points we generated.
# Set up the canvas and map projection
(mymap, map_actors) = mapmaker.mapmaker(domain='terrestrial',
                                        map_name='region:world')

heatmap.render_histogram(mymap, 
                         domain = 'terrestrial',
                         point_source=points,       # Our list of points we created above
                         bounding_box = None,       # Bounding box is generated from mymap
                         bin_size=0.25, 
                         color_map='gist_heat')

