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

class Shoreline(object):
  """Information about a single shoreline

  Attributes:
    resolution (str): Fidelity of the given shape
    level (str): Hierarchical level that contains specific information, see the build_shoreline_dict() docstring
      for more information
    polygon (Shapely Polygon): Shapely polygon generated from the points of the given shape
    global_bbox (list): Lower left and upper right coordinates for the bounding box that encompasses all
      shapes from the loaded shapefile
    shape_bbox (list): Lower left and upper right coordinates for the bounding box of the given shape
      in [lon,lat,lon,lat] format
    shape_centroid (tuple): Center point or centroid for the given shape
    geojson (dicts): GeoJSON formated point information for the given shape
    points (list(tuple)): Non-GeoJSON formated point information for the given shape
  """

  def __init__(self, resolution="low", level="L1"):
    """Initialize an empty shoreline"""
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
    """Return human-readable representation of shoreline object"""

    return '<Shoreline: (Bounding Box: %s | Centroid (Lon, Lat): %s | Resolution: %s | Level: %s)>' % ( self.shape_bbox, self.shape_centroid, self.resolution, self.level )

def build_shoreline_dict(resolution="low", level="L1"):
  """Assemble the shoreline dictionary on first access

  This function is called whenever the user tries to look up a
  shoreline. It checks to make sure the table has been populated and,
  if not, loads it from disk.

  The geography data come in five resolutions:
  - full resolution: Original (full) data resolution.
  - high resolution: About 80 % reduction in size and quality.
  - intermediate resolution: Another ~80 % reduction.
  - low resolution: Another ~80 % reduction.
  - crude resolution: Another ~80 % reduction.

  Unlike the shoreline polygons at all resolutions, the lower resolution rivers are
  not guaranteed to be free of intersections. Shorelines are furthermore
  organized into 6 hierarchical levels:

  - L1: Continental land masses and ocean islands, except Antarctica.
  - L2: Lakes
  - L3: Islands in lakes
  - L4: Ponds in islands within lakes
  - L5: Antarctica based on ice front boundary.
  - L6: Antarctica based on grounding line boundary.

  The top 13 polygons (indices 0-12) in the L1 data are:

  Index | Landmass
  0     | Eurasia
  1     | Africa
  2     | North America
  3     | South America
  4     | Antarctica (AC grounding line)
  5     | Antarctica (AC ice line)
  6     | Australia
  7     | Greenland
  8     | New Guinea
  9     | Borneo
  10    | Madagascar
  11    | Baffin Island
  12    | Indonesia

  Returns:
    None

  Side Effects:
    Shapefile data will be loaded if not already in memory
  """

  global SHORELINE_DICT

  if len(SHORELINE_DICT) > 0:
    return # we've already built it
  else:
    SHORELINE_DICT = dict()

  if resolution == "high" or resolution == "full":
    raise NotImplementedError("Due to packaging constraints full and high resolution resolutions are unavailable.")
    logger.warning("Resolution is set above `intermediate/medium`, it may take longer then expected to load the requested shape(s). Please be patient or use a less detailed resolution.")

  sf = None
  if resolution == "crude":
    if level == "L4":
      raise ValueError("Level 4 data doesn't exist at the crude resolution")
    sf = shapefile.Reader(retrieve(f"GSHHS_c_{level}.shp"))
  elif resolution == "low":
    sf = shapefile.Reader(retrieve(f"GSHHS_l_{level}.shp"))
  elif resolution == "intermediate" or resolution == "medium":
    sf = shapefile.Reader(retrieve(f"GSHHS_i_{level}.shp"))
  elif resolution == "high":
    sf = shapefile.Reader(retrieve(f"GSHHS_h_{level}.shp"))
  elif resolution == "full":
    sf = shapefile.Reader(retrieve(f"GSHHS_f_{level}.shp"))

  # This approach is faster for loading everything in, doesn't mean I approve
  c = 0
  sf_shapes = sf.shapes()
  for s in sf_shapes:
    shoreline = Shoreline(resolution=resolution, level=level)
    shoreline.index = c
    shoreline.polygon = Polygon(s.points)
    shoreline.global_bbox = sf.bbox
    shoreline.shape_bbox = s.bbox
    centroid = shape(s.__geo_interface__).centroid
    shoreline.shape_centroid = (centroid.y, centroid.x)
    shoreline.geojson = s.__geo_interface__
    shoreline.points = s.points

    SHORELINE_DICT[c] = shoreline
    c += 1

# ----------------------------------------------------------------------

