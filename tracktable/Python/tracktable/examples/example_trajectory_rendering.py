# Example: Rendering a trajectory map
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
#    1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#     
#    2. Redistributions in binary form must reproduce the above copyright
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

# Purpose: Sample code to render assembled trajectories     
# In some cases, you may wish to read in trajectories with certain constraints. 
# For example, we can have trajectories with a minimum number of points. Or 
# we acknowledge that the points in the trajectory should be within a certain 
# time and/or distance threshold to belong to the same trajectory. The Trajectory 
# Builder does this.

# Imports
import matplotlib
from tracktable.examples.example_trajectory_rendering import render_trajectories
from tracktable.domain import terrestrial
from tracktable.render import mapmaker
from matplotlib import pyplot


# Requirements: We will need data points built into trajectories. 
inFile = open('../data/SampleTrajectories.traj', 'r')
trajectories = terrestrial.TrajectoryReader()
trajectories.input = inFile

# Set up the canvas and map projection
dpi = 160
(mymap, map_actors) = mapmaker.mapmaker(domain='terrestrial',
                                        map_name='region:conus')

color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1)
render_trajectories(mymap, trajectories, trajectory_linewidth=2)


# It is possible the scale of the selected map is not appropriate for the trajectories you wish 
# to render. The rendered example map is of the continental United States or CONUS. This is one 
# of the preset convenience maps and was set as the map name when we called the render function. 
# Other convenience maps are europe, north_america, south_america, australia and world.  
# 
# Let us expand our view using another custom map.
inFile = open('../data/SampleTrajectories.traj', 'r')
trajectories = terrestrial.TrajectoryReader()
trajectories.input = inFile

# Set up the canvas and map projection
dpi = 160
(mymap, map_actors) = mapmaker.mapmaker(domain='terrestrial',
                                        map_name='region:world')

color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1)
render_trajectories(mymap, trajectories, trajectory_linewidth=2)