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
from math import pi

import shapefile
from shapely.geometry import Polygon, shape
from tracktable.core.conversions import km_to_radians
from tracktable.core.geomath import intersects
from tracktable.domain.terrestrial import BoundingBox
from tracktable_data.data import retrieve

logger = logging.getLogger(__name__)

class River(object):
  """Information about a single river

  Attributes:
    resolution (str): Fidelity of the given shape
    level (str): Hierarchical level that contains specific information, see the build_river_dict() docstring
      for more information
    polygon (Shapely Polygon): Shapely polygon generated from the points of the given shape
    global_bbox (list): Lower left and upper right coordinates for the bounding box that encompasses all
      shapes from the loaded shapefile
    shape_bbox (list): Lower left and upper right coordinates for the bounding box of the given shape
      in [lon,lat,lon,lat] format
    shape_centroid (tuple): Center point or centroid for the given shape
    geojson (dict): GeoJSON formated point information for the given shape
    points (list(tuple)): Non-GeoJSON formated point information for the given shape
  """

  def __init__(self, resolution="low", level="L01"):
    """Initialize an empty river"""
    self.resolution = resolution
    self.level = level
    self.index = None
    self.polygon = None
    self.global_bbox = None
    self.shape_bbox = None
    self.shape_centroid = None
    self.geojson = None
    self.points = None

  def __str__(self):
    """Return human-readable representation of river object"""

    return '<River: (Bounding Box: %s | Centroid (Lon, Lat): %s | Resolution: %s | Level: %s)>' % ( self.shape_bbox, self.shape_centroid, self.resolution, self.level )

def build_river_dict(resolution="low", level="L01"):
  """Assemble the river dictionary on first access

  This function is called whenever the user tries to look up an
  river. It checks to make sure the table has been populated and,
  if not, loads it from disk.

  The geography data come in five resolutions:
  - full resolution: Original (full) data resolution.
  - high resolution: About 80 % reduction in size and quality.
  - intermediate resolution: Another ~80 % reduction.
  - low resolution: Another ~80 % reduction.
  - crude resolution: Another ~80 % reduction.

  Note that because GIS software confusingly seem to assume a Cartesian geometry,
  any polygon straddling the Dateline is broken into an east and west component.
  The most obvious example is Antarctica.

  The river database comes with 11 levels:

  - L01: Double-lined rivers (river-lakes).
  - L02: Permanent major rivers.
  - L03: Additional major rivers.
  - L04: Additional rivers.
  - L05: Minor rivers.
  - L06: Intermittent rivers - major.
  - L07: Intermittent rivers - additional.
  - L08: Intermittent rivers - minor.
  - L09: Major canals.
  - L10: Minor canals.
  - L11: Irrigation canals.

  Returns:
    None

  Side Effects:
    Shapefile data will be loaded if not already in memory
  """

  global RIVER_DICT

  if len(RIVER_DICT) > 0:
    return # we've already built it
  else:
    RIVER_DICT = dict()

  if resolution == "high" or resolution == "full":
    raise NotImplementedError("Due to packaging constraints full and high resolution resolutions are unavailable.")
    logger.warning("Resolution is set above `intermediate/medium`, it may take longer then expected to load the requested shape(s). Please be patient or use a less detailed resolution.")

  sf = None
  if resolution == "crude":
    sf = shapefile.Reader(retrieve(f"WDBII_river_c_{level}.shp"))
  elif resolution == "low":
    sf = shapefile.Reader(retrieve(f"WDBII_river_l_{level}.shp"))
  elif resolution == "intermediate" or resolution == "medium":
    sf = shapefile.Reader(retrieve(f"WDBII_river_i_{level}.shp"))
  elif resolution == "high":
    sf = shapefile.Reader(retrieve(f"WDBII_river_h_{level}.shp"))
  elif resolution == "full":
    sf = shapefile.Reader(retrieve(f"WDBII_river_f_{level}.shp"))

  # This approach is faster for loading everything from disk, this doesn't mean I approve of it though.
  c = 0
  sf_shapes = sf.shapes()
  for s in sf_shapes:
    river = River(resolution=resolution, level=level)
    river.index = c
    river.polygon = shape(s.__geo_interface__)
    river.global_bbox = sf.bbox
    river.shape_bbox = s.bbox
    centroid = shape(s.__geo_interface__).centroid
    river.shape_centroid = (centroid.y, centroid.x)
    river.geojson = s.__geo_interface__
    river.points = s.points

    RIVER_DICT[c] = river
    c += 1

# ----------------------------------------------------------------------

