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

# Purpose: Demonstrate how to create and use a terrestrial point reader.    
# The basic object in tracktable is the point reader. This data structure reads 
# tabular data from a file and saves it as points containing, at the least, an 
# object id, timestamp, longitude, and latitude.    

# Imports
from tracktable.domain.terrestrial import TrajectoryPointReader
from tracktable.core import data_directory

import os.path

# To create a point, we create a generic TrajectoryPointReader object and give it the following:    
#   input file - File stream connected to a data file    
#   delimiter - The character separating fields in the fileie, a csv will have ',' as a delimiter)    
#   comment character - The character marking comments in the file and will be ignored by the point reader    

#   Note: The domain will default to terrestrial, which is what we typically use for real data.

inFile = open(os.path.join(data_directory(), 'SampleASDI.csv'), 'r')
reader = TrajectoryPointReader()
reader.input = inFile
reader.comment_character = '#'
reader.field_delimiter = ','

# In order to view the points the reader has read, we iterate over the reader.    
# Note: Data is not actually read from file until accessed. This means that even 
# though we have configured the reader, the reader is not finished with the input 
# file until the points have been read below.    

i = 10              # Used to limit how many results we see
for x in reader:    # Only need this line and the next to see all the data
    print(x)
    i-=1
    if i <=0:
        break
inFile.close()


# So what happens in the background?    
# The reader has several attributes that can be set. Some of these attributes are:    
#     object_id_column - Column in dataset holding the object id    
#     timestamp_column - Column in dataset holding the timestamp    
#     coordinate0 - Column in dataset holding the longitude    
#     coordinate1 - Column in dataset holding the latitude    
#     
# These four columns are required. 
#     
# Note: Coordinates are referenced like a list and there are three, coordinates[0], coordinates[1], 
# and coordinates[2] representing longitude, latitude, and z-order respectively.    
#
# In addition to these attributes, custom columns can be set such as 'altitude', 'speed', 'airline', 
# etc so long as it is numeric, timestamp, or string. Any columns not given values will be assigned the default, or 'None'.     
#     
# In the next example, we set a numeric field (speed) and a string field(status) and see the results.    


inFile = open('data/SampleASDI.csv', 'r')
reader.input = inFile
reader.object_id_column = 0
reader.timestamp_column = 1
reader.coordinates[0] = 2
reader.coordinates[1] = 3
reader.set_real_field_column('speed', 4)     # The column name is 'speed' and it is located in column 4
reader.set_string_field_column('status', 9)

i=10
for x in reader:
    print(x)
    i-=1
    if i <= 0:
        break

