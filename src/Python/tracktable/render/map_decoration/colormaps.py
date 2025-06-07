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


"""Several usable, mostly-accessible color maps for use when rendering points and trajectories

These colormaps are registered with matplotlib so that you can refer
to them by name just as you can the standard ones.

Colormaps registered are available by name through
``matplotlib.colormaps[cmap_name]``.  You can also use them with
``render_trajectories()`` regardless of which back end you're using.

Here are the names of all the color maps:

- red_blue
- orange_yellow_white
- blue_turquoise_white
- approach_departure
- orange_white_blue
- blue_white_orange
- blue_white_orange_semitransparent
_ blue_white_orange_opaque
- blue_white_orange_brighter
- blue_white_orange_invisible_middle
- all_white
- all_grey50
- all_yellow
- yellow_orange
- orange_yellow
- turquoise_blue
- blue_turquoise

"""

import matplotlib as mpl
from matplotlib import colors

import typing
from typing import Literal, Sequence, Tuple


COLORMAPS_REGISTERED: bool = False

# We don't get TypeAlias until Python 3.10.
#MatplotlibColor: typing.TypeAlias = typing.Union[
MatplotlibColor = typing.Union[
    str,  # HTML colorspec or color name or float as string or
    # single-character shorthand or XKCD color survey or
    # Tableau color
    tuple[float, float, float],  # RGB
    tuple[float, float, float, float],  # RGBA
    tuple[str, float]  # str + alpha
]

# SegmentedColormap: typing.TypeAlias = dict[
SegmentedColormap = dict[
    Literal["red", "green", "blue", "alpha"],
    Sequence[Tuple[float, ...]]
]

def make_simple_colormap(
    name: str, color_list: list[MatplotlibColor]
) -> colors.Colormap:
    """Create a colormap by spacing colors evenly from 0 to 1

    Take a list of 2 or more colors and space them evenly from 0 to 1.
    The result will be instantiated as a named Matplotlib color map and
    returned.  You must still register the color map yourself.

    Args:
      name (str): Name of colormap.
      color_list (list of colors): List of color specifications.  Colors
         can be specified as strings (color names or HTML colors),
         tuples of floats (RGB or RGBA), or a tuple of a string plus
         a float (named color plus alpha).

    Returns:
      mpl.colors.Colormap: New colormap object.
    """

    colors_as_rgb = [
        colors.colorConverter.to_rgb(color) for color in color_list
    ]
    colormap = colors.LinearSegmentedColormap.from_list(name, colors_as_rgb)
    return colormap


def register_colormaps():
    """Register all colormaps with Matplotlib.

    This function is idempotent.  It checks the COLORMAPS_REGISTERED
    flag before taking any action, then sets that flag when finished.
    It will execute when you import the module for the first time.

    No arguments.

    Returns None.
    """

    global COLORMAPS_REGISTERED

    if COLORMAPS_REGISTERED:
        return

    all_colormaps = [
        red_blue_colormap(),
        orange_yellow_white_colormap(),
        blue_turquoise_white_colormap(),
        approach_departure_colormap(),
        orange_white_blue_colormap(),
        blue_white_orange_colormap(),
        blue_white_orange_semitransparent_colormap(),
        blue_white_orange_opaque_colormap(),
        blue_white_orange_brighter_colormap(),
        blue_white_orange_invisible_middle_colormap(),
        all_white_colormap(),
        all_grey50_colormap(),
        all_yellow_colormap(),
        yellow_orange_colormap(),
        orange_yellow_colormap(),
        turquoise_blue_colormap(),
        blue_turquoise_colormap()
    ]

    for cmap in all_colormaps:
        mpl.colormaps.register(cmap)

    COLORMAPS_REGISTERED = True


def red_blue_colormap() -> colors.Colormap:
    """Create a colormap that goes smoothly from red to blue

    No arguments.

    Returns:
        mpl.colors.Colormap: New colormap for red->blue
    """

    return colors.LinearSegmentedColormap.from_list("red_blue", ["red", "blue"])


