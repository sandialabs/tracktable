#
# Copyright (c) 2014-2017 National Technology and Engineering
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
simple_timezone - Timezone struct based on UTC offset
"""

from datetime import tzinfo, timedelta, datetime

ZERO = timedelta(0)
ONE_HOUR = timedelta(hours=1)

class SimpleTimeZone(tzinfo):
    """Trivial time zone struct for use with datetime.

    We use this when we don't need the full power of the pytz package.

    Attributes:
      offset (datetime.timedelta): Offset from UTC
      name (string): Human-readable name for timezone
    """

    def __init__(self, hours=0, minutes=0, name='UTC'):
        """Initialize a timezone to UTC.

        Args:
           hours (integer): Hours away from UTC (default 0)
           minutes (integer): Minutes to add to the hours (default 0)
           name (string): Human-readable name for time zone (default 'UTC')
        """

        self.offset = timedelta(hours=hours, minutes=minutes)
        self.name = name

    def __repr__(self):
        """Return machine-parseable representation of time zone"""
        return '<SimpleTimeZone: {}, offset {}>'.format(self._name, self._offset)

    def utcoffset(self, dt):
        """Return offset from UTC

        This method is required by the Python datetime library in
        order to create 'aware' datetime objects.

        Args:
          dt (datetime.timedelta): Not used
        """
        return timedelta(minutes=self.offset.total_seconds() / 60)

    def localize(self, timestamp):
        """Convert a datetime into an 'aware' datetime object by replacing its time zone

        Args:
          timestamp (datetime.datetime): Timestamp object to make aware

        Returns:
          New datetime.datetime object with this timezone attached
        """
        return timestamp.replace(tzinfo=self)

    def dst(self, dt):
        """Return daylight savings time offset

        Since we don't support daylight savings time in SimpleTimeZone this is always zero.

        Args:
          dt (datetime.datetime): Timestamp to check for DST

        Returns:
          Zero time offset
        """
        return ZERO