def shoreline_information(index, resolution="low", level="L1"):
  """Retrieve a specific shoreline shape's information. Shapes are sorted from largest to smallest.

  Args:
    index (int): Index of the desired shoreline to retrieve information for.

  Keyword Arguments:
    resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
    level (string): See the docstring for build_shoreline_dict() for more information about levels. (Default: "L1")

  Returns:
    Shoreline object at the specified index, resolution and level.

  Raises:
    KeyError: No such shoreline
    ValueError: Unknown resolution or level
  """

  resolution = resolution.lower()
  level = level.upper()

  if resolution not in ["crude","low","intermediate", "medium", "high", "full"]:
    raise ValueError("Unknown resolution level, choices are crude, low, intermediate/medium, high, full")

  if level not in ["L1","L2","L3","L4","L5","L6"]:
    raise ValueError("Unknown level, choices are L1, L2, L3, L4, L5, L6")

  global SHORELINE_DICT

  if len(SHORELINE_DICT) == 0:
    build_shoreline_dict(resolution=resolution, level=level)
  elif SHORELINE_DICT[0].resolution != resolution or SHORELINE_DICT[0].level != level:
    SHORELINE_DICT = dict()
    build_shoreline_dict(resolution=resolution, level=level)

  return SHORELINE_DICT[index]

# ----------------------------------------------------------------------

def all_shorelines(resolution="low", level="L1"):
  """Return all the shoreline records at the given level and resolution.

  Keyword Arguments:
    resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
    level (string): See the docstring for build_shoreline_dict() for more information about levels. (Default: "L1")

  Returns:
    List of shoreline objects.

  Raises:
    ValueError: Unknown resolution or level
  """

  resolution = resolution.lower()
  level = level.upper()

  if resolution not in ["crude","low","intermediate", "medium", "high", "full"]:
    raise ValueError("Unknown resolution level, choices are crude, low, intermediate/medium, high, full")

  if level not in ["L1","L2","L3","L4","L5","L6"]:
    raise ValueError("Unknown level, choices are L1, L2, L3, L4, L5, L6")

  global SHORELINE_DICT

  if len(SHORELINE_DICT) == 0:
    build_shoreline_dict(resolution=resolution, level=level)
  elif SHORELINE_DICT[0].resolution != resolution or SHORELINE_DICT[0].level != level:
    SHORELINE_DICT = dict()
    build_shoreline_dict(resolution=resolution, level=level)

  return list(SHORELINE_DICT.values())

# ----------------------------------------------------------------------

def all_shorelines_within_bounding_box(bounding_box, resolution="low", level="L1"):
  """Return all the shoreline records that exist in the given given bounding box.

  Args:
    bounding_box (Bounding Box): Bounding box to return all shoreline from.

  Keyword Arguments:
    resolution (string): Resolution of the shapes to pull from the shapefile. (Default: "low")
    level (string): See the docstring for build_shoreline_dict() for more information about levels. (Default: "L1")

  Returns:
    Dictionary of shorelines from the given bounding box.

  Raises:
    ValueError: Unknown resolution or level
  """

  resolution = resolution.lower()
  level = level.upper()

  if resolution not in ["crude","low","intermediate", "medium", "high", "full"]:
    raise ValueError("Unknown resolution level, choices are crude, low, intermediate/medium, high, full")

  if level not in ["L1","L2","L3","L4","L5","L6"]:
    raise ValueError("Unknown level, choices are L1, L2, L3, L4, L5, L6")

  global SHORELINE_DICT

  if len(SHORELINE_DICT) == 0:
    build_shoreline_dict(resolution=resolution, level=level)
  elif SHORELINE_DICT[0].resolution != resolution or SHORELINE_DICT[0].level != level:
    SHORELINE_DICT = dict()
    build_shoreline_dict(resolution=resolution, level=level)

  shorelines = {}
  for shoreline_index, shoreline in SHORELINE_DICT.items():
    shoreline_bounding_box = BoundingBox((shoreline.shape_bbox[0], shoreline.shape_bbox[1]), (shoreline.shape_bbox[2], shoreline.shape_bbox[3]))
    if intersects(shoreline_bounding_box, bounding_box):
      shorelines[shoreline_index] = shoreline

  return shorelines

# ----------------------------------------------------------------------

def buffer(points, buffer=10):
  """Return a buffered shapely polygon for the given set of points.

  Args:
    points (Shapely Points): Bounding box to return all shoreline from.

  Keyword Arguments:
    buffer (int): Distance to buffer in km. (Default: 10)

  Returns:
    Buffered polygon.
  """

  buffer_deg = km_to_radians(buffer) * 180/pi
  buffered_polygon = Polygon(points).buffer(buffer_deg)

  return buffered_polygon

# ----------------------------------------------------------------------

SHORELINE_DICT = {}
