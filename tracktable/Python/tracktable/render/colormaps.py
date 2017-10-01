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


"""Several usable, mostly-accessible color maps for use when rendering points and trajectories

These colormaps are registered with matplotlib so that you can refer
to them by name just as you can the standard ones.
"""

import matplotlib.colors
import matplotlib.cm


def make_simple_colormap(color_list, name=None):
    """Create a colormap by spacing colors evenly from 0 to 1

    Take a list of 2 or more colors and space them evenly from 0 to 1.
    The result will be instantiated as a Matplotlib color map and
    returned.  If you include a name, the color map will also be
    registered so that you can refer to it with that name instead of
    needing the object itself.

    Note that this function does not handle transparency at all.  If
    you need that capability you will need to work directly with
    matplotlib.colors.LinearSegmentedColormap.

    Colors are supplied to this function as 'color specifications'.
    Here's the documentation of those, borrowed from the documentation
    for matplotlib.colors.ColorConverter:

    * a letter from the set 'rgbcmykw'
    * a hex color string, like '#0000FF'
    * a standard name, like 'aqua'
    * a float, like '0.4', indicating gray on a 0-1 scale

    Args:
      color_list (list): List of color specifications (described above)
      name (string): Optional name for the color map for registration

    Returns:
      A new matplotlib colormap object.

    Side Effects:
      If you specify a value for the 'name' parameter then the created
      colormap will be registered under that name.

    """

    colors_as_rgb = [ matplotlib.colors.colorConverter.to_rgb(color) for color in color_list ]
    colormap = matplotlib.colors.LinearSegmentedColormap.from_list(name, colors_as_rgb)
    return colormap

# usable color-blind-safe color schemes:
#
# incoming 00BFFF, outgoing 99FF33, other C0C0C0, land 303030, sea 101030
#
# incoming 0099FF, outgoing FFCC00, other 909090, land 303030, sea 101030 (this one is my favorite)

all_yellow = [ '#FFCC00', '#FFCC00' ]
yellow_to_orange = [ '#FFCC00', '#FF9900', '#FF6600' ]
orange_to_yellow = [ '#FF6600', '#FF9900', '#FFCC00' ]
turquoise_to_blue = [ '#0099FF', '#0066FF', '#0033FF' ]
blue_to_turquoise = [ '#0033FF', '#0066FF', '#0099FF' ]
dark_to_light_gray = [ '#666666', '#999999', '#CCCCCC' ]
light_to_dark_gray = [ '#CCCCCC', '#999999', '#666666' ]


#                               0     0.125       0.25      0.5           1
orange_yellow_white = [ '#FF6600', '#FF9900', '#FFCC00', '#FFFFE0', '#FFFFFF' ]
blue_turquoise_white = [ '#0033FF', '#0066FF', '#0099FF', '#E0FFFF', '#FFFFFF' ]

# range on these colormaps is 0 - 40000

all_white_dict = { 'red': [ ( 0,  1, 1 ),
                            ( 1,  1, 1 ) ],
                   'green': [ ( 0,  1, 1 ),
                              ( 1,  1, 1 ) ],
                   'blue': [ ( 0,   1, 1 ),
                             ( 1,   1, 1 ) ] }


all_grey50_dict = { 'red': [ ( 0,  0.5, 0.5 ),
                             ( 1,  0.5, 0.5 ) ],
                    'green': [ ( 0,  0.5, 0.5 ),
                               ( 1,  0.5, 0.5 ) ],
                    'blue': [ ( 0,   0.5, 0.5 ),
                              ( 1,   0.5, 0.5 ) ] }

orange_yellow_white_dict = { 'red':   [ ( 0,      0, 1 ),
                                        ( 0.125,  1, 1 ),
                                        ( 0.25,   1, 1 ),
                                        ( 0.5,    1, 1 ),
                                        ( 1,      1, 1 ) ],

                             'green': [ ( 0,      0, 0.375 ),
                                        ( 0.125,  0.5625, 0.5625 ),
                                        ( 0.25,   0.75, 0.75 ),
                                        ( 0.5,    1, 1 ),
                                        ( 1,      1, 1 ) ],

                             'blue':  [ ( 0,      0, 0 ),
                                        ( 0.125,  0, 0 ),
                                        ( 0.25,   0, 0 ),
                                        ( 0.5,    0.9375, 0.9375 ),
                                        ( 1,      1, 1 ) ] }


