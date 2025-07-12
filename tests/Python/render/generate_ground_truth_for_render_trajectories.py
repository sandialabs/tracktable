#!/usr/bin/env python
# coding: utf-8

#Generate Ground Truth html files
from tracktable.domain.terrestrial import TrajectoryPointReader
from tracktable.applications.assemble_trajectories import AssembleTrajectoryFromPoints
from tracktable.render.render_trajectories import render_trajectories

#Load sample data for rendering exmples

#Read in points and assemble trajectories
inFile = open('../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/Points/data/SampleFlightsUS.csv')
reader = TrajectoryPointReader()
reader.input = inFile
reader.comment_character = '#'
reader.field_delimiter = ','
# Set columns for data we care about
reader.object_id_column = 0
reader.timestamp_column = 1
reader.coordinates[0] = 2
reader.coordinates[1] = 3
reader.set_real_field_column('altitude',4) #could be ints
reader.set_real_field_column('heading',5)
reader.set_real_field_column('speed',6)

builder = AssembleTrajectoryFromPoints()
builder.input = reader
builder.minumum_length = 3

trajs = list(builder.trajectories())

few_trajs = [traj for traj in trajs if traj[0].object_id == 'SSS019' or traj[0].object_id == 'TTT020']


from tracktable.render.render_trajectories import render_trajectories

