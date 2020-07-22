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

"""Tracktable Trajectory Library - Top-level module

Welcome to Tracktable!

UNITS:

All user-facing functions will measure angles in degrees and distances
in kilometers.

"""

# \defgroup Tracktable_Python Python components of Tracktable

__version__ = "1.3.1"
__title__ = "Tracktable"
__description__ = "Trajectory Analysis and Visualization"
__url__ = "https://tracktable.sandia.gov"
__uri__ = __url__
__doc__ = __description__ + " <" + __uri__ + ">"
__author__ = "Andy Wilson, Danny Rintoul, Chris Valicka, Ben Newton, Paul Schrum, Phil Baxley, Kat Ward, Rick Vinyard"
__maintainer__ = "Andy Wilson"
__license__ = "BSD"
__copyright__ = "Copyright (c) 2014-2020 National Technology and Engineering Solutions of Sandia, LLC."


from .core import register_core_types

# We always start out with the log level set to INFO.
# You can set it lower in your own code if you want.
import logging
import tracktable.core.log
tracktable.core.log.set_log_level(logging.INFO)