def orange_yellow_white_colormap() -> colors.Colormap:
    """Create a colormap that goes smoothly from orange to yellow to white

    No arguments.

    Returns:
        mpl.colors.Colormap: New colormap for orange->yellow->white
    """

    orange_yellow_white_dict: SegmentedColormap = {
        "red": [
            (0,     0, 1),
            (0.125, 1, 1),
            (0.25,  1, 1),
            (0.5,   1, 1),
            (1,     1, 1)
            ],
        "green": [
            (0,     0, 0.375),
            (0.125, 0.5625, 0.5625),
            (0.25,  0.75, 0.75),
            (0.5,   1, 1),
            (1,     1, 1)
        ],
        "blue": [
            (0,     0, 0),
            (0.125, 0, 0),
            (0.25,  0, 0),
            (0.5,   0.9375, 0.9375),
            (1,     1, 1)
        ]
    }

    # MyPy can't figure out that the dict is in fact in the format
    # LinearSegmentedColormap() wants so it complains incorrectly
    return colors.LinearSegmentedColormap(
        "orange_yellow_white",
        orange_yellow_white_dict
    )


def blue_turquoise_white_colormap() -> colors.Colormap:
    """Create a colormap that goes smoothly from blue to turquoise to white

    No arguments.

    Returns:
        mpl.colors.Colormap: New colormap for blue->turquoise->white
    """

    blue_turquoise_white_dict: SegmentedColormap = {
    "red": [
        (0, 0, 0),
        (0.125, 0, 0),
        (0.25, 0, 0),
        (0.5, 0.9375, 0.9375),
        (1, 1, 1)],
    "green": [
        (0, 0.1875, 0.1875),
        (0.125, 0.375, 0.375),
        (0.25, 0.5625, 0.5625),
        (0.5, 1, 1),
        (1, 1, 1),
    ],
    "blue": [
        (0, 1, 1),
        (0.125, 1, 1),
        (0.25, 1, 1),
        (0.5, 1, 1),
        (1, 1, 1)]
    }

    return colors.LinearSegmentedColormap(
        "blue_turquoise_white",
        blue_turquoise_white_dict
        )


def approach_departure_colormap() -> colors.Colormap:
    """Return a blue-white-orange colormap

    This colormap is useful for highlighting flights
    on approach or departure.  Use climb rate as the color variable
    and normalize so that a climb rate of 0 maps to 0.5.
    The blues at the bottom are negative climb rates that
    usually indicate approach and landing.  The oranges at
    the top are climbs that indicate departures.  The semitransparent whites
    in the middle are level flight.

    No arguments.

    Returns:
        mpl.colors.Colormap: Blue/white/orange colormap
    """

    unified_colormap_dict: SegmentedColormap = {
        "red": [
            (0, 0, 1),
            (0.0625, 1, 1),
            (0.125, 1, 1),
            (0.25, 1, 1),
            (0.5, 1, 1),
            (0.75, 0.9375, 0.9375),
            (0.875, 0, 0),
            (0.9375, 0, 0),
            (1, 0, 0),
        ],
        "green": [
            (0, 0, 0.375),
            (0.0625, 0.5625, 0.5625),
            (0.125, 0.75, 0.75),
            (0.25, 1, 1),
            (0.5, 1, 1),
            (0.75, 1, 1),
            (0.875, 0.5625, 0.5625),
            (0.9375, 0.375, 0.375),
            (1, 0.1875, 0.1875),
        ],
        "blue": [
            (0, 0, 0),
            (0.0625, 0, 0),
            (0.125, 0, 0),
            (0.25, 0.9375, 0.9375),
            (0.5, 1, 1),
            (0.75, 1, 1),
            (0.875, 1, 1),
            (0.9375, 1, 1),
            (1, 1, 1),
        ],
        "alpha": [
            (0, 1, 1),
            (0.25, 1, 1),
            (0.5, 0.4, 0.4),
            (0.75, 1, 1),
            (1, 1, 1)]
    }

    return colors.LinearSegmentedColormap(
        "approach_departure",
        unified_colormap_dict
    )


