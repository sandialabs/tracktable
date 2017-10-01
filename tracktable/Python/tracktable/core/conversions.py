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

"""
Unit conversions
"""

# ----------------------------------------------------------------------

def m_per_sec_to_mi_per_hr(mps):
    """Convert speed: meters/sec -> miles/hour

    Args:
       mps (float): Speed in meters per second

    Returns:
       Speed in miles per hour
    """

    return mps * (3600.0) * (39.37 / 12) / (5280.0)

# ----------------------------------------------------------------------

def m_per_sec_to_km_per_hr(mps):
    """Convert speed: meters/sec -> km/hour

    Args:
       mps (float): Speed in meters per second

    Returns:
       Speed in kilometers per hour
    """

    return mps * (3600.0 / 1000.0)

# ----------------------------------------------------------------------

def m_per_sec_to_nm_per_hr(mps):
    """Convert meters per second to nautical miles per hour (knots)

    Args:
       mps (float): Speed in meters per second

    Returns:
       Speed in nautical miles per hour
    """

    return m_per_sec_to_mi_per_hr(mps)/ 1.15

# ----------------------------------------------------------------------

def meters_to_miles(meters):
    """Convert meters to statute miles

    Args:
       meters (float): Distance in meters

    Returns:
       Distance in miles
    """

    return m * (39.37 / 12) / 5280

# ----------------------------------------------------------------------

def miles_to_meters(miles):
    """Convert statute miles to meters

    Args:
       miles (float): Distance in miles

    Returns:
       Distance in meters
    """

    return (m / 5280.0) * (12 / 39.37)

# ----------------------------------------------------------------------

def miles_to_nm(m):
    """Convert statute miles to nautical miles

    Args:
       miles (float): Distance in miles

    Returns:
       Distance in nautical miles
    """

    return m / 1.15

# ----------------------------------------------------------------------

def nm_to_miles(nm):
    """Convert nautical miles to statute miles

    Args:
       nm (float): Distance in nautical miles

    Returns:
       Distance in miles
    """

    return nm * 1.15


EARTH_RADIUS_IN_MILES = 3959
EARTH_RADIUS_IN_KM = 6371

def radians(deg):
    """Convert degrees to radians.

    Args:
      degrees (float): Angle measured in degrees

    Returns:
      Angle measured in radians
    """

    return math.pi * (deg / 180.0)

def degrees(rad):
    """Convert radians to degrees.

    Args:
      radians (float): Angle measured in radians

    Returns:
      Angle measured in degrees
    """
    return 180.0 * (rad / math.pi)

def radians_to_km(rad):
    """Convert radians on the surface of the Earth to kilometers.

    Args:
       radians (float): Distance in radians

    Returns:
       Distance measured in kilometers
    """
    return rad * EARTH_RADIUS_IN_KM

def radians_to_miles(rad):
    """Convert radians on the surface of the Earth to miles.

    Args:
       radians(float): Distance in radians

    Returns:
       Distance measured in miles
    """
    return rad * EARTH_RADIUS_IN_MILES

def miles_to_radians(miles):
    """Convert miles on the surface of the Earth to radians.

    Args:
       miles (float): distance in miles

    Returns:
       Distance measured in radians
    """
    return miles / EARTH_RADIUS_IN_MILES

def km_to_radians(km):
    """Convert kilometers on the surface of the Earth to radians.

    Args:
       km (float): distance in kilometers

    Returns:
       Distance measured in radians
    """
    return km / EARTH_RADIUS_IN_KM
