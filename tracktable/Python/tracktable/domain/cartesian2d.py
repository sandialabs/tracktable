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


from tracktable.lib._cartesian2d import BasePointCartesian2D as BasePoint
from tracktable.lib._cartesian2d import TrajectoryPointCartesian2D as TrajectoryPoint
from tracktable.lib._cartesian2d import TrajectoryCartesian2D as Trajectory
from tracktable.lib._cartesian2d import BasePointReaderCartesian2D as BasePointReader
from tracktable.lib._cartesian2d import TrajectoryPointReaderCartesian2D as TrajectoryPointReader
from tracktable.lib._cartesian2d import BoundingBoxCartesian2D as BoundingBox
from tracktable.lib._cartesian2d import TrajectoryReaderCartesian2D as TrajectoryReader
from tracktable.lib._cartesian2d import BasePointWriterCartesian2D as BasePointWriter
from tracktable.lib._cartesian2d import TrajectoryPointWriterCartesian2D as TrajectoryPointWriter
from tracktable.lib._cartesian2d import TrajectoryWriterCartesian2D
DIMENSION = 2

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
    'TrajectoryWriter': TrajectoryWriterCartesian2D
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
        TrajectoryWriterCartesian2D,
        BoundingBox ]:
    domain_class.domain_classes = domain_classes
    domain_class.DOMAIN = "cartesian2d"

def identity_projection(*coord_lists):
    return coord_lists
    
class TrajectoryWriter:
    def __init__(self, output):
        self.writer = TrajectoryWriterCartesian2D(output)
    
    def write(self, trajectories):
        if isinstance(trajectories, list):
            self.writer.write(trajectories)
        else:
            self.writer.write([trajectories])