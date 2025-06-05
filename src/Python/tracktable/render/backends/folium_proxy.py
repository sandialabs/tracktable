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
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""Folium proxy: import offlinefolium if available

When on high-side or air-gapped networks, it is convenient to have a
version of Folium that includes all of its necessary Javascript
resources inline instead of reaching out to the open Internet for
them.  We typically install a package `offlinefolium` that does that.

This module does the following:

1. Provide a wrapper (import()) that imports `offlinefolium` if available;
   `folium` otherwise.

2. Allow the user to change `offlinefolium` to some other module name.

3. Allow the user to enable/disable this mechanism.

Functions:
   - folium_proxy_name() - Get the name of the offline Folium package
   - set_folium_proxy_name() - Set the name of the offline Folium package
   - folium_proxy_enabled() - Get whether or not preferential import of
     `offlinefolium` is enabled
   - set_folium_proxy_enabled() - Set whether or not to preferentially
     import `offlinefolium`
   - import_folium() - Import either `offlinefolium` or `folium`, whichever
     is found first, or some subpackage
"""

import importlib
import logging
import types

from typing import Optional

LOG = logging.getLogger(__name__)

__all__ = [
    "folium_proxy_name",
    "set_folium_proxy_name",
    "folium_proxy_enabled",
    "set_folium_proxy_enabled",
    "import_folium"
]

# This is the module that we will try to import first.
FOLIUM_PROXY_NAME: str = "offlinefolium"

# We will try that if and only if this is True.
FOLIUM_PROXY_ENABLED: bool = True

# This will be set to the name of whatever Folium module we have
# imported.  Used as a guard in case the user tries to switch
# mid-stream.
ACTIVE_FOLIUM_NAME: Optional[str] = None


def folium_proxy_name() -> str:
    """Get the name of the Folium proxy module

    This is the name of the module that we will try to import whenever
    Folium is requested.  Defaults to "offlinefolium".  Change with
    set_folium_proxy_name().

    No arguments.

    Returns:
        Name of module as string
    """
    return FOLIUM_PROXY_NAME


def set_folium_proxy_name(package_name: str) -> None:
    """Set the name of the Folium proxy module

    Change the name of the module that we will try to import whenever
    Folium is requested.

    Arguments:
        package_name (str): Name of module to try to import instead of
            Folium

    Returns:
        None
    """

    global FOLIUM_PROXY_NAME

    if (ACTIVE_FOLIUM_NAME is not None
        and package_name != FOLIUM_PROXY_NAME
        and ACTIVE_FOLIUM_NAME == FOLIUM_PROXY_NAME):
        LOG.warning((
            "Folium proxy package is being changed from '%s' to '%s' after "
            "proxy package has already been imported.  This may cause "
            "problems with maps rendered hereafter."
        ))

    if package_name != FOLIUM_PROXY_NAME:
        LOG.info("Folium proxy package name changed to '%s'.",
                 package_name)
        FOLIUM_PROXY_NAME = package_name


def folium_proxy_enabled() -> bool:
    """Is the Folium proxy module enabled?

    If True (the default), we will try to import the module
    named in folium_proxy_module() first, then fall back to
    importing `folium`.

    No arguments.

    Returns:
        bool: Whether or not preferential import is enabled
    """
    return FOLIUM_PROXY_ENABLED


def set_folium_proxy_enabled(enabled: bool) -> None:
    """Enable or disable preferential import of offlinefolium

    If True, we will try to import the proxy module first, then
    fall back to `folium` if it is not found.  If False, we will
    only try to import `folium`.

    Arguments:
        enabled (bool): Whether to do preferential import

    Returns:
        None
    """

    global FOLIUM_PROXY_ENABLED

    if ACTIVE_FOLIUM_NAME is not None:
        LOG.warning((
            "Preferential import for the Folium proxy is being changed "
            "after Folium has already been imported.  This may cause "
            "problems with maps rendered hereafter."
        ))

    if enabled != FOLIUM_PROXY_ENABLED:
        if enabled:
            LOG.info("Folium module preferential import enabled.")
        else:
            LOG.info("Folium proxy module preferential import disabled.")
        FOLIUM_PROXY_ENABLED = enabled


def import_folium(subpackage: Optional[str] = None) -> types.ModuleType:
    """Import Folium or some subpackage

    This function will try to import `offlinefolium` or whatever
    package was specified with `set_folium_proxy_name()`.  If that
    fails, it will try to import `folium`.  Use as follows:

    Instead of `import folium`:
    >>> folium = import_folium()

    Instead of `from folium.plugins import heat_map`:
    >>> heat_map = import_folium("plugins.heat_map")

    Note that you can only import a module or package.  To access
    members of the module such as folium.plugins.heat_map.HeatMap,
    use the following:

    >>> heat_map_module = import_folium("plugins.heat_map")
    >>> HeatMap = heat_map_module.HeatMap

    This function will print a log message at level INFO when we
    successfully import the proxy module instead of regular
    Folium.  It will also print a log message at level WARNING
    if we get a different module than the one that was already
    imported.

    Keyword Arguments:
        subpackage (str): Sub-package of Folium to import.
            To get "folium.plugins.heat_map", specify
            "plugins.heat_map".

    Returns:
        Imported module.

    Raises:
        ImportError: Neither the proxy module nor `folium` could
        be imported
    """

    global ACTIVE_FOLIUM_NAME

    proxy_name = folium_proxy_name()

    if subpackage is not None:
        full_proxy_package_name = f"{proxy_name}.{subpackage}"
        full_fallback_package_name = f"folium.{subpackage}"
    else:
        full_proxy_package_name = proxy_name
        full_fallback_package_name = "folium"

    folium_package = None
    if folium_proxy_enabled():
        try:
            folium_package = importlib.import_module(full_proxy_package_name)
        except ImportError:
            pass
    if folium_package is None:
        folium_package = importlib.import_module(full_fallback_package_name)

    imported_package_name = _package_name_respecting_proxy(folium_package)

    if ACTIVE_FOLIUM_NAME is None:
        if imported_package_name != "folium":
            LOG.info("Imported '%s' as a proxy for Folium.", imported_package_name)
    else:
        if ACTIVE_FOLIUM_NAME != imported_package_name:
            LOG.warning((
                "Active Folium package changed from %s to %s.  This "
                "may cause instability with subsequently rendered maps."),
                ACTIVE_FOLIUM_NAME, imported_package_name)

    ACTIVE_FOLIUM_NAME = imported_package_name
    return folium_package


def _package_name_respecting_proxy(package: types.ModuleType) -> str:
    """Get base name of imported package

    If the package imported was just plain Folium, this will be
    'folium'.  If it was the proxy, it will be 'offlinefolium' or
    'my_offline_packages.folium' or whatever you specified as
    FOLIUM_PROXY_NAME.

    Arguments:
        package: Module whose name we want

    Returns:
        Name of package
    """

    if package.__name__.startswith(folium_proxy_name()):
        return folium_proxy_name()
    return package.__name__.split('.')[0]
