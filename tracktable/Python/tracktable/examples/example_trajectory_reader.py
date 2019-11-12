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

# Purpose: Demonstrate how to create and use a Trajectory Reader    
# If you have a file of already formed trajectories, you can use the Trajectory 
# Reader to read them from file. Like the point reader, you can iterate over the 
# trajectories you have and access the properties of the points in each trajectory.

from tracktable.domain.terrestrial import TrajectoryReader

# The trajectory reader is set up in a similar way as a point reader. In the 
# example below, we give it a file containing trajectories and we use the default 
# which is the terrestrial point reader. Terrestrial is typically used on real data. 
# In order to access the trajectories, iterate over the reader.

inFile = open("data/SampleTrajectories.traj")
reader = TrajectoryReader()
reader.input = inFile
i = 1
for x in reader:                                 #Each object in the reader is an iterator pointer here
    print(*x)
    print("\n")
    i -= 1
    if i <= 0:
        break

# Note that by iterating over the reader, you get a collection of points together as 
# trajectories. Just like the point reader, you can edit the delimiting character and 
# comment character as well as the column properties.
