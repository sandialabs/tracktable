#
# Copyright (c) 2014-2020 National Technology and Engineering
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

"""
tracktable.source - Point/trajectory sources for Tracktable trajectories

This module contains Sources.  A Source is an object that produces
points or trajectories.  These can come from anywhere else, whether
loaded from a file, extracted from a database or created
algorithmically.
"""

# TODO (mjfadem): Remove this file in release 1.6

import warnings
import sys

import tracktable.analysis
import tracktable.analysis.assemble_trajectories

import tracktable.data_generators
import tracktable.data_generators.point

import tracktable.feature
import tracktable.feature.interleave_points
import tracktable.feature.interpolated_points

# This just stops the source line from printing with the warning
def format_warning(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s:%s\n' % (filename, lineno, category.__name__, message)

warnings.formatwarning = format_warning

# Allow the PendingDeprecationWarning through since it's disabled by default
warnings.simplefilter("always", category=PendingDeprecationWarning)

# This will display a PendingDeprecationWarning when the source modules are imported
warnings.warn(" \nThe tracktable.source submodules have been relocated to more appropriate locations listed below and tracktable.source will be fully removed in release 1.6.\n"
        "\ttracktable.source.combine            -> tracktable.feature.interleave_points\n"
        "\ttracktable.source.path_point_source  -> tracktable.feature.interpolated_points\n"
        "\ttracktable.source.point              -> tracktable.data_generators.point\n"
        "\ttracktable.source.trajectory         -> tracktable.analysis.assemble_trajectories\n", category=PendingDeprecationWarning)

# Aliases to smooth the transition of relocation of tracktable.source modules
sys.modules['tracktable.source.combine'] = tracktable.feature.interleave_points
sys.modules['tracktable.source.path_point_source'] = tracktable.feature.interpolated_points
sys.modules['tracktable.source.point'] = tracktable.data_generators.point
sys.modules['tracktable.source.trajectory'] = tracktable.analysis.assemble_trajectories