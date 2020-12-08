#
# Copyright (c) 2017-2020 National Technology and Engineering
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
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function, division
import sys
import datetime

from tracktable.domain.terrestrial import TrajectoryPointReader

def read_and_get_timestamp(file, format) :
    all_points = []
    
    with open(file, 'rb') as infile:
        reader = TrajectoryPointReader()
        reader.input = infile
        reader.timestamp_format = format
        reader.timestamp_column = 1
        reader.field_delimiter = ","
        
        for point in reader:
            all_points.append(point)
            
        return all_points[3].timestamp  
        
def test_reader_timestamps(file_location):
    print("Attempting to read timestamps from files in {}.".format(file_location))
    error_count = 0

    expected_timestamp = datetime.datetime(2004, 12, 7, 11, 43, 18, 0, datetime.timezone.utc)
    
    actual_timestamp = read_and_get_timestamp(file_location + "PointsWithTimestamps1.csv", "%Y-%m-%d %H:%M:%S")
    
    if (actual_timestamp != expected_timestamp) :
        print("Error, actual timestamp {} does not match expected timestamp {}".format(actual_timestamp, expected_timestamp))
        error_count += 1
        
    actual_timestamp = read_and_get_timestamp(file_location + "PointsWithTimestamps2.csv", "%Y:%m:%d::%H:%M:%S")
    
    if (actual_timestamp != expected_timestamp) :
        print("Error, actual timestamp {} does not match expected timestamp {}".format(actual_timestamp, expected_timestamp))
        error_count += 1    
        
    actual_timestamp = read_and_get_timestamp(file_location + "PointsWithTimestamps3.csv", "%b %d %Y %H:%M:%S")
    
    if (actual_timestamp != expected_timestamp) :
        print("Error, actual timestamp {} does not match expected timestamp {}".format(actual_timestamp, expected_timestamp))
        error_count += 1    
        
    return error_count


def main():
    return test_reader_timestamps(sys.argv[1])

if __name__ == '__main__':
    sys.exit(main())

