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

"""Projector classes for Tracktable

Here we define projections from 2D and 3D back down to 2D.  We will
import these into domains as appropriate.
"""

def make_projection_cartesian2d():
    return ( Projection2DCartesian(), list() )

class Projection2DCartesian(object):
    """Project from 2D space to 2D space.

    The initial implementation of this class will be trivial.  We'll
    allow matplotlib's Axes class to take care of moving things about.
    We can add more complexity as it's needed.
    """

    def __init__(self):
        pass

    def __call__(self, x_list, y_list):
        """Map points from world space into projected space.

        In order to project points down into 2D, call this object like
        a function.  Pass it two lists, one of X coordinates and one
        of Y coordinates.  You will get back two lists of projected
        coordinates.
        """

        return (x_list, y_list)
