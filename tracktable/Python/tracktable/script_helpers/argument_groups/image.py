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

"""Arguments for image generation.

Use this group as follows::

   from tracktable.script_helpers import argument_groups, argparse
   my_parser = argparse.ArgumentParser()
   argument_groups.use_group('image', my_parser)

Arguments:

| ``--dpi NUMBER``
| Dots per inch for the image.  This determines font height and line width in pixels.
|
| ``--resolution XRES YRES``
| Image resolution.  This can be almost arbitrarily large subject to your computer's memory limits.

"""


from tracktable.script_helpers.argument_groups import create_argument_group, add_argument

GROUP_INSTALLED = False

def install_group():
    """Create the argument group for image parameters.

    This function is called automatically when the argument_groups
    module is loaded.

    """

    global GROUP_INSTALLED
    if GROUP_INSTALLED:
        return
    else:
        GROUP_INSTALLED = True

    create_argument_group("image",
                          title="Images",
                          description="Parameters for image size and resolution")

    add_argument("image", [ '--dpi' ],
                 nargs=1,
                 type=int,
                 default=72,
                 help='Dots per inch (DPI) for image.  This determines font height and line width.')

    add_argument("image", [ '--resolution' ],
                 nargs=2,
                 type=int,
                 default=[800,600],
                 help='Image resolution in pixels.')
