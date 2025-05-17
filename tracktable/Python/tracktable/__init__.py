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

"""Tracktable Trajectory Library - Top-level module

Welcome to Tracktable!

UNITS:

All user-facing functions will measure angles in degrees and distances
in kilometers.

"""

# \defgroup Tracktable_Python Python components of Tracktable

import os
__version__ = "1.7.2"
__title__ = "Tracktable"
__description__ = "Trajectory Analysis and Visualization"
__url__ = "https://tracktable.sandia.gov"
__uri__ = __url__
__doc__ = __description__ + " <" + __uri__ + ">"
__author__ = "Andy Wilson, Danny Rintoul, Chris Valicka, Ben Newton, Paul Schrum, Phil Baxley, Kat Ward, Rick Vinyard, Michael Scoggin, Michael Fadem, Geoff Danielson"
__maintainer__ = "Andy Wilson"
__license__ = "BSD"
__copyright__ = "Copyright (c) 2014-2023 National Technology and Engineering Solutions of Sandia, LLC."


# We need to verify that Tracktable can import the compiled objects from
# the ``lib`` module when it is first imported to verify that the
# installation is functional.
FAILURE_COUNT = 0

try:
  from tracktable.lib import _c_python
except Exception as e:
  FAILURE_COUNT += 1
  print("Error importing C Python extension example. Original exception error text: {}".format(e))

try:
  from tracktable.lib import _tracktable_hello
except Exception as e:
  FAILURE_COUNT += 1
  print("Error importing Boost.Python example. Original exception error text: {}".format(e))

try:
  from tracktable.lib import _boost_libs
except Exception as e:
  FAILURE_COUNT += 1
  print("Error importing core Boost libraries. Original exception error text: {}".format(e))

try:
  from tracktable.lib import _core_types
except Exception as e:
  FAILURE_COUNT += 1
  print("Error importing Tracktable's core types library. Original exception error text: {}".format(e))


# We got failures so we need to give the user some useful information
if FAILURE_COUNT > 0:
  import os
  import sys
  import pprint
  import platform

  if FAILURE_COUNT == 1:
    print("\nThere was {} failure when attempting to import Tracktable!\n".format(FAILURE_COUNT))
  else:
    print("\nThere were {} failures when attempting to import Tracktable!\n".format(FAILURE_COUNT))

  print("Typically these failures are caused when the Python interpreter can't find shared libraries required by Tracktable",
      "such as Boost or Tracktable's compiled libraries. \nVerify that the system and/or Python path contains references to",
      "Boost and Tracktable's compiled libraries.")

  if platform.system() == "Windows":
    print("\nAlong with verifying the system and/or Python path, ensure that Microsoft's C++ runtime library is installed.")
  if platform.system() == "Darwin":
    print("\nIf not using one of Tracktable's included Anaconda environment files, ensure that the version of the ICU library matches the",
          "version specified in the the Tracktable documentation.")

  print("\nAdditional troubleshooting steps can be found in the Tracktable documentation: https://tracktable.readthedocs.io/en/latest/common_errors.html#shared-library-errors")

  print("\nDiagnostic Path Information:")
  print("----------------------------")
  print("Python path:")
  pprint.pprint(sys.path)
  print("\nSystem path:")
  pprint.pprint(os.environ["PATH"].split(os.pathsep))

  # No real reason to include the traceback since this exception
  # is raised at the top of tracktable
  if sys.version_info[1] < 7:
    sys.tracebacklimit = None
  else:
    sys.tracebacklimit = 0

  # In order to prevent the user from being able to just `import tracktable` a
  # second time without the above errors we need to throw an exception
  print("\n")
  raise ImportError("Error importing Tracktable, see debug messages above.")

else:
  # We always start out with the log level set to INFO.
  # You can set it lower in your own code if you want.
  import logging
  import tracktable.core.log
  tracktable.core.log.set_log_level(logging.INFO)