blue_turquoise_white_dict = { 'red':  [ ( 0,      0, 0 ),
                                        ( 0.125,  0, 0 ),
                                        ( 0.25,   0, 0 ),
                                        ( 0.5,    0.9375, 0.9375 ),
                                        ( 1,      1, 1 ) ],

                              'green': [ ( 0,     0.1875, 0.1875 ),
                                         ( 0.125, 0.375, 0.375 ),
                                         ( 0.25,  0.5625, 0.5625 ),
                                         ( 0.5,   1, 1 ),
                                         ( 1,     1, 1 ) ],

                              'blue':  [ ( 0,     1, 1 ),
                                         ( 0.125, 1, 1 ),
                                         ( 0.25,  1, 1 ),
                                         ( 0.5,   1, 1 ),
                                         ( 1,     1, 1 ) ] }

unified_colormap_dict = { 'red':   [ ( 0,       0, 1 ),
                                     ( 0.0625,  1, 1 ),
                                     ( 0.125,   1, 1 ),
                                     ( 0.25,    1, 1 ),
                                     ( 0.5,     1, 1 ),
                                     ( 0.75,    0.9375, 0.9375 ),
                                     ( 0.875,   0, 0 ),
                                     ( 0.9375,  0, 0 ),
                                     ( 1,       0, 0 ) ],

                          'green': [ ( 0,       0, 0.375 ),
                                     ( 0.0625,  0.5625, 0.5625 ),
                                     ( 0.125,   0.75, 0.75 ),
                                     ( 0.25,    1, 1 ),
                                     ( 0.5,     1, 1  ),
                                     ( 0.75,    1, 1 ),
                                     ( 0.875,   0.5625, 0.5625 ),
                                     ( 0.9375,  0.375, 0.375 ),
                                     ( 1,       0.1875, 0.1875 ) ],

                          'blue':  [ ( 0,       0, 0 ),
                                     ( 0.0625,  0, 0 ),
                                     ( 0.125,   0, 0 ),
                                     ( 0.25,    0.9375, 0.9375 ),
                                     ( 0.5,     1, 1 ),
                                     ( 0.75,    1, 1 ),
                                     ( 0.875,   1, 1 ),
                                     ( 0.9375,  1, 1 ),
                                     ( 1,       1, 1 ) ],
                          'alpha': [ ( 0,       1, 1 ),
                                     ( 0.25,    1, 1 ),
                                     ( 0.5,     0.4, 0.4 ),
                                     ( 0.75,    1, 1 ),
                                     ( 1,       1, 1 ) ]
                          }


orange_white_blue_dict = { 'red':   [ ( 0,       0, 1 ),
                                      ( 0.0625,  1, 1 ),
                                      ( 0.125,   1, 1 ),
                                      ( 0.45,    1, 1 ),
                                      ( 0.5,     1, 1 ),
                                      ( 0.55,    0.9375, 0.9375 ),
                                      ( 0.875,   0, 0 ),
                                      ( 0.9375,  0, 0 ),
                                      ( 1,       0, 0 ) ],

                          'green': [ ( 0,       0, 0.375 ),
                                     ( 0.0625,  0.5625, 0.5625 ),
                                     ( 0.125,   0.75, 0.75 ),
                                     ( 0.45,    1, 1 ),
                                     ( 0.5,     1, 1  ),
                                     ( 0.55,    1, 1 ),
                                     ( 0.875,   0.5625, 0.5625 ),
                                     ( 0.9375,  0.375, 0.375 ),
                                     ( 1,       0.1875, 0.1875 ) ],

                          'blue':  [ ( 0,       0, 0 ),
                                     ( 0.0625,  0, 0 ),
                                     ( 0.125,   0, 0 ),
                                     ( 0.45,    0.9375, 0.9375 ),
                                     ( 0.5,     1, 1 ),
                                     ( 0.55,    1, 1 ),
                                     ( 0.875,   1, 1 ),
                                     ( 0.9375,  1, 1 ),
                                     ( 1,       1, 1 ) ],
                          'alpha': [ ( 0,       1, 1 ),
                                     ( 0.25,    1, 1 ),
                                     ( 0.5,     0.4, 0.4 ),
                                     ( 0.75,    1, 1 ),
                                     ( 1,       1, 1 ) ]
                          }

