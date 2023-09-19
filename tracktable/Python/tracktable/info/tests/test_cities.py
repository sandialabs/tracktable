# Copyright (c) 2014-2023, National Technology & Engineering Solutions of
#   Sandia, LLC (NTESS).
# All rights reserved.
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

# Author: Phil Baxley
# Date:   May 27, 2020

import sys

from tracktable.info import cities
from tracktable.core import Timestamp
import importlib
import pprint
from tracktable.domain.terrestrial import TrajectoryPoint, BasePoint

#Search for Paris in the US, using lat lon
# There are multiple Paris's in the US.
# Will use lat long of Paris France, should return
# one in US though!
def test_paris_us_lat_lon():
    city = cities.get_city("Paris", "US", (50, 2))

    if (city == None or city.name != "Paris") or \
        (city.country_code != "us") or \
        (city.population != 5073) or \
        (city.location != BasePoint(44.2597222, -70.5011111)):
        print("Failed test_paris_us_lat_lon")
        return 1

    return 0

# Searching with lat lon close to Phillipines will return Albuquerque PH
# Not using the US version since default is to return the largest town
def test_abq_with_tuple():
    city = cities.get_city("Albuquerque", None, (10, 120))

    if (city == None or city.name != "Albuquerque") or \
        (city.country_code != "ph") or \
        (city.population != 2730) or \
        (city.location != BasePoint(9.608056, 123.958056)):
        print("Failed test_abq_with_lat_lon")
        return 1

    return 0

# Searching with lat lon close to Phillipines will return Albuquerque PH
# Not using the US version since default is to return the largest town
def test_abq_with_basepoint():
    city = cities.get_city("Albuquerque", None, BasePoint(10, 120))

    if (city == None or city.name != "Albuquerque") or \
        (city.country_code != "ph") or \
        (city.population != 2730) or \
        (city.location != BasePoint(9.608056, 123.958056)):
        print("Failed test_abq_with_lat_lon")
        return 1

    return 0

# Searching with lat lon close to Phillipines will return Albuquerque PH
# Not using the US version since default is to return the largest town
def test_abq_with_trajpoint():
    city = cities.get_city("Albuquerque", None, TrajectoryPoint(10, 120))

    if (city == None or city.name != "Albuquerque") or \
        (city.country_code != "ph") or \
        (city.population != 2730) or \
        (city.location != BasePoint(9.608056, 123.958056)):
        print("Failed test_abq_with_lat_lon")
        return 1

    return 0

# Searching by country in this example will return something smaller than Albuquerque US
def test_abq_with_country():
    city = cities.get_city("Albuquerque", "PH")

    if (city == None or city.name != "Albuquerque") or \
        (city.country_code != "ph") or \
        (city.population != 2730) or \
        (city.location != BasePoint(9.608056, 123.958056)):
        print("Failed test_abq_with_country")
        return 1

    return 0

# If searching on only the name, the largest city (by population) is returned
def test_abq_name_only():
    city = cities.get_city("Albuquerque")

    if (city == None or city.name != "Albuquerque") or \
        (city.country_code != "us") or \
        (city.population != 487378) or \
        (city.location != BasePoint(35.0844444, -106.6505556)):
        print("Failed test_abq_name_only")
        return 1

    return 0

def main():
    error_count = 0
    error_count += test_abq_name_only()
    error_count += test_abq_with_country()
    error_count += test_abq_with_tuple()
    error_count += test_abq_with_basepoint()
    error_count += test_abq_with_trajpoint()
    error_count += test_paris_us_lat_lon()
    return error_count

if __name__ == '__main__':
    sys.exit(main())