def river_information(index, resolution="low", level="L01"):
  """Retrieve a specific river shape's information. Shapes are sorted from largest to smallest.

  Args:
    index (int): Index of the desired river to retrieve information for.

  Keyword Arguments:
    resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
    level (string): See the docstring for build_river_dict() for more information about levels. (Default: "L01")

  Returns:
    River object at the specified index, resolution and level.

  Raises:
    KeyError: No such river
    ValueError: Unknown resolution or level
  """

  resolution = resolution.lower()
  level = level.upper()

  if resolution not in ["crude", "low", "intermediate", "medium", "high", "full"]:
    raise ValueError("Unknown resolution level, choices are crude, low, intermediate/medium, high, full")

  if level not in ["L01","L02","L03","L04","L05","L06","L07","L08","L09","L10","L11"]:
    raise ValueError("Unknown level, choices are L01, L02, L03, L04, L05, L06, L07, L08, L09, L10, L11")

  global RIVER_DICT

  if len(RIVER_DICT) == 0:
      build_river_dict(resolution=resolution, level=level)
  elif RIVER_DICT[0].resolution != resolution or RIVER_DICT[0].level != level:
    RIVER_DICT = dict()
    build_river_dict(resolution=resolution, level=level)

  return RIVER_DICT[index]

# ----------------------------------------------------------------------

def all_rivers(resolution="low", level="L01"):
  """Return all the river records at the given level and resolution.

  Keyword Arguments:
    resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
    level (string): See the docstring for build_river_dict() for more information about levels. (Default: "L01")

  Returns:
    List of river objects.

  Raises:
    ValueError: Unknown resolution or level
  """

  resolution = resolution.lower()
  level = level.upper()

  if resolution not in ["crude", "low", "intermediate", "medium", "high", "full"]:
    raise ValueError("Unknown resolution level, choices are crude, low, intermediate/medium, high, full")

  if level not in ["L01","L02","L03","L04","L05","L06","L07","L08","L09","L10","L11"]:
    raise ValueError("Unknown level, choices are L01, L02, L03, L04, L05, L06, L07, L08, L09, L10, L11")

  global RIVER_DICT

  if len(RIVER_DICT) == 0:
    build_river_dict(resolution=resolution, level=level)
  elif RIVER_DICT[0].resolution != resolution or RIVER_DICT[0].level != level:
    RIVER_DICT = dict()
    build_river_dict(resolution=resolution, level=level)

  return list(RIVER_DICT.values())

# ----------------------------------------------------------------------

def all_rivers_within_bounding_box(bounding_box, resolution="low", level="L01"):
  """Return all the river records that exist in the given given bounding box.

  Args:
    bounding_box (Bounding Box): Bounding box to return all river from.

  Keyword Arguments:
    resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
    level (string): See the docstring for build_river_dict() for more information about levels. (Default: "L01")

  Returns:
    Dictionary of rivers from the given bounding box.

  Raises:
    ValueError: Unknown resolution or level
  """

  resolution = resolution.lower()
  level = level.upper()

  if resolution not in ["crude", "low", "intermediate", "medium", "high", "full"]:
    raise ValueError("Unknown resolution level, choices are crude, low, intermediate/medium, high, full")

  if level not in ["L01","L02","L03","L04","L05","L06","L07","L08","L09","L10","L11"]:
    raise ValueError("Unknown level, choices are L01, L02, L03, L04, L05, L06, L07, L08, L09, L10, L11")

  global RIVER_DICT

  if len(RIVER_DICT) == 0:
    build_river_dict(resolution=resolution, level=level)
  elif RIVER_DICT[0].resolution != resolution or RIVER_DICT[0].level != level:
    RIVER_DICT = dict()
    build_river_dict(resolution=resolution, level=level)

  rivers = {}
  for river_index, river in RIVER_DICT.items():
    river_bounding_box = BoundingBox((river.shape_bbox[0], river.shape_bbox[1]), (river.shape_bbox[2], river.shape_bbox[3]))
    if intersects(river_bounding_box, bounding_box):
      rivers[river_index] = river

  return rivers

# ----------------------------------------------------------------------

def buffer(points, buffer=10):
  """Return a buffered polygon for the given set of points.

  Args:
    points (Shapely Points): Bounding box to return all river from.

  Keyword Arguments:
    buffer (int): Distance to buffer in km. (Default: 10)

  Returns:
    Buffered polygon.
  """

  buffer_deg = km_to_radians(buffer) * 180/pi
  buffered_polygon = Polygon(points).buffer(buffer_deg)

  return buffered_polygon

# ----------------------------------------------------------------------

RIVER_DICT = {}
