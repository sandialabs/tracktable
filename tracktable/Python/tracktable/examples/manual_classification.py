import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from mpl_toolkits.basemap import Basemap
#import numpy as np
#import matplotlib.pyplot as plt

from pymongo import MongoClient
import argparse
from tracktable.script_helpers import argument_groups, argparse

#freqs = np.arange(2, 20, 3)

#fig, ax = plt.subplots()
#plt.subplots_adjust(bottom=0.2)
#t = np.arange(0.0, 1.0, 0.001)
#s = np.sin(2*np.pi*freqs[0]*t)
#l, = plt.plot(t, s, lw=2)


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


class Index:
    def __init__(self, trajs, trajs_out, sample_rate, figure_dimensions, args, ax):
        self.traj_iter = trajs.find()
        self.trajs_out = trajs_out
        self.sample_rate = sample_rate
        self.count = 0
        self.figure_dimensions = figure_dimensions
        self.args = args
        self.ax = ax

    def plot(self, num):
        #print("next")
        #self.ind += 1
        #i = self.ind % len(freqs)
        #ydata = np.sin(2*np.pi*freqs[i]*t)
        #l.set_ydata(ydata)
        self.ax.clear()
        plt.axes([0.1, 0.1, 0.8, 0.8])
        #plt.cla()
        #plt.close()
        m = Basemap(llcrnrlon=-105.,llcrnrlat=25.,urcrnrlon=25.,urcrnrlat=65.,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='l',projection='merc',\
            lat_0=40.,lon_0=-20.,lat_ts=20.)
        m.drawcoastlines()
        m.fillcontinents()
        # draw parallels
        m.drawparallels(np.arange(10,90,20),labels=[1,1,0,1])
        # draw meridians
        m.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1])
        self.ax.set_title('Great Circle from New York to London')
        nylat = 40.78; nylon = -73.98
        # lonlat, lonlon are lat/lon of London.
        lonlat = 51.53; lonlon = 0.08
        m.drawgreatcircle(nylon+num,nylat+num,lonlon+num,lonlat+num,linewidth=2,color='k')

    def buttons(self):
        axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
        axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
        bnext = Button(axnext, 'Yes')
        bnext.on_clicked(self.next)
        bprev = Button(axprev, 'No')
        bprev.on_clicked(self.prev)

    def next(self, event):
        print("yes")
        self.plot(-5)
        self.buttons()
        plt.draw()

    def prev(self, event):
        self.plot(5)
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

    callback.plot(0)
    axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
    axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
    bnext = Button(axnext, 'Yes')
    bnext.on_clicked(callback.next)
    bprev = Button(axprev, 'No')
    bprev.on_clicked(callback.prev)

    plt.show()

if __name__ == '__main__':
    main()





