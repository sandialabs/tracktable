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

from tracktable.domain.terrestrial import TrajectoryPointReader
from tracktable.applications.assemble_trajectories import AssembleTrajectoryFromPoints
from tracktable.render.render_trajectories import render_trajectories
from tracktable.core import test_utilities as utils
import os.path
import sys

def load_sample_data(path):
    inFile = open(os.path.join(path, 'SampleFlightsUS.csv'))
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

    return list(builder.trajectories())

# ----------------------------------------------------------------------

def test_render_trajectories(ground_truth_path, test_output_path,
                             data_path):

    trajs = load_sample_data(data_path)
    few_trajs = [traj for traj in trajs if traj[0].object_id == 'SSS019'\
                 or traj[0].object_id == 'TTT020']
    #return test_default(ground_truth_path, test_output_path, few_trajs)
    num_errors = 0

    filename = "Default.html"
    render_trajectories(few_trajs,
                        backend='folium', show=False,save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "Single.html"
    render_trajectories(trajs[3],
                        backend='folium', show=False,save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "Tiles.html"
    render_trajectories(trajs[3], tiles='CartoDBPositron',
                        backend='folium', show=False,save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "TileServer.html"
    render_trajectories(trajs[3],
                        tiles='http://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
                        attr='ESRI',
                        backend='folium', show=False,save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "Bbox.html"
    render_trajectories(few_trajs,
                        map_bbox=[-108.081, 39.3078, -104.811, 41.27],
                        backend='folium', show=False,save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "ObjIds.html"
    render_trajectories(trajs, obj_ids="VVV022",
                        backend='folium', show=False,save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "ObjIdsList.html"
    render_trajectories(trajs, obj_ids=["JJJ010", "LLL012"],
                        backend='folium', show=False,save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "SolidSingle.html"
    render_trajectories([trajs[0], trajs[12]], line_color = 'red',
                        backend='folium', show=False,save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "SolidMulti.html"
    render_trajectories([trajs[0], trajs[12]],
                        line_color = ['red', '#0000FF'],
                        backend='folium', show=False,save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "ColormapSingle.html"
    render_trajectories([trajs[0], trajs[12]],
                        color_map = 'BrBG',
                        backend='folium', show=False,save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "ColormapMulti.html"
    render_trajectories([trajs[0], trajs[12]],
                        color_map = ['BrBG', 'plasma'],
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "CustomColormap.html"
    import matplotlib.cm
    import numpy as np
    blues_map = matplotlib.cm.get_cmap('Blues', 256)
    newcolors = blues_map(np.linspace(0, 1, 256))
    pink = np.array([248/256, 24/256, 148/256, 1])
    newcolors[:25, :] = pink # pink for takeoff (first ~10% of trajectory)
    render_trajectories([trajs[0], trajs[12]],
                        color_map = matplotlib.colors.ListedColormap(newcolors),
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))

    filename = "GradientHueSingle.html"
    render_trajectories([trajs[0], trajs[12]],
                        gradient_hue = .5,
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "GradientHueMulti.html"
    render_trajectories([trajs[0], trajs[12]],
                        gradient_hue = [.25, .66],
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "GradientHueFromColors.html"
    render_trajectories([trajs[0], trajs[12]],
                        gradient_hue = ['#00FF00', 'orange'],
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "AltitudeColormap.html"
    import matplotlib.colors
    def altitude_generator(trajectory):
        return [point.properties['altitude'] for point in trajectory[:-1]]
    render_trajectories([trajs[16]],
                        trajectory_scalar_generator = altitude_generator,
                        color_scale = \
                        matplotlib.colors.Normalize(vmin=0, vmax=35000),
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "Linewidth.html"
    render_trajectories(trajs[26], linewidth=5,
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "CustomLinewidth.html"
    from tracktable.render.map_processing.common_processing import progress_linewidth_generator
    render_trajectories(trajs[28], line_color='green',
                        trajectory_linewidth_generator=progress_linewidth_generator,
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "DefaultPoints.html"
    render_trajectories(trajs[15], show_points=True,
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "PointProperties.html"
    render_trajectories(trajs[15], show_points=True,
                        point_popup_properties = ['altitude', 'heading',
                                                  'speed'],
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "PointSingleColor.html"
    render_trajectories(trajs[15], point_color='red', show_points=True,
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "DotColorSize.html"
    render_trajectories(trajs[24], dot_color='red', dot_size=5,
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "NoDot.html"
    render_trajectories(trajs[24], show_dot=False,
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "DistanceGeometry.html"
    render_trajectories(trajs[25], show_distance_geometry=True,
                        distance_geometry_depth=4,
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)

    filename = "Animate.html"
    render_trajectories(trajs[23], animate=True,
                        backend='folium', show=False, save=True,
                        filename=os.path.join(test_output_path,
                                              filename))
    num_errors += utils.compare_html_to_ground_truth(filename,
                                                     ground_truth_path,
                                                     test_output_path,
                                                     ignore_uuids=True)
    return num_errors

# ----------------------------------------------------------------------

def main():
    if len(sys.argv) != 4:
        print("usage: {} ground_truth_dir test_output_dir test_data_dir".format(sys.argv[0]))
        exit(-1)
        #arg 3 is path to sample data
    return test_render_trajectories(sys.argv[1], sys.argv[2], sys.argv[3])

# ----------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(main())