blue_white_orange_dict = { 'red':   [ ( 0,       0, 0 ),
                                      ( 0.0625,  0, 0 ),
                                      ( 0.125,   0, 0 ),
                                      ( 0.45,    0.9375, 0.9375 ),
                                      ( 0.5,     1, 1 ),
                                      ( 0.55,    1, 1 ),
                                      ( 0.875,   1, 1 ),
                                      ( 0.9375,  1, 1 ),
                                      ( 1,       1, 1 ) ],

                           'green': [ ( 0,       0.1875, 0.1875 ),
                                      ( 0.0625,  0.375, 0.375 ),
                                      ( 0.125,   0.5625, 0.5625 ),
                                      ( 0.45,    1, 1 ),
                                      ( 0.5,     1, 1 ),
                                      ( 0.55,    1, 1 ),
                                      ( 0.875,   0.75, 0.75 ),
                                      ( 0.9375,  0.5625, 0.5625 ),
                                      ( 1,       0.375, 0.375 ) ],

                           'blue': [ ( 0,       1, 1 ),
                                     ( 0.0625,  1, 1 ),
                                     ( 0.125,   1, 1 ),
                                     ( 0.45,    1, 1 ),
                                     ( 0.5,     1, 1 ),
                                     ( 0.55,    0.9375, 0.9375 ),
                                     ( 0.875,   0, 0 ),
                                     ( 0.9375,  0, 0 ),
                                     ( 1,       0, 0 ) ],

                           'alpha': [ ( 0,      1, 1 ),
                                      ( 0.25,   1, 1 ),
                                      ( 0.5,    0.4, 0.4 ),
                                      ( 0.75,   1, 1 ),
                                      ( 1,      1, 1 ) ]
                          }

blue_white_orange_opaque_dict = { 'red':   [ ( 0,       0, 0 ),
                                      ( 0.0625,  0, 0 ),
                                      ( 0.125,   0, 0 ),
                                      ( 0.45,    0.9375, 0.9375 ),
                                      ( 0.5,     1, 1 ),
                                      ( 0.55,    1, 1 ),
                                      ( 0.875,   1, 1 ),
                                      ( 0.9375,  1, 1 ),
                                      ( 1,       1, 1 ) ],

                           'green': [ ( 0,       0.1875, 0.1875 ),
                                      ( 0.0625,  0.375, 0.375 ),
                                      ( 0.125,   0.5625, 0.5625 ),
                                      ( 0.45,    1, 1 ),
                                      ( 0.5,     1, 1 ),
                                      ( 0.55,    1, 1 ),
                                      ( 0.875,   0.75, 0.75 ),
                                      ( 0.9375,  0.5625, 0.5625 ),
                                      ( 1,       0.375, 0.375 ) ],

                           'blue': [ ( 0,       1, 1 ),
                                     ( 0.0625,  1, 1 ),
                                     ( 0.125,   1, 1 ),
                                     ( 0.45,    1, 1 ),
                                     ( 0.5,     1, 1 ),
                                     ( 0.55,    0.9375, 0.9375 ),
                                     ( 0.875,   0, 0 ),
                                     ( 0.9375,  0, 0 ),
                                     ( 1,       0, 0 ) ],

                           'alpha': [ ( 0,      1, 1 ),
                                      ( 0.25,   1, 1 ),
                                      ( 0.5,    1, 1 ),
                                      ( 0.75,   1, 1 ),
                                      ( 1,      1, 1 ) ]
                          }

