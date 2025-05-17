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

"""Test whether folium_proxy finds the module it's pointed to"""

import sys
import types

from tracktable.render.backends import folium_proxy

def _module_has_member(module: types.ModuleType, member: str) -> bool:
    """Does a module contain some member?

    Arguments:
        module (imported module): Module to chechk
        member (str): Name of member to look for

    Returns:
        True if member present, False if not
    """

    try:
        _ = getattr(module, member)
        print(f"Module {module.__name__} has member {member}")
        return True
    except AttributeError:
        print(f"Module {module.__name__} does not have member {member}")
        return False


# ----------------------------------------------------------------------

def test_folium_proxy_import_dotted_package() -> int:
    """Try to import a package whose name contains a dot."""

    folium_proxy.set_folium_proxy_name("logging.config")
    my_logging_config = folium_proxy.import_folium()

    if (_module_has_member(my_logging_config, "dictConfig")
        and folium_proxy.ACTIVE_FOLIUM_NAME == "logging.config"):
        return 0
    return 1


# ----------------------------------------------------------------------

def main():
    return test_folium_proxy_import_dotted_package()

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
