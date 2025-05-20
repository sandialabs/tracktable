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

"""Convenience wrappers for geographic map creation and decoration
"""

import warnings

from tracktable.render.render_map import render_map

def mapmaker(domain='terrestrial', *args, **kwargs):
    """Generate a map for a given domain. Wrapper of render_map for deprecation purposes.

    Keyword Args:
        domain (str): Domain to create the map in (Default: 'terrestrial')
        args (tuple): Arguments to be passed to specific map creation (Default: tuple)
        kwargs (dict): Any other arguments to customize the generated map (Default: dict)

    Returns:
        A terrestrial or cartesian domain map

    """

    # This just stops the source line from printing with the warning
    def format_warning(message, category, filename, lineno, file=None, line=None):
        return '%s:%s: %s:%s\n' % (filename, lineno, category.__name__, message)

    warnings.formatwarning = format_warning

    # Allow the DeprecationWarning through
    warnings.simplefilter("always", category=DeprecationWarning)

    # This will display a DeprecationWarning when the function is called
    warnings.warn(" \nThe tracktable.render.mapmaker mapmaker() function has been deprecated and will be fully removed in release 1.8."
                  " Please use the tracktable.render.render_map render_map() function.\n", category=DeprecationWarning)

    # Aliases to smooth the transition of relocation of the function(s)/module(s)
    return render_map(domain, *args, **kwargs)