blue_white_orange_semitransparent_dict = { 'red':   [ ( 0,       0, 0 ),
                                                      ( 0.0625,  0, 0 ),
                                                      ( 0.125,   0, 0 ),
                                                      ( 0.45,    0.9375, 0.9375 ),
                                                      ( 0.5,     1, 1 ),
                                                      ( 0.55,    1, 1 ),
                                                      ( 0.875,   1, 1 ),
                                                      ( 0.9375,  1, 1 ),
                                                      ( 1,       1, 1 ) ],

                                           'green': [ ( 0,       0.1875, 0.1875 ),
                                                      ( 0.0625,  0.375, 0.375 ),
                                                      ( 0.125,   0.5625, 0.5625 ),
                                                      ( 0.45,    1, 1 ),
                                                      ( 0.5,     1, 1 ),
                                                      ( 0.55,    1, 1 ),
                                                      ( 0.875,   0.75, 0.75 ),
                                                      ( 0.9375,  0.5625, 0.5625 ),
                                                      ( 1,       0.375, 0.375 ) ],

                                           'blue': [ ( 0,       1, 1 ),
                                                     ( 0.0625,  1, 1 ),
                                                     ( 0.125,   1, 1 ),
                                                     ( 0.45,    1, 1 ),
                                                     ( 0.5,     1, 1 ),
                                                     ( 0.55,    0.9375, 0.9375 ),
                                                     ( 0.875,   0, 0 ),
                                                     ( 0.9375,  0, 0 ),
                                                     ( 1,       0, 0 ) ],

                                           'alpha': [ ( 0,      0.5, 0.5 ),
                                                      ( 0.25,   0.5, 0.5 ),
                                                      ( 0.5,    0.2, 0.2 ),
                                                      ( 0.75,   0.5, 0.5 ),
                                                      ( 1,      0.5, 0.5 ) ]
                                       }

blue_white_orange_brighter_dict = { 'red':   [ ( 0,       0.1, 0.1 ),
                                               ( 0.0625,  0.1, 0.1 ),
                                               ( 0.125,   0.1, 0.1 ),
                                               ( 0.45,    0.9375, 0.9375 ),
                                               ( 0.5,     1, 1 ),
                                               ( 0.55,    1, 1 ),
                                               ( 0.875,   1, 1 ),
                                               ( 0.9375,  1, 1 ),
                                               ( 1,       1, 1 ) ],

                                    'green': [ ( 0,       0.2875, 0.2875 ),
                                               ( 0.0625,  0.475, 0.475 ),
                                               ( 0.125,   0.5625, 0.5625 ),
                                               ( 0.45,    1, 1 ),
                                               ( 0.5,     1, 1 ),
                                               ( 0.55,    1, 1 ),
                                               ( 0.875,   0.75, 0.75 ),
                                               ( 0.9375,  0.5625, 0.5625 ),
                                               ( 1,       0.375, 0.375 ) ],

                                    'blue': [ ( 0,       1, 1 ),
                                              ( 0.0625,  1, 1 ),
                                              ( 0.125,   1, 1 ),
                                              ( 0.45,    1, 1 ),
                                              ( 0.5,     1, 1 ),
                                              ( 0.55,    0.9375, 0.9375 ),
                                              ( 0.875,   0, 0 ),
                                              ( 0.9375,  0, 0 ),
                                              ( 1,       0, 0 ) ],

                                    'alpha': [ ( 0,      1, 1 ),
                                               ( 0.25,   1, 1 ),
                                               ( 0.5,    0.5, 0.5 ),
                                               ( 0.75,   1, 1 ),
                                               ( 1,      1, 1 ) ]
                                }



blue_white_orange_invisible_middle_dict = { 'red':   [ ( 0,       0.1, 0.1 ),
                                                       ( 0.0625,  0.1, 0.1 ),
                                                       ( 0.125,   0.1, 0.1 ),
                                                       ( 0.45,    0.9375, 0.9375 ),
                                                       ( 0.5,     1, 1 ),
                                                       ( 0.55,    1, 1 ),
                                                       ( 0.875,   1, 1 ),
                                                       ( 0.9375,  1, 1 ),
                                                       ( 1,       1, 1 ) ],

                                            'green': [ ( 0,       0.2875, 0.2875 ),
                                                       ( 0.0625,  0.475, 0.475 ),
                                                       ( 0.125,   0.5625, 0.5625 ),
                                                       ( 0.45,    1, 1 ),
                                                       ( 0.5,     1, 1 ),
                                                       ( 0.55,    1, 1 ),
                                                       ( 0.875,   0.75, 0.75 ),
                                                       ( 0.9375,  0.5625, 0.5625 ),
                                                       ( 1,       0.375, 0.375 ) ],

                                            'blue': [ ( 0,       1, 1 ),
                                                      ( 0.0625,  1, 1 ),
                                                      ( 0.125,   1, 1 ),
                                                      ( 0.45,    1, 1 ),
                                                      ( 0.5,     1, 1 ),
                                                      ( 0.55,    0.9375, 0.9375 ),
                                                      ( 0.875,   0, 0 ),
                                                      ( 0.9375,  0, 0 ),
                                                      ( 1,       0, 0 ) ],

                                            'alpha': [ ( 0,      1, 1 ),
                                                       ( 0.25,   1, 1 ),
                                                       ( 0.5,    0.1, 0.1 ),
                                                       ( 0.75,   1, 1 ),
                                                       ( 1,      1, 1 ) ]
                                        }


