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

"""Options for parallel movie rendering.

This argument group allows you to set the number of processes and
(eventually) maximum memory that you're willing to use when rendering
movies in parallel.

Arguments:

| ``--processors NUMBER``
|   How many processes to spawn.  The default value (0) means 'one process per detected core on the system'.
"""


from tracktable.script_helpers.argument_groups import create_argument_group, add_argument

GROUP_INSTALLED = False

def install_group():
    """Standard method - define the Parallel Movie Rendering argument group"""

    global GROUP_INSTALLED
    if not GROUP_INSTALLED:
        GROUP_INSTALLED = True

        create_argument_group("parallel",
                              title="Multiprocess Parallelism",
                              description="Set the number of processes and (eventually) maximum memory that you want to use when running jobs in parallel.")
        add_argument("parallel",
                     [ "--processors" ],
                     type=int,
                     default=0,
                     help="How many processes to spawn.  The default value (0) means 'one process for each detected core on the system'.")

