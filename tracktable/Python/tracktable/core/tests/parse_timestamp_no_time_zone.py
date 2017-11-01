#
# Copyright (c) 2017 National Technology and Engineering Solutions of
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

import pytz
import unittest

from datetime import datetime

from tracktable.core import Timestamp


class TestParseTimestamp(unittest.TestCase):

    def test_no_time_zone_non_iso(self):
        timestring = '2014-12-25 13:12:45'
        parsed_timestamp = Timestamp.from_string(timestring)
        constructed_timestamp = datetime(2014, 12, 25,
                                         hour=13, minute=12, second=45,
                                         tzinfo=pytz.utc)

        self.assertTrue(parsed_timestamp.tzinfo is not None)
        self.assertTrue(parsed_timestamp == constructed_timestamp)

    def test_no_time_zone_iso(self):
        timestring = '2014-12-25T13:12:45'
        parsed_timestamp = Timestamp.from_string(timestring)
        constructed_timestamp = datetime(2014, 12, 25,
                                         hour=13, minute=12, second=45,
                                         tzinfo=pytz.utc)

        self.assertTrue(parsed_timestamp.tzinfo is not None)
        self.assertTrue(parsed_timestamp == constructed_timestamp)


if __name__ == '__main__':
    unittest.main()
