#
# Copyright (c) 2014-2023 National Technology and Engineering
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

from __future__ import print_function

import datetime
import pytz
import sys

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot

from tracktable.render.map_processing import maps
from tracktable.render.map_decoration import clock
from tracktable.core import Timestamp

def run_test():
    figure = pyplot.figure(figsize=(8, 6), dpi=100)
    axes = figure.add_axes([0, 0, 1, 1], frameon=False, facecolor='black')
    axes.set_frame_on(False)

    my_timestamp = Timestamp.from_any('2013-06-07 23:18:54-0500')

    def format_time1(timestamp):
        return Timestamp.to_string(timestamp)

    def format_time2(timestamp):
        hours = timestamp.time().hour
        minutes = timestamp.time().minute
        if minutes < 30:
            minutes = 0
        else:
            minutes = 30

        new_timestamp = datetime.datetime(year=my_timestamp.date().year,
                                          month=my_timestamp.date().month,
                                          day=my_timestamp.date().day,
                                          hour=hours,
                                          minute=minutes,
                                          second=0,
                                          tzinfo=timestamp.tzinfo)

        new_timestamp = new_timestamp.astimezone(pytz.timezone('US/Pacific'))

        print("format_time2: new timestamp is {}".format(str(new_timestamp)))

        return Timestamp.to_string(new_timestamp, format_string='%H:%M', include_tz=False)

    (mymap, artists) = maps.predefined_map('conus', ax=axes)

    clock_artist1 = clock.digital_clock(my_timestamp,
                                        format_time1,
                                        (0.1, 0.1),
                                        family='fantasy',
                                        ha='left',
                                        va='top',
                                        size=24,
#                                        rotation=45,
                                        weight='normal',
                                        zorder=10)

    clock_artist2 = clock.digital_clock(my_timestamp,
                                        format_time2,
                                        (0.95, 0.95),
                                        ha='right',
                                        va='baseline',
                                        family='cursive',
                                        weight='light',
                                        color='white',
                                        size=12,
                                        backgroundcolor='black',
                                        zorder=10)

    pyplot.savefig('/tmp/test_digital_clock.png')
    return 0

if __name__ == '__main__':
    sys.exit(run_test())

