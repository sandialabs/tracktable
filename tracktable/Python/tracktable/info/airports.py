# -*- coding: utf-8 -*-

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


from __future__ import print_function, absolute_import, division
import operator
import os
import os.path

from tracktable.core.compatibility import UnicodeCSVDictReader

# if sys.version_info[0] > 2:
#     pass # python 3
# else:
# #    from tracktable.core.compatibility import open_backport as open
#     from tracktable.core.compatibility import UTF8Recoder, UnicodeReader

class Airport(object):
    """Information about a single airport

    Attributes:
      iata_code (string): 3-letter IATA airport identifier
      icao_code (string): 4-leter ICAO airport identifier
      name (string): Human-readable airport name
      city (string): City where airport is located
      country (string): Country where airport is located
      position (tuple): (longitude, latitude, altitude) position of airport
      size_rank (integer): Approximate rank among all the world's airports
      utc_offset (integer): Local time zone as an offset from UTC
    """

    def __init__(self):
        """Initialize an empty airport"""
        self.iata_code = None
        self.icao_code = None
        self.name = None
        self.city = None
        self.country = None
        self.position = None # latitude, longitude, altitude
        self.utc_offset = None
        self.size_rank = 1000000

    def __str__(self):
        """Return human-readable representation of airport object"""

        return '<AIRPORT: %s (ICAO %s / IATA %s)>' % ( self.name, self.iata_code, self.icao_code )

def build_airport_dict():
    """Assemble the airport dictionary on first access

    This function is called whenever the user tries to look up an
    airport.  It checks to make sure the table has been populated and,
    if not, loads it from disk.

    Returns:
      None

    Side Effects:
      Airport data will be loaded if not already in memory
    """

    global AIRPORT_DICT

    if len(AIRPORT_DICT) > 0:
        return # we've already built it
    else:
        AIRPORT_DICT = dict()

        data_filename = '%s/data/airports.csv' % os.path.dirname(__file__)
        openflight_field_names = [ 'numeric_id',
                                   'name',
                                   'city',
                                   'country',
                                   'iata',
                                   'icao',
                                   'latitude',
                                   'longitude',
                                   'altitude',
                                   'utc_offset',
                                   'daylight_savings' ]

#        with open(data_filename, mode='r', encoding='utf-8') as infile:
        with open(data_filename, mode='r') as infile:
            csvreader = UnicodeCSVDictReader(
                infile,
                delimiter=',',
                quotechar='"',
                fieldnames=openflight_field_names
                )

            for row in csvreader:
                airport = Airport()
                airport.name = row['name']
                airport.city = row['city']
                airport.country = row['country']
                airport.iata_code = row['iata']
                airport.icao_code = row['icao']
                airport.position = ( float(row['longitude']),
                                     float(row['latitude']),
                                     float(row['altitude']) )
                airport.utc_offset = float(row['utc_offset'])
                airport.daylight_savings = row['daylight_savings']

                if len(airport.iata_code) == 0:
                    airport.iata_code = None
                else:
                    AIRPORT_DICT[airport.iata_code] = airport

                if len(airport.icao_code) == 0:
                    airport.icao_code = None
                else:
                    AIRPORT_DICT[airport.icao_code] = airport

            # now we add traffic information - rank each airport by
            # the amount of traffic it sees in some arbitrary period
            from tracktable.info.data.airport_traffic import AIRPORTS_BY_TRAFFIC
            airports_with_traffic = sorted(AIRPORTS_BY_TRAFFIC.items(),
                                           key=operator.itemgetter(1),
                                           reverse=True)
            ranked_airports_with_traffic = enumerate(airports_with_traffic)
            for (i, info) in ranked_airports_with_traffic:
                apt = info[0]
                if apt in AIRPORT_DICT:
                    AIRPORT_DICT[apt].size_rank = i

# ----------------------------------------------------------------------

def airport_information(airport_code):
    """Look up information about an airport

    Args:
      airport_code: ICAO or IATA code for an airport

    Returns:
      Airport object containing requested information.

    Raises:
      KeyError: no such airport
    """

    global AIRPORT_DICT

    if len(AIRPORT_DICT) == 0:
        build_airport_dict()

    return AIRPORT_DICT.get(airport_code, None)

# ----------------------------------------------------------------------

def airport_size_rank(airport_code):
    """Return an airport's global rank by size

    Args:
      airport_code (string): IATA or ICAO airport identifier

    Returns:
      Integer ranking.  1 is the largest, higher values are smaller.
    """

    try:
        ap_info = airport_information(airport_code)
        return ap_info.size_rank
    except KeyError:
        return 1000000

# ----------------------------------------------------------------------

def all_airports():
    """Return all the airport records we have

    Returns:
      Unsorted list of airport objects.
    """

    global AIRPORT_DICT

    if len(AIRPORT_DICT) == 0:
        build_airport_dict()

    return AIRPORT_DICT.values()

# ----------------------------------------------------------------------