def orange_white_blue_colormap() -> colors.Colormap:
    """Create an orange-white-blue colormap

    Colors are evenly spaced: orange at 0, white at 0.5, blue at 1.
    Semitransparent in the middle.

    No arguments.

    Returns:
        mpl.colors.Colormap: Orange->white->blue
    """

    orange_white_blue_dict: SegmentedColormap = {
        "red": [
            (0, 0, 1),
            (0.0625, 1, 1),
            (0.125, 1, 1),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 0.9375, 0.9375),
            (0.875, 0, 0),
            (0.9375, 0, 0),
            (1, 0, 0),
        ],
        "green": [
            (0, 0, 0.375),
            (0.0625, 0.5625, 0.5625),
            (0.125, 0.75, 0.75),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 0.5625, 0.5625),
            (0.9375, 0.375, 0.375),
            (1, 0.1875, 0.1875),
        ],
        "blue": [
            (0, 0, 0),
            (0.0625, 0, 0),
            (0.125, 0, 0),
            (0.45, 0.9375, 0.9375),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 1, 1),
            (0.9375, 1, 1),
            (1, 1, 1),
        ],
        "alpha": [(0, 1, 1), (0.25, 1, 1), (0.5, 0.4, 0.4), (0.75, 1, 1), (1, 1, 1)],
    }
    return colors.LinearSegmentedColormap(
        "orange_white_blue", orange_white_blue_dict
        )


def blue_white_orange_colormap() -> colors.Colormap:
    """Create a blue-white-orange colormap

    Colors are evenly spaced: blue at 0, white at 0.5, orange at 1.
    Semitransparent in the middle.  This is the reverse of
    orange_white_blue.

    No arguments.

    Returns:
        mpl.colors.Colormap: Blue->white->orange
    """

    blue_white_orange_dict: SegmentedColormap = {
        "red": [
            (0, 0, 0),
            (0.0625, 0, 0),
            (0.125, 0, 0),
            (0.45, 0.9375, 0.9375),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 1, 1),
            (0.9375, 1, 1),
            (1, 1, 1),
        ],
        "green": [
            (0, 0.1875, 0.1875),
            (0.0625, 0.375, 0.375),
            (0.125, 0.5625, 0.5625),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 0.75, 0.75),
            (0.9375, 0.5625, 0.5625),
            (1, 0.375, 0.375),
        ],
        "blue": [
            (0, 1, 1),
            (0.0625, 1, 1),
            (0.125, 1, 1),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 0.9375, 0.9375),
            (0.875, 0, 0),
            (0.9375, 0, 0),
            (1, 0, 0),
        ],
        "alpha": [(0, 1, 1), (0.25, 1, 1), (0.5, 0.4, 0.4), (0.75, 1, 1), (1, 1, 1)],
    }

    return colors.LinearSegmentedColormap(
        "blue_white_orange",
        blue_white_orange_dict
    )


def blue_white_orange_semitransparent_colormap() -> colors.Colormap:
    """Create a blue-white-orange colormap with alpha=0.5

    Colors are evenly spaced: blue at 0, white at 0.5, orange at 1.
    All semitransparent.  Alpha goes all the way down to 0.2 in the
    middle.  This lets you maintain a more readable
    image when lots of lines pile up on top of one another.

    No arguments.

    Returns:
        mpl.colors.Colormap: Blue->white->orange
    """

    blue_white_orange_semitransparent_dict: SegmentedColormap = {
        "red": [
            (0, 0, 0),
            (0.0625, 0, 0),
            (0.125, 0, 0),
            (0.45, 0.9375, 0.9375),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 1, 1),
            (0.9375, 1, 1),
            (1, 1, 1),
        ],
        "green": [
            (0, 0.1875, 0.1875),
            (0.0625, 0.375, 0.375),
            (0.125, 0.5625, 0.5625),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 0.75, 0.75),
            (0.9375, 0.5625, 0.5625),
            (1, 0.375, 0.375),
        ],
        "blue": [
            (0, 1, 1),
            (0.0625, 1, 1),
            (0.125, 1, 1),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 0.9375, 0.9375),
            (0.875, 0, 0),
            (0.9375, 0, 0),
            (1, 0, 0),
        ],
        "alpha": [
            (0, 0.5, 0.5),
            (0.25, 0.5, 0.5),
            (0.5, 0.2, 0.2),
            (0.75, 0.5, 0.5),
            (1, 0.5, 0.5),
        ],
    }

    return colors.LinearSegmentedColormap(
        "blue_white_orange_semitransparent",
        blue_white_orange_semitransparent_dict
    )