red_blue_dict = { 'red':   [ ( 0,     1, 1 ),
                             ( 1,     0, 0 ) ],
                  'green': [ ( 0,     0, 0 ),
                             ( 1,     0, 0 ) ],
                  'blue':  [ ( 0,     0, 0),
                             ( 1,     1, 1) ] }


# unified colormap:
#
# 0:      [ 1, 0.375, 0 ]
# 0.0625: [ 1, 0.5625, 0 ]
# 0.125:  [ 1, 0.75, 0 ]
# 0.25:   [ 1, 1, 0.9375 ]
# 0.5:    [ 1, 1, 1 ]
# 0.75:   [ 0.9375, 1, 1 ]
# 0.875:  [ 0, 0.5625, 1 ]
# 0.9375: [ 0, 0.375, 1 ]
# 1:      [ 0, 0.1875, 1 ]

red_blue = matplotlib.colors.LinearSegmentedColormap('red_blue', red_blue_dict)

orange_yellow_white = matplotlib.colors.LinearSegmentedColormap('orange_yellow_white', orange_yellow_white_dict)
blue_turquoise_white = matplotlib.colors.LinearSegmentedColormap('blue_turquoise_white', blue_turquoise_white_dict)

approach_departure = matplotlib.colors.LinearSegmentedColormap('unified', unified_colormap_dict)

orange_white_blue = matplotlib.colors.LinearSegmentedColormap('orange_white_blue', orange_white_blue_dict)
blue_white_orange = matplotlib.colors.LinearSegmentedColormap('blue_white_orange', blue_white_orange_dict)
blue_white_orange_semitransparent = matplotlib.colors.LinearSegmentedColormap('blue_white_orange_semitransparent', blue_white_orange_semitransparent_dict)
blue_white_orange_opaque = matplotlib.colors.LinearSegmentedColormap('blue_white_orange_opaque', blue_white_orange_opaque_dict)

blue_white_orange_brighter = matplotlib.colors.LinearSegmentedColormap('blue_white_orange_brighter', blue_white_orange_brighter_dict)

blue_white_orange_invisible_middle = matplotlib.colors.LinearSegmentedColormap('blue_white_orange_invisible_middle', blue_white_orange_invisible_middle_dict)

all_white = matplotlib.colors.LinearSegmentedColormap('all_white', all_white_dict)
all_grey50 = matplotlib.colors.LinearSegmentedColormap('all_grey50', all_grey50_dict)

yellow_to_orange_colormap = make_simple_colormap(yellow_to_orange, 'yellow_to_orange')
orange_to_yellow_colormap = make_simple_colormap(orange_to_yellow, 'orange_to_yellow')
turquoise_to_blue_colormap = make_simple_colormap(turquoise_to_blue, 'turqoise_to_blue')
blue_to_turquoise_colormap = make_simple_colormap(blue_to_turquoise, 'blue_to_turquoise')
dark_to_light_gray_colormap = make_simple_colormap(dark_to_light_gray, 'dark_to_light_gray')
light_to_dark_gray_colormap = make_simple_colormap(light_to_dark_gray, 'light_to_dark_gray')
all_yellow_colormap = make_simple_colormap(all_yellow, 'all_yellow')

matplotlib.cm.register_cmap('red_blue', red_blue)
matplotlib.cm.register_cmap('orange_yellow_white', orange_yellow_white)
matplotlib.cm.register_cmap('blue_turquoise_white', blue_turquoise_white)
matplotlib.cm.register_cmap('approach_departure', approach_departure)
matplotlib.cm.register_cmap('orange_white_blue', orange_white_blue)
matplotlib.cm.register_cmap('blue_white_orange_brighter', blue_white_orange_brighter)
matplotlib.cm.register_cmap('blue_white_orange_opaque', blue_white_orange_opaque)
matplotlib.cm.register_cmap('blue_white_orange_semitransparent', blue_white_orange_semitransparent)
matplotlib.cm.register_cmap('blue_white_orange_invisible_middle', blue_white_orange_invisible_middle)
matplotlib.cm.register_cmap('blue_white_orange', blue_white_orange)