AIRPORT_DICT = {}

# This information comes from Wikipedia:
#
# http://en.wikipedia.org/wiki/World's_busiest_airports_by_passenger_traffic

TIER1_AIRPORTS = [
    'ATL',
    'PEK',
    'LHR',
    'HND',
    'ORD',
    'LAX',
    'CDG',
    'DFW',
    'CGK',
    'DXB',
    'FRA',
    'HKG',
    'DEN',
    'BKK',
    'SIN',
    'AMS',
    'JFK',
    'CAN',
    'MAD',
    'IST',
    'PVG',
    'SFO',
    'LAS',
    'CLT',
    'PHX',
    'IAH',
    'KUL',
    'MIA',
    'ICN',
    'MUC',
    'SYD',
    'FCO',
    'MCO',
    'BCN',
    'YYZ',
    'LGW'
]

TIER2_AIRPORTS = [
    'DEL',
    'EWR',
    'SHA',
    'SEA',
    'MSP',
    'NRT',
    'GRU',
    'DTW',
    'MNL',
    'CTU',
    'PHL',
    'BOM',
    'SZX',
    'MEL',
    'BOS',
    'LGA',
    'FLL',
    'BWI',
    'IAD',
    'SLC',
    'MDW',
    'DCA',
    'HNL',
    'SAN',
    'TPA'
]

TIER3_AIRPORTS = [
    'PDX',
    'STL',
    'MCI',
    'HOU',
    'BNA',
    'MKE',
    'OAK',
    'RDU',
    'AUS',
    'CLE',
    'SMF',
    'MEM',
    'MSY',
    'SNA',
    'SJC',
    'PIT',
    'SAT',
    'SJU',
    'DAL',
    'RSW',
    'IND',
    'CVG',
    'CMH',
    'PBI',
    'BDL',
    'ABQ',
    'JAX',
    'OGG',
    'BUF',
    'ANC',
    'ONT',
    'BUR',
    'OMA',
    'PVD',
    'RNO'
]


# This information comes from Wikipedia:
# http://en.wikipedia.org/wiki/List_of_the_busiest_airports_in_the_United_States

BUSIEST_US_AIRPORTS_BY_PASSENGER_BOARDINGS = [
    'ATL',
    'ORD',
    'LAX',
    'DFW',
    'DEN',
    'JFK',
    'SFO',
    'LAS',
    'PHX',
    'IAH',
    'CLT',
    'MIA',
    'MCO',
    'EWR',
    'SEA',
    'MSP',
    'DTW',
    'PHL',
    'BOS',
    'LGA',
    'FLL',
    'BWI',
    'IAD',
    'SLC',
    'MDW',
    'DCA',
    'HNL',
    'SAN',
    'TPA'
]

# This information comes from Wikipedia:
# http://en.wikipedia.org/wiki/List_of_the_busiest_airports_in_the_United_States

US_SECONDARY_HUBS = [
    'PDX',
    'STL',
    'MCI',
    'HOU',
    'BNA',
    'MKE',
    'OAK',
    'RDU',
    'AUS',
    'CLE',
    'SMF',
    'MEM',
    'MSY',
    'SNA',
    'SJC',
    'PIT',
    'SAT',
    'SJU',
    'DAL',
    'RSW',
    'IND',
    'CVG',
    'CMH',
    'PBI',
    'BDL',
    'ABQ',
    'JAX',
    'OGG',
    'BUF',
    'ANC',
    'ONT',
    'BUR',
    'OMA',
    'PVD',
    'RNO'
]

AIRPORTS_BY_TIER = dict()

def airport_tier(airport_code):
    """Return an estimated tier for an airport

    We divide airports roughly into 4 tiers (chosen purely by hand)
    for a classification task.  This function lets us retrieve the
    tier assigned to any given airport.

    Args:
      airport_code (string): IATA/ICAO airport identifier

    Returns:
      String: tier1, tier2, tier3 or tier4

    Raises:
      KeyError: no such airport
    """


    global AIRPORTS_BY_TIER, TIER1_AIRPORTS, TIER2_AIRPORTS, TIER3_AIRPORTS

    if len(AIRPORTS_BY_TIER) == 0:
        for airport in TIER1_AIRPORTS:
           info = airport_information(airport)
           AIRPORTS_BY_TIER[info.iata_code] = 'tier1'
           AIRPORTS_BY_TIER[info.icao_code] = 'tier1'
        for airport in TIER2_AIRPORTS:
           info = airport_information(airport)
           AIRPORTS_BY_TIER[info.iata_code] = 'tier2'
           AIRPORTS_BY_TIER[info.icao_code] = 'tier2'
        for airport in TIER3_AIRPORTS:
           info = airport_information(airport)
           AIRPORTS_BY_TIER[info.iata_code] = 'tier3'
           AIRPORTS_BY_TIER[info.icao_code] = 'tier3'

    return AIRPORTS_BY_TIER.get(airport_code, 'tier4')
