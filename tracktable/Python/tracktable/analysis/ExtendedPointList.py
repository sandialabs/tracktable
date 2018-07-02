import sys, csv, os, math
# sys.path.append(os.getcwd())
from tracktable.analysis.ExtendedPoint import ExtendedPoint as EP
import tracktable.analysis.ExtendedPoint as ExtendedPoint
import tracktable.core.geomath as geomath
from statistics import median
import tracktable.analysis.parseTreeCategorizations as CATs
import tracktable.analysis.parseTreeNode
from tracktable.analysis.parseTreeNode import Parse_Tree_Root as PTroot
from tracktable.analysis.parseTreeNode import Parse_Tree_Leaf as PTleaf
import tracktable.analysis.nx_graph as nxg

__author__ = ['Paul Schrum']

class ExtendedPointList(list):
    def computeAllPointInformation(self, account_for_lat_long=False,
                                   computeSpeeds=True):
        """
        For each triplet of points in the list of points, compute the
        attribute data for the arc (circular curve segment) that starts
        at point 1, passes through point 2, and ends at point 3.  Then
        assign the curve data to point 2 for safe keeping.
        :param self: This list of points to be analyzed. These must be ordered
                    spatially or the results are meaningless.
        :param account_for_lat_long: When true, treat coordinates where
                |y| < 90° and |x| < 180° as lat/long, then use the Quick
                Projection method.
                See https://tinyurl.com/QuickProjectionMethod for
                documentation on that.
        :return: None
        """
        use_quick_projection = account_for_lat_long and \
            math.fabs(self[2].Y) < 90.0 and \
            math.fabs(self[2].X) < 180.0

        if use_quick_projection:
            for pt1, pt2, pt3 in zip(self[:-2],
                                     self[1:-1],
                                     self[2:]):
                ExtendedPoint.compute_arc_parameters_lat_long(pt1, pt2, pt3,
                                            convert_distances_to='miles')
        else:
            for pt1, pt2, pt3 in zip(self[:-2],
                                     self[1:-1],
                                     self[2:]):
                ExtendedPoint.compute_arc_parameters(pt1, pt2, pt3)

        from math import cos
        for a_point, prev_point, next_point in \
                zip(self[1:-2], self[:-3], self[2:-1]):
            timedelta = a_point.timestamp - prev_point.timestamp
            if a_point.pt2pt:
                # The following hack is a hack for distance and speed
                #   adjustment. Do not use it. Do not keep it. Do not
                #   commit it. It is wrong and a crutch just for today.
                distBackMiles = a_point.pt2pt.distanceBack

                a_point.pt2pt.seconds_back = timedelta.seconds
                speed = distBackMiles / (timedelta.seconds / 3600.0)
                a_point.pt2pt.speed_back_mph = speed
                # speed is miles per hour
            if prev_point.pt2pt:
                prev_point.pt2pt.speed_ahead_mph = speed
            if a_point.arc:
                a_point.arc.time_delta = next_point.timestamp - \
                    prev_point.timestamp

                if a_point.arc.deflection != 0.0:
                    miles_per_second = (a_point.arc.lengthBack + \
                                        a_point.arc.lengthAhead) / \
                                        (a_point.arc.time_delta.seconds)
                    a_point.arc.speed = (miles_per_second * 3600.0, 'mph')

                    # compute ω
                    radial_speed = a_point.arc.deflection / \
                                   a_point.arc.time_delta.seconds
                    radial_accel_meters_per_s2 = radial_speed * radial_speed \
                                                 / (a_point.arc.radius * 1609.344)
                    rad_accel_g_force = radial_accel_meters_per_s2 / 9.81
                    micro_g = 1000000.0 * rad_accel_g_force

                    a_point.arc.radial_acceleration = (micro_g, 'μg')

                else:
                    a_point.arc.speed = 0.0
                    a_point.arc.radial_acceleration = (0.0, 'μg')

        for idx, a_point in enumerate(self):
            a_point.my_index = idx

    def mark_likely_zigzags(self):
        """
        Marks every point with may_be_zigzag attribute based on criteria
        in this method
        :return: None
        """
        for pt in self:
            pt.may_be_zigzag = False
        if len(self) < 26:
            return

        time_delta_zz_threshold = median([pt.pt2pt.seconds_back
                                     for pt in self[2:-2]]) * 1.25

        prev_secs = self[1].pt2pt.seconds_back
        # prev_dist = self[1].pt2pt.distanceBack
        for pt in self[2:-2]:
            # current_dist = pt.pt2pt.distanceBack
            current_secs = pt.pt2pt.seconds_back
            if current_secs < 0.001 or prev_secs < 0.001:
                seconds_ratio = float('inf')
            else:
                seconds_ratio = current_secs / prev_secs
                if seconds_ratio < 1.0:
                    seconds_ratio = 1 / seconds_ratio
            # totlTime = prev_secs + current_secs
            def_deg = math.fabs(pt.pt2pt.deflection_deg)
            # speed_mph = pt.pt2pt.speed_back_mph
            if (def_deg >= 75.0 and seconds_ratio > 2.1) or \
                def_deg >= 125.0:
                pt.may_be_zigzag = True
            prev_secs = current_secs
            # prev_dist = current_dist

    def categorize_points(self: "ExtendedPointList") -> None:
        """For certain criteria, categorize each point."""
        for a_point in self[1:-1]:
            CATs.LegLengthCat.assign_to(a_point, 'leg_length_cat')
            CATs.CurvatureCat.assign_to(a_point, 'curvature_cat')
            CATs.DeflectionCat.assign_to(a_point, 'deflection_cat')
        self[0].leg_length_cat = self[1].leg_length_cat = None
        self[0].curvature_cat = self[-1].curvature_cat = None
        self[0].deflection_cat = self[-1].deflection_cat = None

    def create_minimal_digraph(self: "ExtendedPointList") -> nxg.TreeDiGraph:
        """From self create/return a NetworkX Directed Graph of the network.
        This includes only the root (mapped to the whole trajectory), and all
        points, which are leaves on the graph."""
        g = nxg.TreeDiGraph()
        g.my_EPL = self
        g.my_trajecory = self.my_trajectory

        trajectory_range = [0, len(self)]
        root_node = PTroot(trajectory_range, self)
        g.add_node(root_node)
        g.root = root_node

        for a_point in self:
            pt_range = [a_point.my_index, a_point.my_index+1]
            a_leaf = PTleaf(pt_range, self)
            g.add_node(a_leaf)
            g.add_edge(root_node, a_leaf)

        g.leaf_count = len(self)

        return g

    def writeToCSV(self, fileName):
        """
        Write all points in the point list to the indicated file, expecting
        the points to be of type ExtendedPoint.
        :param self:
        :return: None
        """
        with open(fileName, 'w') as f:
            headerStr = EP.header_list()
            f.write(headerStr + '\n')
            for i, point in enumerate(self):
                writeStr = str(point)
                f.write(writeStr + '\n')