# The only required parameter is a list of trajectories.  It's that simple.
render_trajectories(few_trajs, backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/Default.html")
# The default rendering assigns each object ID a hue which transitions from dark to light as the trajectory
# progresses.  In addition, by default, a white dot shows the point with the latest timestamp in the trajectory.
# Hovering over a trajectory reveals its object_id, and clicking on a trajectory give the object_id and start and stop
# time for the entire trajectory


# Can render a single trajectory
render_trajectories(trajs[3], backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/Single.html")


# You can change map tiles
render_trajectories(trajs[3], tiles='CartoDBPositron', backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/Tiles.html")
# Options include:
# OpenStreetMaps
# StamenTerrain
# StamenToner
# StamenWatercolor
# CartoDBPositron
# CartoDBDark_Matter


# You can specify a map tile server by URL # must include attribution(attr) string
render_trajectories(trajs[3], tiles='http://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}', attr='ESRI', backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/TileServer.html")


# Can specify a bounding box (default extent shows all input trajectories)
# format of map_bbox is  [minLon, minLat, maxLon, maxLat]
render_trajectories(few_trajs, map_bbox=[-108.081, -104.811, 39.3078, 41.27], backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/Bbox.html")


# Can specify specific object_ids to render as a string...
render_trajectories(trajs, obj_ids="VVV022", backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/ObjIds.html")


# ... or a list of strings
render_trajectories(trajs, obj_ids=["JJJ010", "LLL012"], backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/ObjIdsList.html")


# Can specify a solid color for all trajectories ...
render_trajectories([trajs[0], trajs[12]], line_color = 'red', backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/SolidSingle.html")
#Other color strings include: ‘red’, ‘blue’, ‘green’, ‘purple’, ‘orange’, ‘darkred’,’lightred’, ‘beige’,
#‘darkblue’, ‘darkgreen’, ‘cadetblue’, ‘darkpurple’, ‘white’, ‘pink’, ‘lightblue’, ‘lightgreen’, ‘gray’,
#‘black’, ‘lightgray’


# ... or a list of colors.  Note you can use hex string notation for the colors as well.
render_trajectories([trajs[0], trajs[12]], line_color = ['red', '#0000FF'], backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/SolidMulti.html")
# Hex string notation is of the format #RRGGBBAA,
# Red Green Blue values from 0 to 255 as 2 hex digits each,
# and an OPTIONAL alpha (opacity) value with same range and format.


# The trajectories can be colored using a colormap ...
render_trajectories([trajs[0], trajs[12]], color_map = 'BrBG', backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/ColormapSingle.html")


# ... or a list of color maps
render_trajectories([trajs[0], trajs[12]], color_map = ['BrBG', 'plasma'], backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/ColormapMulti.html")


# You can even define your own color maps
import matplotlib.cm
import numpy as np
blues_map = matplotlib.cm.get_cmap('Blues', 256)
newcolors = blues_map(np.linspace(0, 1, 256))
pink = np.array([248/256, 24/256, 148/256, 1])
newcolors[:25, :] = pink # pink for takeoff (first ~10% of trajectory)
render_trajectories([trajs[0], trajs[12]], color_map = matplotlib.colors.ListedColormap(newcolors), backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/CustomColormap.html")


# You can specify a hue as a float between 0 and 1 which will be used to create a gradient that transitions form dark
# to light as the trajectory progresses
render_trajectories([trajs[0], trajs[12]], gradient_hue = .5, backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/GradientHueSingle.html")


# As with other color options, a list of hues can be used as well.
render_trajectories([trajs[0], trajs[12]], gradient_hue = [.25, .66], backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/GradientHueMulti.html")


# Hues can be derived from an rgb color specified as a color name or hex string color
render_trajectories([trajs[0], trajs[12]], gradient_hue = ['#00FF00', 'orange'], backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/GradientHueFromColors.html")


#You can specify custom scalar mappings.  In this case the color gets lighter as altitude increases.
import matplotlib.colors
def altitude_generator(trajectory):
    #N-1 segments show altitude at beginning point
    return [point.properties['altitude'] for point in trajectory[:-1]]
#Note: be sure to include the generator, and the scale for mapping scalars to the color map.
render_trajectories([trajs[16]], trajectory_scalar_generator = altitude_generator,
                    color_scale = matplotlib.colors.Normalize(vmin=0, vmax=35000), backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/AltitudeColormap.html")


#The linewidth of the trajectories can be adjusted.  Default is 2.5 in folium
render_trajectories(trajs[26], linewidth=5, backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/Linewidth.html")


# You can also adjust the width of the trajectory by some scalar.  In this case the trajectory starts out very narrow
# and gets wider at each point it passes (as it progresses), but the color remains green throughout.
from tracktable.render.map_processing.common_processing import progress_linewidth_generator
render_trajectories(trajs[28], line_color='green', trajectory_linewidth_generator=progress_linewidth_generator, backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/CustomLinewidth.html")


# You can also show the sample points along the trajectory. By default the points are colored consistent with line
# segments
render_trajectories(trajs[15], show_points=True, backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/DefaultPoints.html")
# Hovering over a point gives the timestamp of that point and by default, clicking on a point reveals the object_id,
# timestamp, Latitude, and Longitude of that point.


# You can specify any set of properties to view when clicking on a point:
render_trajectories(trajs[15], show_points=True, point_popup_properties = ['altitude', 'heading', 'speed'], backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/PointProperties.html")
# Clicking on a point now additionaly reveals the altitude, heading, and speed.


# The colors of all points can be specified
render_trajectories(trajs[15], point_color='red', show_points=True, backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/PointSingleColor.html")


# The color and radius of the dot at the close of the trajectory can be changed
render_trajectories(trajs[24], dot_color='red', dot_size=5, backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/DotColorSize.html")


# To not show the dot at the close of the trajectory:
render_trajectories(trajs[24], show_dot=False, backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/NoDot.html")


# In folium the distance geometry calculations can be shown.  Default depth is 4
render_trajectories(trajs[25], show_distance_geometry=True, distance_geometry_depth=4, backend="folium", show=False, save=True, filename="../../../../../tracktable-data/tracktable-data/tracktable_data/internal_test_data/GroundTruth/DistanceGeometry.html")
#red are level 1 lines
#blue are leve 2 lines
#yellow are level 3 lines
# and purple are level 4 lines
#hovering over the lines gives the normalized length of each line
