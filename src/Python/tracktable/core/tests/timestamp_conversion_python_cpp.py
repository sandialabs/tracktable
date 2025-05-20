#
# Copyright (c) 2021 National Technology and Engineering Solutions of
# Sandia, LLC. Under the terms of Contract DE-NA0003525 with National
# Technology and Engineering Solutions of Sandia, LLC, the
# U.S. Government retains certain rights in this software.
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
#

# Purpose: Make sure that time zones on timestamps going into 
# TrajectoryPoints get accounted for properly.
#
# Explanation:
#
# Our Python wrappers have code to convert between Python 
# datetime.datetime objects and C++ boost::posix_time::ptime objects.
# Since boost::posix_time doesn't support time zones, we made the 
# decision to store timestamps internally in UTC all the time.
#
# We found a bug where timezones other than UTC on the Python timestamps
# were not getting accounted for properly during the conversion from
# Python to C++.  The ptime object in C++ would have the local time
# from the datetime object rather than being properly shifted into
# UTC.
#
# This test verifies that we are in fact using the time zone in the
# conversion.

import pytz
import unittest

from datetime import datetime
import pytz

from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint


class TestTimestampTimeZoneConversion(unittest.TestCase):
    def test_same_time_after_conversion(self):
        eastern = pytz.timezone('US/Eastern')

        naive_timestamp = datetime(
            2015, 10, 21, 14, 0, 0)
        timestamp_in_us_eastern = eastern.localize(naive_timestamp)

        my_point = TerrestrialTrajectoryPoint()
        my_point.object_id = 'testing'
        my_point[0] = 10
        my_point[1] = 20
        my_point.timestamp = timestamp_in_us_eastern

        # We do NOT expect this to be exactly the same as the value
        # of timestamp_in_us_eastern because of the conversion
        # described above.
        converted_timestamp = my_point.timestamp

        print("DEBUG: Original timestamp is {} and converted timestamp is {}".format(
            timestamp_in_us_eastern.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
            converted_timestamp.strftime('%Y-%m-%d %H:%M:%S %Z%z')))

        self.assertTrue(converted_timestamp == timestamp_in_us_eastern)

if __name__ == '__main__':
    unittest.main()