class _low_high(list):
    def __init__(self):
        self.append(float("inf"))
        self.append(-1 * float("inf"))

    def _include(self, next_value):
        self[0] = min(self[0], next_value)
        self[1] = max(self[1], next_value)

    @property
    def min_val(self):
        return self[0]

    @property
    def max_val(self):
        return self[1]


def _createExtendedPointList_trajectory(trajectory):
    """
    Args:
        trajectory: An np array of points. X is [0], Y is [1]
            Z is optional and would be [2]

    Returns: New instance of an ExtendedPointList.
    """
    z_range_list = _low_high()
    xIndex = 0; yIndex = 1; zIndex = 2
    newEPL = ExtendedPointList()
    prevRow = None
    for aRow in trajectory:
        x = aRow[xIndex]
        y = aRow[yIndex]
        z = geomath.altitude(aRow)

        new_ext_pt = EP(x, y, z)
        new_ext_pt.timestamp = getattr(aRow, 'timestamp')

        newEPL.append(new_ext_pt)
        z_range_list._include(z)
        prevRow = aRow

    newEPL.z_range = z_range_list
    newEPL.name = trajectory[0].object_id
    trajectory.my_EPL = newEPL
    newEPL.my_trajectory = trajectory
    return newEPL



def _createExtendedPointList_csvFile(csvFileName=None):
    """
    Args:
        csvFileName: The path and filename of the csv file to be read.

    Returns: New instance of an ExtendedPointList.
    """
    newEPL = ExtendedPointList()
    with open(csvFileName, mode='r') as f:
        rdr = csv.reader(f)
        count = 0
        for aRow in rdr:
            if count == 0:
                header = aRow
                count += 1
                xIndex = header.index('X')
                yIndex = header.index('Y')
            else:
                x = float(aRow[xIndex])
                y = float(aRow[yIndex])
                newEPL.append(EP(x, y))

    newEPL.my_trajectory = None
    return newEPL


def CreateExtendedPointList(trajectory=None, csvFileName=None):
    """
    Factory method. Use this instead of the constructor:
                variable = ExtendedPointList().

    Args:
        trajectory: An np array of points. X is [0], Y is [1]
        csvFileName: The path and filename of the csv file to be read.

    Returns: New instance of an ExtendedPointList.
    """

    if csvFileName is None and trajectory is None:
        return None
    if csvFileName and trajectory:
        raise ValueError("both parameters may not be defined.")

    if csvFileName:
        return _createExtendedPointList_csvFile(csvFileName)

    return _createExtendedPointList_trajectory(trajectory)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Running tests.")
        cwd = os.getcwd()
        inFileName = cwd + r"/TestFiles/CSV/Y15A_Computed.csv"
        outFileName = cwd + r"/TestFiles/CSV/Y15A_Computed_temp.csv"
        if not os.path.exists(inFileName):
            print("The test input file can't be found. Test not run.")
            exit(0)
    else:
        inFileName = sys.argv[1]
        outFileName = sys.argv[2]

    aPointList = CreateExtendedPointList(inFileName)
    aPointList.computeAllPointInformation()
    aPointList.writeToCSV(outFileName)

    if len(sys.argv) == 1:
        print('Test complete.')
    if not os.path.exists(outFileName):
        print('output file not created.')