def blue_white_orange_opaque_colormap() -> colors.Colormap:
    """Create a blue-white-orange colormap, all opaque

    Colors are evenly spaced: blue at 0, white at 0.5, orange at 1.
    All opaque.  This gets confused when lots of lines pile up
    but is better for reading sparese traffic.

    No arguments.

    Returns:
        mpl.colors.Colormap: Blue->white->orange
    """

    blue_white_orange_opaque_dict: SegmentedColormap = {
        "red": [
            (0, 0, 0),
            (0.0625, 0, 0),
            (0.125, 0, 0),
            (0.45, 0.9375, 0.9375),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 1, 1),
            (0.9375, 1, 1),
            (1, 1, 1),
        ],
        "green": [
            (0, 0.1875, 0.1875),
            (0.0625, 0.375, 0.375),
            (0.125, 0.5625, 0.5625),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 0.75, 0.75),
            (0.9375, 0.5625, 0.5625),
            (1, 0.375, 0.375),
        ],
        "blue": [
            (0, 1, 1),
            (0.0625, 1, 1),
            (0.125, 1, 1),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 0.9375, 0.9375),
            (0.875, 0, 0),
            (0.9375, 0, 0),
            (1, 0, 0),
        ],
        "alpha": [(0, 1, 1), (0.25, 1, 1), (0.5, 1, 1), (0.75, 1, 1), (1, 1, 1)],
    }
    return colors.LinearSegmentedColormap(
        "blue_white_orange_opaque",
        blue_white_orange_opaque_dict
    )


def blue_white_orange_brighter_colormap() -> colors.Colormap:
    """Create a blue-white-orange colormap, very bright

    Colors are evenly spaced: blue at 0, white at 0.5, orange at 1.
    Colors are brighter (closer to white).  Good for images being
    shown on dim or low-contrast screens.

    No arguments.

    Returns:
        mpl.colors.Colormap: Blue->white->orange
    """

    blue_white_orange_brighter_dict: SegmentedColormap = {
        "red": [
            (0, 0.1, 0.1),
            (0.0625, 0.1, 0.1),
            (0.125, 0.1, 0.1),
            (0.45, 0.9375, 0.9375),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 1, 1),
            (0.9375, 1, 1),
            (1, 1, 1),
        ],
        "green": [
            (0, 0.2875, 0.2875),
            (0.0625, 0.475, 0.475),
            (0.125, 0.5625, 0.5625),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 0.75, 0.75),
            (0.9375, 0.5625, 0.5625),
            (1, 0.375, 0.375),
        ],
        "blue": [
            (0, 1, 1),
            (0.0625, 1, 1),
            (0.125, 1, 1),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 0.9375, 0.9375),
            (0.875, 0, 0),
            (0.9375, 0, 0),
            (1, 0, 0),
        ],
        "alpha": [(0, 1, 1), (0.25, 1, 1), (0.5, 0.5, 0.5), (0.75, 1, 1), (1, 1, 1)],
    }

    return colors.LinearSegmentedColormap(
        "blue_white_orange_brighter",
        blue_white_orange_brighter_dict
    )


def blue_white_orange_invisible_middle_colormap() -> colors.Colormap:
    """Create a blue-white-orange colormap, middle is invisible

    Colors are evenly spaced: blue at 0, white at 0.5, orange at 1.
    The middle of the colormap is completely invisible.  Good for
    just showing the low and high ends of the color space.

    No arguments.

    Returns:
        mpl.colors.Colormap: Blue->white->orange
    """

    blue_white_orange_invisible_middle_dict: SegmentedColormap = {
        "red": [
            (0, 0.1, 0.1),
            (0.0625, 0.1, 0.1),
            (0.125, 0.1, 0.1),
            (0.45, 0.9375, 0.9375),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 1, 1),
            (0.9375, 1, 1),
            (1, 1, 1),
        ],
        "green": [
            (0, 0.2875, 0.2875),
            (0.0625, 0.475, 0.475),
            (0.125, 0.5625, 0.5625),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 1, 1),
            (0.875, 0.75, 0.75),
            (0.9375, 0.5625, 0.5625),
            (1, 0.375, 0.375),
        ],
        "blue": [
            (0, 1, 1),
            (0.0625, 1, 1),
            (0.125, 1, 1),
            (0.45, 1, 1),
            (0.5, 1, 1),
            (0.55, 0.9375, 0.9375),
            (0.875, 0, 0),
            (0.9375, 0, 0),
            (1, 0, 0),
        ],
        "alpha": [(0, 1, 1), (0.25, 1, 1), (0.5, 0.1, 0.1), (0.75, 1, 1), (1, 1, 1)],
    }

    return colors.LinearSegmentedColormap(
        "blue_white_orange_invisible_middle",
        blue_white_orange_invisible_middle_dict
    )


