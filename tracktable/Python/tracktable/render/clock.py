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

"""Draw a digital clock on a Matplotlib figure"""


from __future__ import print_function, division, absolute_import

import math

from matplotlib import pyplot, collections, lines, patches, text
from six.moves import range

def draw_analog_clock_on_map(time,
                             offset=None, # should be a datetime.timedelta
                             center=(0.5,0.5), # in image coordinates, not axis coordinates!
                             radius=0.05, # again, in image coordinates
                             axes=None,
                             use_short_side_for_radius=True,
                             long_hand_radius=0.9,
                             short_hand_radius=0.5,
                             tickmarks=True,
                             tickmark_length=0.25, # in fractions of the radius
                             color='white',
                             linewidth=1,
                             zorder=4,
                             label=None,
                             label_placement='top',
                             label_kwargs=dict()):
    """Draw an analog clock on a Matplotlib figure.

    NOTE: THIS INTERFACE IS SUBJECT TO CHANGE.  LOTS OF CHANGE.

    Args:
      time (datetime.datetime): Time to display
      offset (datetime.timedelta): Offset for local time zone.  This
           will be added to the 'time' argument to determine the
           time that will actually be displayed.
      center (2-tuple in [0,1] * [0, 1]): image-space center of clock
      radius (float in [0, 1]): Radius of clock face
      axes (matplotlib.axes.Axes): axes to render into
      use_short_side_for_radius (boolean): Clock radius will 
           be calculated relative to short side of figure
      long_hand_radius (float in [0, 1]): Radius of minute hand relative
           to radius of clock face
      short_hand_radius (float in [0,1]): Radius of hour hand relative
           to radius of clock face
      tickmarks (boolean): Whether or not to place tickmarks at every
           hour around the clock face
      tickmark_length (float in [0,1]): Length of tickmarks relative
           to clock face radius
      color (colorspec): Color for clock face and hands
      linewidth (float): Thickness (in points) of lines drawn
      zorder (integer): Ordering of clock in image element stack
           (higher values are on top)
      label (string): Label text to display near clock
      label_placement (string): One of 'top', 'bottom'.  Determines
           where label will be rendered relative to clock face
      label_kwargs (dict): Arguments to be passed to Matplotlib
           text renderer for label

    Side Effects:
      The clock actors will be added to the 'axes' argument or (if no
         axes are supplied) to the current Matplotlib axes.

    Returns:
      A list of Matplotlib artists added to the figure.
    """

    if axes is None:
        axes = pyplot.gca()

    transform = axes.transData

    # Find the appropriate side of the image to measure the clock
    # against
    axis_x_bounds = axes.get_xbound()
    axis_y_bounds = axes.get_ybound()
    axis_x_span = axis_x_bounds[1] - axis_x_bounds[0]
    axis_y_span = axis_y_bounds[1] - axis_y_bounds[0]

    if use_short_side_for_radius:
        axis_span = min(axis_x_span, axis_y_span)
    else:
        axis_span = max(axis_x_span, axis_y_span)


    actors_to_return = []

    clock_radius = axis_span * radius

    time_as_datetime = time
    if offset:
        time_as_datetime += offset
    hour = time_as_datetime.hour
    minute = time_as_datetime.minute
    second = time_as_datetime.second

    second_of_day = second + (minute*60) + (hour*3600)
    fraction_of_day = float(second_of_day) / 86400.0

    second_of_hour = second + (minute * 60)
    fraction_of_hour = float(second_of_hour) / 3600

    hour_hand_radius = short_hand_radius * clock_radius
    minute_hand_radius = long_hand_radius * clock_radius


    # In a polar coordinate system where 0 is along the positive
    # x-axis, our clock hands rotate in a negative direction starting
    # at pi/2.

    minute_hand_angle = (0.5 * math.pi) - (2 * math.pi * fraction_of_hour)
    # Since we want the hour hand to go twice around in a day instead
    # of just once we multiply by 4pi
    hour_hand_angle = (0.5 * math.pi) - (4 * math.pi * fraction_of_day)

    minute_hand_endpoint = ( minute_hand_radius * math.cos(minute_hand_angle),
                             minute_hand_radius * math.sin(minute_hand_angle) )

    hour_hand_endpoint = ( hour_hand_radius * math.cos(hour_hand_angle),
                           hour_hand_radius * math.sin(hour_hand_angle) )

    center_in_axis_space = ( center[0] * axis_x_span + axis_x_bounds[0],
                              center[1] * axis_y_span + axis_y_bounds[0] )

    if label:
        my_label_kwargs = { 'horizontalalignment': 'center',
                            'verticalalignment': 'bottom',
                            'rotation': 'horizontal',
                            'size': 12
                            }

        if label_placement == 'top':
            label_anchor = ( center_in_axis_space[0],
                             center_in_axis_space[1] + 1.25 * clock_radius )
            my_label_kwargs['verticalalignment'] = 'bottom'
        elif label_placement == 'bottom':
            label_anchor = ( center_in_axis_space[0],
                             center_in_axis_space[1] - 1.25 * clock_radius )
            my_label_kwargs['verticalalignment'] = 'top'
        elif label_placement == 'right':
            label_anchor = ( center_in_axis_space[0] + 1.25 * clock_radius,
                             center_in_axis_space[1] )
            my_label_kwargs['horizontalalignment'] = 'left'
            my_label_kwargs['verticalalignment'] = 'center',
            my_label_kwargs['rotation'] = 'vertical'
        elif label_placement == 'left':
            label_anchor = ( center_in_axis_space[0] - 1.25 * clock_radius,
                             center_in_axis_space[1] )
            my_label_kwargs['horizontalalignment'] = 'right'
            my_label_kwargs['verticalalignment'] = 'center'
            my_label_kwargs['rotation'] = 'vertical'

        my_label_kwargs.update(label_kwargs)

        label_actor = text.Text(x=label_anchor[0],
                                y=label_anchor[1],
                                text=label,
                                **my_label_kwargs)

        actors_to_return.append(label_actor)
        axes.add_artist(label_actor)

    minute_hand_endpoint = ( center_in_axis_space[0] + minute_hand_endpoint[0],
                             center_in_axis_space[1] + minute_hand_endpoint[1] )
    hour_hand_endpoint = ( center_in_axis_space[0] + hour_hand_endpoint[0],
                           center_in_axis_space[1] + hour_hand_endpoint[1] )

    minute_hand_coords = { 'x': [ center_in_axis_space[0],
                                  minute_hand_endpoint[0] ],
                           'y': [ center_in_axis_space[1],
                                  minute_hand_endpoint[1] ] }

    hour_hand_coords = { 'x': [ center_in_axis_space[0],
                                hour_hand_endpoint[0] ],
                         'y': [ center_in_axis_space[1],
                                hour_hand_endpoint[1] ] }

    tickmark_segments = []

    for hour in range(12):
        hour_angle = - (hour / 12.0) * 2 * math.pi

        center_point = ( center_in_axis_space[0], center_in_axis_space[1] )
        vector_to_outside = ( clock_radius * math.cos(hour_angle),
                              clock_radius * math.sin(hour_angle) )
        vector_to_inside = ( (1-tickmark_length) * clock_radius * math.cos(hour_angle),
                             (1-tickmark_length) * clock_radius * math.sin(hour_angle) )

        new_segment = ( ( center_point[0] + vector_to_inside[0],
                          center_point[1] + vector_to_inside[1] ),
                        ( center_point[0] + vector_to_outside[0],
                          center_point[1] + vector_to_outside[1] ) )

        tickmark_segments.append(new_segment)

    hour_tickmarks = collections.LineCollection(tickmark_segments,
                                                linewidths=0.5 * linewidth,
                                                colors=color,
                                                zorder=zorder,
                                                transform=transform)

    minute_hand = lines.Line2D(minute_hand_coords['x'], minute_hand_coords['y'],
                               linewidth=linewidth,
                               color=color,
                               zorder=zorder,
                               transform=transform)

    hour_hand = lines.Line2D(hour_hand_coords['x'], hour_hand_coords['y'],
                             linewidth=linewidth,
                             color=color,
                             zorder=zorder,
                             transform=transform)

    boundary = patches.Circle( center_in_axis_space,
                               clock_radius,
                               zorder=zorder,
                               color=color,
                               linewidth=linewidth,
                               fill=fill_circle,
                               transform=transform )

    axes.add_line(minute_hand)
    axes.add_line(hour_hand)
    axes.add_artist(hour_tickmarks)
    axes.add_artist(boundary)

    return [ boundary, minute_hand, hour_hand, hour_tickmarks ]

# ----------------------------------------------------------------------

def digital_clock(time,
                  formatter,
                  position,
                  **kwargs):
    """Add a digital clock (a string representation of time) to the image at a user-specified location

    XXX: This function may go away since it doesn't provide any useful
    enhancement over just adding a text actor ourselves.

    """

    time_string = formatter(time)
    return [ pyplot.figtext(position[0], position[1],
                            time_string,
                            **kwargs) ]
