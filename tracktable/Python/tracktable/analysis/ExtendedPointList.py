import sys, csv, os
# sys.path.append(os.getcwd())
from tracktable.analysis.ExtendedPoint import ExtendedPoint as EP
import tracktable.analysis.ExtendedPoint as ExtendedPoint

__author__ = ['Paul Schrum']

class ExtendedPointList(list):
    def computeAllPointInformation(self):
        """
        For each triplet of points in the list of points, compute the
        attribute data for the arc (circular curve segment) that starts
        at point 1, passes through point 2, and ends at point 3.  Then
        assign the curve data to point 2 for safe keeping.
        :param self: This list of points to be analyzed. These must be ordered
                    spatially or the results are meaningless.
        :return: None
        """
        for pt1, pt2, pt3 in zip(self[:-2],
                                 self[1:-1],
                                 self[2:]):
            ExtendedPoint.compute_arc_parameters(pt1, pt2, pt3)

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

def _createExtendedPointList_trajectory(trajectory):
    """
    Args:
        trajectory: An np array of points. X is [0], Y is [1]
            Z is optional and would be [2]

    Returns: New instance of an ExtendedPointList.
    """
    xIndex = 0; yIndex = 1; zIndex = 2;
    newEPL = ExtendedPointList()
    if len(trajectory[0]) == 3:
        for aRow in trajectory:
            x = aRow[xIndex]
            y = aRow[yIndex]
            z = aRow[zIndex]
            newEPL.append(EP(x, y, z))
    elif len(trajectory[0]) == 2:
        for aRow in trajectory:
            x = aRow[xIndex]
            y = aRow[yIndex]
            newEPL.append(EP(x, y))
    else:
        raise ValueError('trajectory matrix must have 2 or 3 columns.')

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

