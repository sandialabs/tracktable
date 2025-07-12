#
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

"""Test whether folium_proxy falls back successfully to Folium"""

import sys

from tracktable.render.backends import folium_proxy


# ----------------------------------------------------------------------


def test_folium_fallback_import_toplevel() -> int:
    """Make sure we get Folium when we ask for it."""

    folium_proxy.set_folium_proxy_name("__no_such_module__")
    my_folium = folium_proxy.import_folium()

    if my_folium.__name__ == "folium":
        return 0
    return 1


# ----------------------------------------------------------------------

def test_folium_fallback_import_submodule() -> int:
    """Try to import a sub-module from regular Folium."""

    folium_proxy.set_folium_proxy_name("__no_such_module__")
    my_submodule = folium_proxy.import_folium("plugins.heat_map")

    if my_submodule.__name__ == "folium.plugins.heat_map":
        return 0
    return 1


# ----------------------------------------------------------------------

def main():
    result = (
        test_folium_fallback_import_toplevel() +
        test_folium_fallback_import_submodule()
    )
    return result

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
