#
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

import logging
import operator
import os
from csv import DictReader

from tracktable.core.geomath import intersects
from tracktable.domain.terrestrial import TrajectoryPoint
from tracktable_data.data import retrieve

logger = logging.getLogger(__name__)

class Port(object):
  """Information about a single port

  Attributes:
    world_port_index_number (str): Arbitrary index number of the given port
    region (str): WPI specified region of port
    name (str): Human-readable port name
    alternate_name (str): Alternate human-readable port name, i.e. a different name for given port
    un_locode (str): UN/LOCODE of port
    country (str): Country where port is located
    water_body (str): Body of water where the port is located
    position (tuple): (longitude, latitude) position of port
    attributes (int): All other misc attributes of the given port, see ports.csv for all other attributes
  """

  def __init__(self):
    """Initialize an empty port"""
    self.world_port_index_number = None
    self.region = None
    self.name = None
    self.alternate_name = None
    self.un_locode = None
    self.country = None
    self.water_body = None
    self.position = None # Longitude, Latitude
    self.attributes = {}

  def __str__(self):
    """Return human-readable representation of port object"""

    return '<Port: %s (Country: %s | Coordindates (Lon, Lat): %s)>' % ( self.name, self.country, self.position )

def build_port_dict():
  """Assemble the port dictionary on first access

  This function is called whenever the user tries to look up an
  port. It checks to make sure the table has been populated and,
  if not, loads it from disk.

  Returns:
    None

  Side Effects:
    Port data will be loaded if not already in memory
  """

  global PORT_DICT

  if len(PORT_DICT) > 0:
    return # we've already built it
  else:
    PORT_DICT = dict()

    with open(retrieve('ports.csv'), mode='r', encoding='utf-8') as infile:
        csvreader = DictReader(infile, delimiter=',', quotechar='"')

        for row in csvreader:
          port = Port()
          port.world_port_index_number = row.pop('World Port Index Number')
          port.region = row.pop('Region Name')
          port.name = row.pop('Main Port Name')
          port.alternate_name = row.pop('Alternate Port Name')
          port.un_locode = row.pop('UN/LOCODE')
          port.country = row.pop('Country Code')
          port.water_body = row.pop('World Water Body')
          port.position = (float(row.pop('Longitude')), float(row.pop('Latitude')))
          port.attributes = row

          PORT_DICT[port.world_port_index_number] = port

        # TODO: If we get decent port traffic stats
        # uncomment this code to sort ports by their traffic

        # from tracktable_data.python_info_data.airport_traffic import PORTS_BY_TRAFFIC
        # ports_with_traffic = sorted(PORTS_BY_TRAFFIC.items(),
        #                                 key=operator.itemgetter(1),
        #                                 reverse=True)
        # ranked_ports_with_traffic = enumerate(ports_with_traffic)
        # for (i, info) in ranked_ports_with_traffic:
        #     apt = info[0]
        #     if apt in PORT_DICT:
        #         PORT_DICT[apt].size_rank = i

# ----------------------------------------------------------------------

def port_information(port_info, country=None):
  """Look up information about an port

  Args:
    port_info (str or int): Name (str), Alternate Name (str) or World Port Index Number (int) of port

  Keyword Arguments:
    country (string): Country containing the desired port. (Default: None)

  Returns:
    Port object containing requested information or list of ports if there are multiple matching port names.

  Raises:
    KeyError: no such port
  """

  global PORT_DICT

  if len(PORT_DICT) == 0:
      build_port_dict()

  if type(port_info) is int or port_info.isdigit():
    return PORT_DICT[str(port_info)]
  else:
    matching_ports = []
    for port_index, port in PORT_DICT.items():
      if port_info.lower() == port.name.lower() or port_info.lower() == port.alternate_name.lower():
        if port_info.lower() == port.alternate_name.lower():
          logger.info("`{}` is the alternate port name for `{}`".format(port.alternate_name, port.name))
        if country is not None and country.lower() == port.country.lower():
          matching_ports.append(port)
        elif country is None:
          matching_ports.append(port)
    if len(matching_ports) > 1:
      logger.warning("`{}` matches {} port names, provide a `country` along with a port name to narrow results or provide the port's World Port Index Number to retrieve the desired port.".format(port_info, len(matching_ports)))
      return matching_ports
    elif len(matching_ports) == 1:
      return matching_ports[0]
    else:
      logger.warning("No ports found with the provided name `{}`. Double check the provided port information and/or remove the provided country.".format(port_info))
      return []

# ----------------------------------------------------------------------

def all_ports():
  """Return all the port records we have.

  Returns:
    Unsorted list of port objects.
  """

  global PORT_DICT

  if len(PORT_DICT) == 0:
    build_port_dict()

  return list(set(PORT_DICT.values()))

# ----------------------------------------------------------------------

def all_ports_by_country(country):
  """Return all the port records we have for a given country.

  Args:
    country (str): Country to return all ports from.

  Returns:
    Dictionary of ports from the given country.
  """

  global PORT_DICT

  if len(PORT_DICT) == 0:
    build_port_dict()

  ports = {}
  country = country.lower().strip(' ')
  for port_index, port in PORT_DICT.items():
    if port.country.lower() == country:
      ports[port_index] = port

  return ports

# ----------------------------------------------------------------------

def all_ports_by_water_body(water_body):
  """Return all the port records we have from a given water body.

  Args:
    water_body (str): Water body to return all ports from.

  Returns:
    Dictionary of ports from the given water body.
  """

  global PORT_DICT

  if len(PORT_DICT) == 0:
    build_port_dict()

  ports = {}
  water_body = water_body.lower().strip(' ')
  for port_index, port in PORT_DICT.items():
    bodies_of_water = port.water_body.split(';')
    bodies_of_water = [i.strip(' ').lower() for i in bodies_of_water]
    for location in bodies_of_water:
      if water_body in location:
        ports[port_index] = port

  return ports

# ----------------------------------------------------------------------

def all_ports_by_wpi_region(wpi_region):
  """Return all the port records we have from a given wpi region.

  Args:
    wpi_region (str or int): WPI region and/or accompanying numeric value to return all ports from.
      For example, wpi_region can be of the format ``Australia -- 53290`` (str) OR ``Australia`` (str) OR ``53290`` (int).

  Returns:
    Dictionary of ports from the given wpi region.
  """

  global PORT_DICT

  if len(PORT_DICT) == 0:
    build_port_dict()

  ports = {}
  wpi_region = str(wpi_region)
  wpi_region = wpi_region.lower().strip(' ')

  if len(wpi_region.split("--")) == 2:
    for port_name, port in PORT_DICT.items():
      if wpi_region == port.region.lower():
        ports[port_name] = port
  else:
    for port_name, port in PORT_DICT.items():
      regions = port.region.split('--')
      regions = [i.strip(' ').lower() for i in regions]
      for region in regions:
        if wpi_region in region:
          ports[port_name] = port

  return ports

# ----------------------------------------------------------------------

def all_ports_within_bounding_box(bounding_box):
  """Return all the port records we have from a given bounding box.

  Args:
    bounding_box (Bounding Box): Bounding box to return all ports from.

  Returns:
    Dictionary of ports from the given bounding box.
  """

  global PORT_DICT

  if len(PORT_DICT) == 0:
    build_port_dict()

  ports = {}
  for port_name, port in PORT_DICT.items():
    if intersects(TrajectoryPoint(port.position), bounding_box):
      ports[port_name] = port

  return ports

# ----------------------------------------------------------------------

PORT_DICT = {}
