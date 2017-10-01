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

"""Options for rendering trajectories onto a map.

Arguments:

| ``--trajectory-color-type ["scalar", "constant"]``
|     Whether to use a function (scalar) or constant color for trajectories
|
| ``--trajectory-color-function NAME``
|     Function to generate trajectory color.  Default is 'progress', a function that is 0 at the beginning of a trajectory and 1 at its end.  Requires ``--trajectory-color-type scalar``.
|
| ``--trajectory-color COLOR``
|     Constant color for trajectories.  Requires ``--trajectory-color-type constant``.
|
| ``--trajectory-colormap NAME``
|     Colormap to use to color trajectories. Use one of the Matplotlib standard colormaps or one of Tracktable's color maps from tracktable.render.colormaps.
|
| ``--trajectory-zorder NUMBER``
|     Layer number for trajectories. Higher-numbered layers are rendered on top of lower-numbered ones.
|
| ``--decorate-trajectory-head``
|     Draw a dot at the head of each trajectory.
|
| ``--trajectory-head-color COLOR``
|     Color (name or hex string) for the dot at the head of the trajectory.  Requires '--decorate-trajectory-head'.  You can also specify 'body' to use the same color as the first segment of the trajectory.
|
| ``--trajectory-head-dot-size NUMBER``
|     Size (in points) of the dot to render at the head of each trajectory.  Requires ``--decorate-trajectory-head``.
|
| ``--trajectory-linewidth NUMBER``
|     Trajectory linewidth in points.  You can also specify 'taper', in which case trajectory linewidth will start at the value of ``--trajectory-initial-linewidth`` and end at ``--trajectory-final-linewidth``.
|
| ``--trajectory-initial-linewidth NUMBER``
|     Width (in points) at the head of the trajectory.  Requires ``--trajectory-linewidth taper``.
|
| ``--trajectory-final-linewidth NUMBER``
|     Width (in points) at the end of the trajectory.  Requires ``--trajectory-linewidth taper``.
|
| ``--scalar-min NUMBER``
|     Scalar value to map to bottom of color map. Requires ``--trajectory-color-type scalar``.
|
| ``--scalar-max NUMBER``
|     Scalar value to map to top of color map. Requires ``--trajectory-color-type scalar``.
"""

from tracktable.script_helpers.argument_groups import create_argument_group, add_argument
from tracktable.feature import annotations

GROUP_INSTALLED = False

def install_group():
    """Standard method - define the Trajectory Rendering argument group"""

    global GROUP_INSTALLED
    if GROUP_INSTALLED:
        return
    else:
        GROUP_INSTALLED = True

    create_argument_group("trajectory_rendering",
                          title="Trajectory Appearance",
                          description="Parameters for trajectory color, linewidth and decoration")

    add_argument("trajectory_rendering", [ "--trajectory-color-type" ],
                 default="scalar",
                 choices=[ "scalar", "constant" ],
                 help="Whether to use a function or a constant to color trajectories")

    add_argument("trajectory_rendering", [ "--trajectory-color", "--trajectory-color-function" ],
                 default="progress",
                 help="Trajectory color.  This must be the name of a color or a hex string if --trajectory-color-type is 'constant' and the name of a function (options are {}) if --trajectory-color-type is 'scalar'.".format(annotations.available_annotations()))

    add_argument("trajectory_rendering", [ "--trajectory-colormap" ],
                 default="gist_heat",
                 help="Colormap to use to color trajectories.  Use one of the Matplotlib standard colormaps or one of Tracktable's color maps from tracktable.render.colormaps.")

    add_argument("trajectory_rendering", [ "--trajectory-zorder" ],
                 default=10,
                 type=int,
                 help="Z-order (layer) for rendered trajectories")

    add_argument("trajectory_rendering", [ "--decorate-trajectory-head" ],
                 action='store_true',
                 help="If set, draw a dot at the head of each trajectory")

    add_argument("trajectory_rendering", [ "--trajectory-head-dot-size" ],
                 type=int,
                 default=2,
                 help="Size (in points) of dot to render at the head of each trajectory.  Requires --decorate-trajectory-head.")

    add_argument("trajectory_rendering", [ "--trajectory-head-color" ],
                 default="white",
                 help="Color name for trajectory color.  You can also specify 'body' to use the same color as the first segment of the trajectory.")

    add_argument("trajectory_rendering", [ "--trajectory-linewidth" ],
                 default=0.5,
                 help="Trajectory linewidth in points.  You can also specify 'taper', in which case trajectory linewidth will start at the value of '--trajectory-initial-linewidth' and end at '--trajectory-final-linewidth'.")

    add_argument("trajectory_rendering", [ "--trajectory-initial-linewidth" ],
                 default=0.5,
                 type=float,
                 help="Initial trajectory linewidth in points.  Requires '--trajectory-linewidth taper'.")

    add_argument("trajectory_rendering", [ "--trajectory-final-linewidth" ],
                 default=0.01,
                 type=float,
                 help="Final trajectory linewidth in points.  Requires '--trajectory-linewidth taper'.")

    add_argument("trajectory_rendering", [ "--scalar-min" ],
                 default=0,
                 type=float,
                 help="Scalar value to map to bottom of colormap.  Requires '--trajectory-color-type scalar'.")

    add_argument("trajectory_rendering", [ "--scalar-max" ],
                 default=1,
                 type=float,
                 help="Scalar value to map to top of colormap.  Requires '--trajectory-color-type scalar'.")
