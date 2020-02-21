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

# Purpose: Sample code to assemble points into trajectories    
# When you read in points from a file, you need to build those points into 
# trajectories. As we know, data can be noisy, therefore we want to filter our 
# trajectories to have a minimum number of points and/or a certain time or 
# distance between points in a trajectory. The trajectory builder does all of this. 

# Imports
from tracktable.domain.terrestrial import TrajectoryPointReader        # Read points from file
from tracktable.source.trajectory import AssembleTrajectoryFromPoints  # Turn points into trajectories
from tracktable.core import data_directory

import os.path

# Requirements: In order to use the trajectory builder, we need a source that gives 
# us data points in time sequential order. As with before, we can use the Point Reader.

inFile = open(os.path.join(data_directory(), 'SampleFlightsUS.csv'), 'r')
reader = TrajectoryPointReader()
reader.input = inFile
reader.comment_character = '#'
reader.field_delimiter = ','
# Set columns for data we care about
reader.object_id_column = 0
reader.timestamp_column = 1
reader.coordinates[0] = 2
reader.coordinates[1] = 3
reader.set_real_field_column('Heading', 5)  # Picked arbitrary data column for example purposes


# Now that we have our points ready to be read, we need to create a builder to 
# take those points and form trajectories.    
# For now, we are going to leave the parameters at default. 

builder = AssembleTrajectoryFromPoints()
builder.input = reader
builder.minumum_length = 3                  # An example of how to set the minimum number of points for each trajectory. Default is 2.


# That's it! Now we can play with the trajectories. As before with the point 
# reader by itself, no data is loaded until you interact with the data.         
# Let's start with seeing how many trajectories we have. We can do this, and 
# see what they look like by dumping the trajectories to a list.  

traj = list(builder.trajectories())
print(len(traj))

# Looking at our first trajectory, we can see all the points included. See how 
# they are in time sequential order and share the same object_id, which is what 
# we would expect from a trajectory. 

print(*traj[0])

# Here is an example of how to access specific information within a trajectory. We show how to get:    
#  1. Core data such as object_id    
#  2. Longitude and Latitude    
#  3. Custom columns such as 'Heading'    

print('Object_id: ' + traj[0][0].object_id)                     # Trajectory 0 in list, point 0 in trajectory
print('Latitude: ' + str(traj[0][0][1]))                        # Trajectory 0 in list, point 0 in trajectory, coordinate[1]
print('Heading: ' + str(traj[0][0].properties['Heading']))      

inFile.close()

# The builder has multiple parameters that can be changed. For example, we can    
#  1. Change the minimum number of points needed to form a trajectory. (builder.minimum_length = 10)    
#  2. Change the minimum distance between points. (builder.separation_stance = 100)    
#  3. Change the minimum time between points. (builder.separation_time = datetime.timedelta(minutes=30))    
