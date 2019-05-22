# Copyright (c) 2014, Sandia Corporation.  All rights
# reserved.
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
Utility classes for position update data
"""
from __future__ import print_function

import copy
import datetime
import math
import re
import sys
import time

from .simple_timezone import SimpleTimeZone

try:
    import pytz
    PYTZ_AVAILABLE = True
    DEFAULT_TIMEZONE = pytz.utc
except ImportError:
    PYTZ_AVAILABLE = False
    DEFAULT_TIMEZONE = SimpleTimeZone(hours=0)

from .core_types import set_default_timezone

set_default_timezone(DEFAULT_TIMEZONE)

# ----------------------------------------------------------------------

def localize_timestamp(naive_ts, utc_offset=0):
    """Imbue a naive timestamp with a timezone

    Python has two kinds of timestamps: naive (just a datetime, no
    time zone) and aware (time plus time zone).  Mixing the two is
    awkward.  Thie routine will assign a time zone to a datetime (UTC
    by default) for consistency throughout Tracktable.

    Note: You can change the default timezone by setting the
    module-level variable DEFAULT_TIMEZONE.  This is not recommended.

    Args:
      naive_ts (datetime): Timestamp to localize
      utc_offset (integer): Number of hours offset from UTC.  You can also specify a fraction of an hour as '0530', meaning 5 hours 30 minutes.

    Returns:
      A new datetime imbued with the desired time zone

    """

    absolute_offset = abs(utc_offset)
    if absolute_offset > 100:
        hours = int(absolute_offset / 100)
        minutes = absolute_offset % 100
    else:
        hours = absolute_offset
        minutes = 0

    if utc_offset >= 0:
        utc_time = naive_ts - datetime.timedelta(hours=hours, minutes=minutes)
    else:
        utc_time = naive_ts + datetime.timedelta(hours=hours, minutes=minutes)

    return DEFAULT_TIMEZONE.localize(utc_time)

# ----------------------------------------------------------------------

class Timestamp(object):
    """Convenience class that can convert from different formats to an 'aware' datetime
    """

    """No timestamp should ever be before this."""
    BEGINNING_OF_TIME = datetime.datetime(1400, 1, 1)

    @staticmethod
    def beginning_of_time():
        """Return a timestamp guaranteed to be before any legal data point

        Returns:
           Timestamp equal to January 1, 1400.
        """
        return datetime.datetime(1400, 1, 1)

    @staticmethod
    def sanity_check(timestamp):
        """Check to see whether a timestamp might be real

        We assume that any timestamp after the year 1600 has a
        non-zero chance of being real and that anything before that is
        bogus.

        Args:
          timestamp (datetime): Timestamp to check

        Returns:
           Timestamp argument if sane, None if not
        """

        if timestamp.year > 1600:
            return timestamp
        else:
            return None

    @staticmethod
    def from_string(timestring, format_string=None):
        """Convert from a string to a datetime

        Populate from a string such as '2012-09-10 12:34:56' or
        '2012-09-10T12:34:56'.  Note that you *must* have both a date
        and a time in that format or else the method will fail.

        You can use a different format if you like but you will have
        to supply the 'format_string' argument.  It will be passed to
        datetime.strptime.  In Python 3 you can use the '%z' directive
        to parse a time zone declaration -- for example, '2017-06-01
        12:34:56-0500' is June 5, 2017 in UTC-5, aka the US east coast.

        Note: Python 2.7 does not have the %z directive.  You must use
        Python 3.4 or newer to get that.

        Args:
          timestring (string): String containing your timestamp

        Kwargs:
          format_string (string): Format string for datetime.strptime

        Returns:
          An aware datetime object.  By default this will be imbued
          with tracktable.core.timestamp.DEFAULT_TIMEZONE.  If you
          used a format string with %z or %Z then you will get
          whatever time zone Python parsed.
        """

        if timestring:
            if format_string is None:
                if timestring[10] == 'T':
                    format_string = '%Y-%m-%dT%H:%M:%S'
                else:
                    format_string = '%Y-%m-%d %H:%M:%S'

            parsed_time = datetime.datetime.strptime(timestring, format_string)

            if parsed_time.tzinfo is not None:
                return parsed_time
            else:
                return DEFAULT_TIMEZONE.localize(parsed_time)
        else:
            return Timestamp.beginning_of_time()

    @staticmethod
    def from_struct_time(mytime):
        """Construct a datetime from a time.struct_time object.

        Args:
          mytime (time.struct_time): Source time

        Returns:
          An aware datetime object imbued with tracktable.core.timestamp.DEFAULT_TIMEZONE.
        """
        return DEFAULT_TIMEZONE.localize(datetime.datetime.fromtimestamp(time.mktime(mytime)))


    @staticmethod
    def from_dict(mydict):
        """Construct a datetime from a dict with named elements.

        Args:
          mydict (dict): Dict with zero or more of 'hour',
            'minute', 'second', 'year', 'month', 'day', and 'utc_offset'
            entries.  Missing entries will be set to their minimum legal values.


        Returns:
          An aware datetime object imbued with tracktable.core.DEFAULT_TIMEZONE
            unless a 'utc_offset' value is specified, in which case the specified
            time zone will be used instead.
        """

        timestamp = datetime.datetime.now()
        timestamp.year=mydict.get('year', datetime.MINYEAR)
        timestamp.month=mydict.get('month', 1)
        timestamp.day=mydict.get('day', 1)
        timestamp.hour=mydict.get('hour', 0)
        timestamp.minute=mydict.get('minute', 0)
        timestamp.second=mydict.get('second', 0)

        if 'utc_offset' in mydict:
            return localize_timestamp(timestamp, mydict['utc_offset'])
        else:
            return DEFAULT_TIMEZONE.localize(timestamp)


    @staticmethod
    def from_any(thing):
        """Try to construct a timestamp from whatever we're given.

        The possible inputs can be:

        - a Python datetime (in which case we just return a copy of the input)

        - a string in the format '2013-04-05 11:23:45', in which case
          we will assume that it resides in timestamp.DEFAULT_TIMEZONE

        - a string in the format '2013-04-05 11:23:45-05', in which case we will
          assume that it's UTC-5 (or other time zone, accordingly)

        - a string in the format '2013-04-05T11:23:45' or
          '2013-04-05T11:23:45-05' -- just like above but with a T in
          the middle instead of a space

        - a string in the format '20130405112345' - these are assumed
          to reside in timestamp.DEFAULT_TIMEZONE

        - a string in the format 'MM-DD-YYYY HH:MM:SS'

        - a string such as '08-Aug-2013 12:34:45' where 'Aug' is the
          abbreviated name for a month in your local environment

        - a dict containing at least 'year', 'month', 'day' entries
          and optionally 'hour', 'minute' and 'second' - these will
          always represent UTC times until I implement it otherwise

        Args:
          thing: String, datetime, or dict (see above)

        Returns:
          Timezone-aware datetime object
        """

        # If it's a datetime then we might need to assign a timezone.  That's all.
        if type(thing) == datetime.datetime:
            if thing.tzinfo is None:
                return localize_timestamp(thing, 0)
            else:
                return copy.copy(thing)

        # If it's a string, try to detect a timezone at the end and
        # then try to parse the rest of it with a whole slew of format
        # strings.  Here we define 'string' as types str and unicode.

        elif type(thing) == str or type(thing) == unicode:
            try:
                (timestamp, utc_offset) = _fastparse(thing)
                return localize_timestamp(timestamp, utc_offset)

            except (ValueError, TypeError):
                match = re.search(r'([+-]\d{1,2})(00|)$', thing)
                if match:
                    match_length = len(match.group(0))
                    string_without_tz = thing[0:-match_length]
                    utc_offset = int(match.group(1))
                else:
                    string_without_tz = thing
                    utc_offset = 0

                format_strings = [ '%Y-%m-%d %H:%M:%S',
                                   '%Y-%m-%dT%H:%M:%S',
                                   '%Y-%b-%d %H:%M:%S',
                                   '%m-%d-%Y %H:%M:%S',
                                   '%Y%m%d%H%M%S' ]
                for format_str in format_strings:
                    try:
                        dt = datetime.datetime.strptime(string_without_tz, format_str)
                        return localize_timestamp(dt, utc_offset)
                    except:
                        continue

        elif type(thing) == dict:
            return Timestamp.from_dict(thing)

        else:
            raise ValueError('ERROR: Thing (%s) is not any kind of timestamp I understand.' % thing)


    @staticmethod
    def from_datetime(mytime):
        """Convert a datetime to an aware timestamp

        Args:
           mytime (datetime): Possibly-naive timestamp

        Returns:
           New datetime that will definitely have a time zone attached
        """

        if mytime:
            if not mytime.tzinfo:
                return DEFAULT_TIMEZONE.localize(mytime)
            else:
                return mytime
        else:
            return None

    @staticmethod
    def to_string(dt, format_string='%Y-%m-%d %H:%M:%S', include_tz=True):
        """Convert a datetime to a string

        Format contents as a string, by default formatted as
        '2013-04-21 14:45:00'.  You may supply an argument
        'format_string' if you want it in a different form.  See the
        documentation for datetime.strftime() for information on what
        this format string looks like.

        Args:
          dt (datetime): Timestamp object to stringify
          format_string (string): String to pass to datetime.strftime()
            that describes format
          include_tz: Whether or not to append timezone UTC offset

        Returns:
          String version of timestamp
        """

        just_the_time = dt.strftime(format_string)
        if include_tz:
            offset_in_minutes = dt.utcoffset().seconds / 60
            absolute_offset = abs(offset_in_minutes)
            hours = absolute_offset / 60
            minutes = absolute_offset % 30
            if offset_in_minutes > 0:
                return '%s+%02d%02d' % ( just_the_time, hours, minutes )
            else:
                return '%s-%02d%02d' % ( just_the_time, hours, minutes )
        else:
            return just_the_time

    @staticmethod
    def to_iso_string(dt, include_tz=True):
        """Convert a timestamp to a string in format YYYY-MM-DDTHH:MM:SS

        Args:
          dt (datetime): Timezone-aware datetime object
          include_tz (boolean): Whether or not to append a '+XXXX' timezone offset

        Returns:
          String representation of the timestamp
        """
        return Timestamp.to_string(dt, format_string='%Y-%m-%dT%H:%M:%S', include_tz=include_tz)

    @staticmethod
    def truncate_to_minute(orig_dt):
        """Zero out the seconds in a timestamp

        Args:
           orig_dt (datetime): Input datetime

        Returns:
           New timestamp with seconds=0
        """

        new_dt = Timestamp.from_any(datetime.datetime(
            year=orig_dt.year,
            month=orig_dt.month,
            day=orig_dt.day,
            hour=orig_dt.hour,
            minute=orig_dt.minute))
        return new_dt

    @staticmethod
    def truncate_to_hour(orig_dt):
        """Zero out the minutes and seconds in a timestamp

        Args:
           orig_dt (datetime): Input datetime

        Returns:
           New timestamp with minutes=0 and seconds=0
        """

        new_dt = Timestamp.from_any(datetime.datetime(
            year=orig_dt.year,
            month=orig_dt.month,
            day=orig_dt.day,
            hour=orig_dt.hour))
        return new_dt

    @staticmethod
    def truncate_to_day(orig_dt):
        """Zero out the time portion of a timestamp

        Args:
           orig_dt (datetime): Input datetime

        Returns:
           New timestamp with hours=0, minutes=0 and seconds=0
        """
        new_dt = Timestamp.from_any(datetime.datetime(
            year=orig_dt.year,
            month=orig_dt.month,
            day=orig_dt.day))
        return new_dt

    @staticmethod
    def truncate_to_year(orig_dt):
        """Zero out all but the year in a timestamp

        Args:
           orig_dt (datetime): Input datetime

        Returns:
           New timestamp with month=1, day=1, hours=0, minutes=0 and seconds=0
        """
        new_dt = Timestamp.from_any(datetime.datetime(
            year=orig_dt.year,
            month=1,
            day=1))
        return new_dt


# ----------------------------------------------------------------------

def _fastparse(text):
    """INTERNAL METHOD

    Because of the string processing we have to do, methods like
    strptime are relatively slow.  We can go a lot faster if we
    know exactly which characters in a substring correspond
    to different parts of a timestamp.  This method is for that
    case.

    We assume that the timestamp is in the format 'YYYY-MM-DD
    HH:MM:SS' with an optional addendum of '+XX' or '-XX' for
    a UTC offset.

    We deliberately don't trap any exceptions here.  If anything
    goes wrong, the caller will find out about it and fall back
    to a slower but more robust method.

    Args:
      text (string): String representation of timestamp

    Returns:
      Timezone-aware datetime object
    """

    textlen = len(text)

    # YYYY-MM-DD HH:MM:SS
    # 0123456789012345678

    if len(text) == 19:
        year = int(text[0:4])
        month = int(text[5:7])
        day = int(text[8:10])
        hour = int(text[11:13])
        minute = int(text[14:16])
        second = int(text[17:19])

        return ( datetime.datetime(year=year,
                                   month=month,
                                   day=day,
                                   hour=hour,
                                   minute=minute,
                                   second=second), 0)

    elif len(text) > 19 and (text[19] == '+' or text[19] == '-'):
        year = int(text[0:4])
        month = int(text[5:7])
        day = int(text[8:10])
        hour = int(text[11:13])
        minute = int(text[14:16])
        second = int(text[17:19])

        offset = int(text[19:22])

        return ( datetime.datetime(year=year,
                                   month=month,
                                   day=day,
                                   hour=hour,
                                   minute=minute,
                                   second=second),
                 offset )
