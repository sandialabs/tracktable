import sys, csv, os, math
# sys.path.append(os.getcwd())
from tracktable.analysis.ExtendedPoint import ExtendedPoint as EP
import tracktable.analysis.ExtendedPoint as ExtendedPoint
import tracktable.core.geomath as geomath

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
        for a_point, prev_point in zip(self[1:], self[:-1]):
            timedelta = a_point.timestamp - prev_point.timestamp
            if a_point.pt2pt:
                # The following hack is a hack for distance and speed
                #   adjustment. Do not use it. Do not keep it. Do not
                #   commit it. It is wrong and a crutch just for today.
                distBackMiles = a_point.pt2pt.distanceBack
                # adjFactor = 0.8 * 69.1
                milesPerDegree = 69.1
                latAdjustment = 1.1 * cos(a_point.Y / 57.2958)
                adjFactor = milesPerDegree * latAdjustment
                distBackMiles *= adjFactor
                #  0.8 adjusts for latitude
                #  69.1 adjusts for miles per degree
                #

                speed = distBackMiles / (timedelta.seconds / 3600.0)
                # speed is miles per hour
                a_point.pt2pt.speedBack = speed
            if prev_point.pt2pt:
                prev_point.pt2pt.speedAhead = speed

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
    for aRow in trajectory:
        x = aRow[xIndex]
        y = aRow[yIndex]
        z = geomath.altitude(aRow)

        new_ext_pt = EP(x, y, z)
        new_ext_pt.timestamp = getattr(aRow, 'timestamp')
        newEPL.append(new_ext_pt)
        z_range_list._include(z)

    newEPL.z_range = z_range_list
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

