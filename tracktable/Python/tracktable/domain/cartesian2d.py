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


from ._cartesian2d import BasePointCartesian2D as BasePoint
from ._cartesian2d import TrajectoryPointCartesian2D as TrajectoryPoint
from ._cartesian2d import TrajectoryCartesian2D as Trajectory
from ._cartesian2d import BasePointReaderCartesian2D as BasePointReader
from ._cartesian2d import TrajectoryPointReaderCartesian2D as TrajectoryPointReader
from ._cartesian2d import BoundingBoxCartesian2D as BoundingBox
from ._cartesian2d import TrajectoryReaderCartesian2D as TrajectoryReader
from ._cartesian2d import BasePointWriterCartesian2D as BasePointWriter
from ._cartesian2d import TrajectoryPointWriterCartesian2D as TrajectoryPointWriter
from ._cartesian2d import TrajectoryWriterCartesian2D as TrajectoryWriter

domain_classes = {
    'BasePoint': BasePoint,
    'TrajectoryPoint': TrajectoryPoint,
    'BasePointReader': BasePointReader,
    'TrajectoryPointReader': TrajectoryPointReader,
    'TrajectoryReader': TrajectoryReader,
    'Trajectory': Trajectory,
    'BoundingBox': BoundingBox,
    'BasePointWriter': BasePointWriter,
    'TrajectoryPointWriter': TrajectoryPointWriter,
    'TrajectoryWriter': TrajectoryWriter
}


for domain_class in [
        BasePoint,
        TrajectoryPoint,
        Trajectory,
        BasePointReader,
        TrajectoryPointReader,
        TrajectoryReader,
        BasePointWriter,
        TrajectoryPointWriter,
        TrajectoryWriter,
        BoundingBox ]:
    domain_class.domain_classes = domain_classes


def identity_projection(*coord_lists):
    return coord_lists
