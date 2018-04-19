# Copyright (c) 2014-2018 National Technology and Engineering
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

# Author: Ben Newton  - April 17, 2018

import argparse
from pymongo import MongoClient
import tracktable.io.trajectory as trajectory
import sys
from matplotlib.widgets import Button

import random

import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#must be run on a node with a monitor

from tracktable.core import geomath
from tracktable.info import cities
from tracktable.render import colormaps, mapmaker, paths
from tracktable.script_helpers import argument_groups, argparse

from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap

from tracktable.examples import example_trajectory_rendering

from numpy import arange, sin, pi


#adapted from https://matplotlib.org/examples/user_interfaces/embedding_in_qt4.html
#from matplotlib.backends import qt_compat
#use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
#if use_pyside:
#    from PySide import QtGui, QtCore
#else:
#    from PyQt5 import QtGui, QtCore

#qt5


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
        args.resolution = [ 800, 600 ]
    return args

# ----------------------------------------------------------------------

def render_trajectories(basemap,
                        trajectory_source,
                        args):

    render_args = argument_groups.extract_arguments("trajectory_rendering", args)

    example_trajectory_rendering.render_trajectories(basemap,
                                                     trajectory_source,
                                                     **render_args)

# ----------------------------------------------------------------------

class Classify:
    def __init__(self, trajs, trajs_out, sample_rate, figure_dimensions, args):
        self.traj_iter = trajs.find()
        self.trajs_out = trajs_out
        self.sample_rate = sample_rate
        self.count = 0
        self.figure_dimensions = figure_dimensions
        self.args = args

    def yes_func(self, event):
        self.trajs_out.insert_one(self.traj_dict)
        pyplot.close()
        self.run()

    def no_func(self, event):
        pyplot.close()
        self.run()

    def run(self):
        self.traj_dict = next(self.traj_iter, None)
        #print(self.traj_dict)
        self.count+=1
        if self.traj_dict is not None:
            if (self.count-1) % self.sample_rate == 0:
                traj = trajectory.from_dict(self.traj_dict)
                figure = pyplot.figure(figsize=self.figure_dimensions)

                axes = figure.add_axes([0, 0, 1, 1], frameon=False)
                axes.set_frame_on(False)
                all_points = [point for point in traj]
                self.args.map_bbox = geomath.compute_bounding_box(all_points)
                mapmaker_args = argument_groups.extract_arguments("mapmaker", self.args)
                (mymap, map_actors) = mapmaker.mapmaker(**mapmaker_args)
                print(mapmaker_args)
                color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1)

                render_trajectories(mymap,
                                    [traj],
                                    self.args)
                axyes = pyplot.axes([0.7, 0.05, 0.1, 0.075])
                byes = Button(axyes, 'Yes')
                axno = pyplot.axes([0.81, 0.05, 0.1, 0.075])
                bno = Button(axno, 'No')
                byes.on_clicked(self.yes_func)
                bno.on_clicked(self.no_func)
                #print("showing")
                #pyplot.show()
                pyplot.draw()
            else:
                self.run() #skip to next
        #else: #done
            #return
            #valid = input("Was that trajectory in the class? (y/n):").lower()
            #if valid == 'y' or valid == 'yes':
            #    trajs_out.insert_one(traj_dict)


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        #print("mystatic***")
        #t = arange(0.0, 3.0, 0.01)
        #s = sin(2*pi*t)
        #self.axes.plot(t, s)
        #figure = pyplot.figure(figsize=self.figure_dimensions)

        #axes = figure.add_axes([0, 0, 1, 1], frameon=False)
        #axes.set_frame_on(False)
        #all_points = [point for point in traj]
        #self.args.map_bbox = geomath.compute_bounding_box(all_points)
        #mapmaker_args = argument_groups.extract_arguments("mapmaker", self.args)
        (mymap, map_actors) = mapmaker.mapmaker(ax = self.axes, domain = 'terrestrial', map_name='custom', map_projection = 'cyl', map_bbox=(-121, 39, -119, 41))
        mymap.plot(-120, 40)
        #print("mystatic2***")
        #color_scale = matplotlib.colors.Normalize(vmin=0, vmax=1)

        #render_trajectories(mymap,
        #                    [traj],
        #                    self.args)


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [random.randint(0, 10) for i in range(4)]
        self.axes.cla()
        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)

        l = QtWidgets.QVBoxLayout(self.main_widget)
        sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        l.addWidget(sc)
        l.addWidget(dc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About",
                                """embedding_in_qt4.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale

This program is a simple example of a Qt4 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation."""
                                )

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

    #figure = pyplot.figure(figsize=figure_dimensions)
    #pyplot.ion()
    #pyplot.show()
    #pyplot.ion() # turn on interactive mode?

    qApp = QtWidgets.QApplication(sys.argv)

    aw = ApplicationWindow()
    aw.setWindowTitle("Manual classification")
    aw.show()
    sys.exit(qApp.exec_())



    c = Classify(trajs, trajs_out, sample_rate, figure_dimensions, args)
    c.run()

    #count = 0
    #for traj_dict in trajs.find():#'{'+args.regex+'}'):


if __name__ == '__main__':
    main()