def all_white_colormap() -> colors.Colormap:
    """Return an all-white color map

    All white, all the time.

    No arguments.

    Returns:
        mpl.colors.Colormap: White from beginning to end
    """


    all_white_dict: SegmentedColormap = {
        "red": [(0, 1, 1), (1, 1, 1)],
        "green": [(0, 1, 1), (1, 1, 1)],
        "blue": [(0, 1, 1), (1, 1, 1)],
    }
    return colors.LinearSegmentedColormap("all_white", all_white_dict)


def all_grey50_colormap() -> colors.Colormap:
    """Return an all-50%-grey

    All grey, all the time.

    No arguments.

    Returns:
        mpl.colors.Colormap: 50% grey from beginning to end
    """

    all_grey50_dict: SegmentedColormap = {
        "red": [(0, 0.5, 0.5), (1, 0.5, 0.5)],
        "green": [(0, 0.5, 0.5), (1, 0.5, 0.5)],
        "blue": [(0, 0.5, 0.5), (1, 0.5, 0.5)],
    }

    return colors.LinearSegmentedColormap("all_grey50", all_grey50_dict)


def all_yellow_colormap() -> colors.Colormap:
    """All yellow, all the time

    No arguments.

    Returns:
        mpl.colors.Colormap: Colormap that's always yellow
    """

    return colors.LinearSegmentedColormap.from_list("all_yellow",
                                                    ["#FFCC00", "#FFCC00"])


def yellow_orange_colormap() -> colors.Colormap:
    """Gradient from yellow to orange

    No arguments.

    Returns:
        mpl.colors.Colormap: Colormap that's yellow at the start, shading to orange
    """

    return colors.LinearSegmentedColormap.from_list(
        "yellow_orange",
        ["#FFCC00", "#FF9900", "#FF6600"])


def orange_yellow_colormap() -> colors.Colormap:
    """Gradient from orange to yellow

    No arguments.

    Returns:
        mpl.colors.Colormap: Colormap that's orange at the start, shading to yellow
    """

    return colors.LinearSegmentedColormap.from_list(
        "orange_yellow",
        ["#FF6600", "#FF9900", "#FFCC00"])


def turquoise_blue_colormap() -> colors.Colormap:
    """Gradient from turquoise to blue

    No arguments.

    Returns:
        mpl.colors.Colormap: Colormap that's turquoise at the start, blue at the end
    """

    return colors.LinearSegmentedColormap.from_list(
        "turquoise_blue",
        ["#0099FF", "#0066FF", "#0033FF"])


def blue_turquoise_colormap() -> colors.Colormap:
    """Gradient from blue to turquoise

    No arguments.

    Returns:
        mpl.colors.Colormap: Colormap that's blue at the start, turquoise at the end
    """

    return colors.LinearSegmentedColormap.from_list(
        "blue_turquoise",
        ["#0033FF", "#0066FF", "#0099FF"])


def dark_to_light_grey_colormap() -> colors.Colormap:
    """Gradient from dark to light grey

    No arguments.

    Returns:
        mpl.colors.Colormap: Colormap that's dark grey at the start, light grey at the end
    """

    return colors.LinearSegmentedColormap.from_list(
        "dark_to_light_grey",
        ["#666666", "#999999", "#CCCCCC"]
    )


def light_to_dark_grey_colormap() -> colors.Colormap:
    """Gradient from light to dark grey

    No arguments.

    Returns:
        mpl.colors.Colormap: Colormap that's light grey at the start, dark grey at the end
    """

    return colors.LinearSegmentedColormap.from_list(
        "light_to_dark_grey",
        ["#CCCCCC", "#999999", "#666666"]
    )



### DO NOT REMOVE THIS CALL
register_colormaps()