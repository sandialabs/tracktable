import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import sys
from mpl_toolkits.basemap import Basemap
#import numpy as np
#import matplotlib.pyplot as plt

from pymongo import MongoClient
import argparse
from tracktable.script_helpers import argument_groups, argparse
import tracktable.inout.trajectory as trajectory
from tracktable.core import geomath
from tracktable.render import colormaps, mapmaker, paths
from tracktable.examples import example_trajectory_rendering

def parse_args():
    parser = argparse.ArgumentParser(description=
                                     'Read from mongo classify yes/no and write back \
                                     yes\'s to a new collection. \
                                     Example: manual_classification.py \
                                     --map "custom" HoldingTrajectories VerifiedHoldingTrajectories')

    argument_groups.use_argument_group("trajectory_rendering", parser)
    argument_groups.use_argument_group("mapmaker", parser)


    parser.add_argument('--resolution', '-r',
                        nargs=2,
                        type=int,
                        help='Resolution of output image.  Defaults to 800 600.')

    parser.add_argument('--dpi',
                        type=int,
                        default=72,
                        help='DPI of output image')

    parser.add_argument('mongo_collection')
    parser.add_argument('output_mongo_collection')
    parser.add_argument('-r', '--regex', default="")

    args = parser.parse_args()

    if args.resolution is None:
        #args.resolution = [ 800, 600 ]
        args.resolution = [ 1600, 1200 ]
    return args

def render_trajectories(basemap,
                        trajectory_source,
                        args):

    render_args = argument_groups.extract_arguments("trajectory_rendering", args)

    example_trajectory_rendering.render_trajectories(basemap,
                                                     trajectory_source,
                                                     **render_args)

class Index:
    def __init__(self, trajs, trajs_out, sample_rate, figure_dimensions, args, ax):
        self.traj_iter = trajs.find()
        self.trajs_out = trajs_out
        self.sample_rate = sample_rate
        self.count = 0
        self.figure_dimensions = figure_dimensions
        self.args = args
        self.ax = ax

    def plot(self):
        found=False
        done=False
        while not found:
            self.traj_dict = next(self.traj_iter, None)
            self.count+=1
            if self.traj_dict is None:
                found=True
                done=True
            elif (self.count-1) % self.sample_rate == 0:
                found=True
        if done:
            print("Done")
            sys.exit(0)
        else:
            plt.axes([0.1, 0.1, 0.8, 0.8])
            plt.cla()
            traj = trajectory.from_dict(self.traj_dict)
            all_points = [point for point in traj]
            self.args.map_bbox = geomath.compute_bounding_box(all_points)
            mapmaker_args = argument_groups.extract_arguments("mapmaker", self.args)
            (mymap, map_actors) = mapmaker.mapmaker(**mapmaker_args)
            color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1)
            plt.title(self.traj_dict['_id'])
            render_trajectories(mymap,
                                [traj],
                                self.args)

    def buttons(self):
        axyes = plt.axes([0.7, 0.05, 0.1, 0.075])
        byes = Button(axyes, 'Yes')
        axno = plt.axes([0.81, 0.05, 0.1, 0.075])
        bno = Button(axno, 'No')
        byes.on_clicked(self.yes_func)
        bno.on_clicked(self.no_func)

    def yes_func(self, event):
        self.trajs_out.insert_one(self.traj_dict)
        self.plot()
        self.buttons()
        plt.draw()

    def no_func(self, event):
        self.plot()
        self.buttons()
        plt.draw()

def main():
    args = parse_args()

    dpi = args.dpi
    image_resolution = args.resolution
    figure_dimensions = [ float(image_resolution[0]) / dpi, float(image_resolution[1]) / dpi ]

    client = MongoClient('localhost', 27017)
    db = client.ASDI
    trajs = db[args.mongo_collection]

    trajs_out = db[args.output_mongo_collection]

    sample_rate = 100 # one in 100

    fig=plt.figure()
    ax=fig.add_axes([0.1,0.1,0.8,0.8])
    callback = Index(trajs, trajs_out, sample_rate, figure_dimensions, args, ax)

    callback.plot()
    axyes = plt.axes([0.7, 0.05, 0.1, 0.075])
    byes = Button(axyes, 'Yes')
    axno = plt.axes([0.81, 0.05, 0.1, 0.075])
    bno = Button(axno, 'No')
    byes.on_clicked(callback.yes_func)
    bno.on_clicked(callback.no_func)

    plt.show()

if __name__ == '__main__':
    main()





