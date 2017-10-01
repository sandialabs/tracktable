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

"""Parameters for movie rendering.

This argument group contains just those parameters that are specific
to movie rendering such as the encoder to use, frames per second,
duration, etc.  Image-related stuff such as resolution and DPI is in
the 'image' argument group.

Note that the timezone label is not a natural fit for this argument
group.  I haven't yet figured out where else to put it.

Arguments:

| ``--encoder NAME``
|   Which movie encoder to use.  Defaults to FFMPEG.
|
| ``--duration NN``
|   How many seconds long the movie should be
|
| ``--fps NN``
|   How many frames per second the movie should contain
|
| ``--start-time TIME``
|   Start time for the movie in 'YYYY-MM-DD HH:MM:SS+XX' format (defaults to start time of data)
|
| ``--end-time TIME``
|   End time for the movie in 'YYYY-MM-DD HH:MM:SS+XX' format (defaults to end time of data)
|
| ``--encoder-args STRING``
|   Extra args to pass to the encoder (specify as a single string)
|
| ``--utc-offset NN``
|   UTC offset for displayed timestamp (will convert to local time zone)
|
| ``--timezone-label STRING``
|   Time zone label to be added to clock

"""


from tracktable.script_helpers.argument_groups import create_argument_group, add_argument

GROUP_INSTALLED = False

def install_group():
    """Standard method - define the Movie Rendering argument group"""

    global GROUP_INSTALLED
    if GROUP_INSTALLED:
        return
    else:
        GROUP_INSTALLED = True


    create_argument_group("movie_rendering",
                          title="Movie Parameters",
                          description="Movie-specific parameters such as frame rate, encoder options, title and metadata")

    add_argument("movie_rendering", [ "--encoder" ],
                 default="ffmpeg",
                 choices=[ "ffmpeg", "mencoder", "avconv", "imagemagick" ],
                 help="Which encoder to use.  NOTE: All options may not be available on all systems.")

    add_argument("movie_rendering", [ "--duration" ],
                 type=int,
                 default=60,
                 help="How many seconds long the movie should be")

    add_argument("movie_rendering", [ "--fps" ],
                 type=int,
                 default=30,
                 help="Movie frame rate in frames/second")

    add_argument("movie_rendering", [ "--start-time" ],
                 help="Start time for the movie in 'YYYY-MM-DD HH:MM:SS+XX' format (defaults to start time of data)")

    add_argument("movie_rendering", [ "--end-time" ],
                 help="End time for the movie in 'YYYY-MM-DD HH:MM:SS+XX' format (defaults to end time of data)")

    add_argument("movie_rendering", [ "--encoder-args" ],
                 default="-c:v mpeg4 -q:v 5",
                 help="Extra args to pass to the encoder (pass in as a single string)")

    add_argument("movie_rendering", [ "--utc-offset" ],
                 type=int,
                 help="UTC offset for displayed timestamp (will convert to local timezone)")

    add_argument("movie_rendering", [ "--timezone-label" ],
                 help="Timezone label to be added to clock")

    add_argument("movie_rendering", [ '--resolution', '-r' ],
                 nargs=2,
                 type=int,
                 help='Resolution of movie frames.  Defaults to 800 600.')

    add_argument("movie_rendering", [ '--dpi' ],
                 type=int,
                 default=72,
                 help='DPI of movie frames.')
