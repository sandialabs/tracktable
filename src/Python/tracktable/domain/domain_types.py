# Copyright (c) 2014-2025 National Technology and Engineering
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

"""Types for trajectories and trajectory points"""

from typing import TypeAlias, Union

import tracktable.domain.terrestrial as terrestrial
import tracktable.domain.cartesian2d as cartesian2d
import tracktable.domain.cartesian3d as cartesian3d

# Should I define protocols PointLike and TrajectoryLike?

__all__ = ["BasePoint", "Trajectory", "TrajectoryPoint"]


BasePoint: TypeAlias = Union[
    terrestrial.BasePoint,
    cartesian2d.BasePoint,
    cartesian3d.BasePoint
]

TrajectoryPoint: TypeAlias = Union[
    terrestrial.TrajectoryPoint,
    cartesian2d.TrajectoryPoint,
    cartesian3d.TrajectoryPoint
]

Trajectory: TypeAlias = Union[
    terrestrial.Trajectory,
    cartesian2d.Trajectory,
    cartesian3d.Trajectory
]

