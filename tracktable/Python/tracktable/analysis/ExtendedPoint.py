# Paul Schrum    Unity ID: ptschrum
# Course Project for GIS 540
"""
A module for determining circle-segment geometry when given
three coplanar points.  The primary class, ExtendedPoint, simply
carries the information about the defined circle segment after a call
to compute_arc_parameters.

Mini-Bibliography on computational geometry for circular segments (on
    the plane):
https://en.wikipedia.org/wiki/Circular_segment
http://mathworld.wolfram.com/CircularSegment.html
http://www.wsdot.wa.gov/publications/manuals/fulltext/M22-97/Chapter11.pdf

The classes in this module all assume themselves to be embedded in the plane.
For embedding on the sphere (i.e., lat/long) see module
ExtendedPointLatLong.py.

"""

__author__ = 'Paul Schrum'

import math
import collections
import tracktable.core.geomath as geomath

class Azimuth:
    """
    Convenience class which represents Azimuths (headings) so that the client
    code does not have to concern itself with handling deflection additions
    which cross 2π. Values may only be initialized via the constructor and only
    radians are expected, although the client code does not need to normalize
    the azimuth. The constructor does that for you.
    References to normalize mean reducing the value so it is between 0.0 and 2π
    """

    @staticmethod
    def _turn():
        """Private static method. Constant for one whole turn in radians.
        """
        return float(2.0 * math.pi)

    @staticmethod
    def ToDeg(inAz):
        """Takes a float: azimuth and converts it to degrees (float, not
            normalized)"""
        retDeg = 360.0 * inAz / Azimuth._turn()
        return retDeg

    @staticmethod
    def DegToAzimuthFloat(inDegree):
        retAz = inDegree * Azimuth._turn() / 360.0
        return retAz

    @staticmethod
    def CreateFromDegrees(deg):
        """Factory method. Creates an azimuth from float: degrees."""
        asAz = deg * Azimuth._turn() / 360.0
        return Azimuth(asAz)

    @staticmethod
    def _normalizeAzimuth(unNormAz):
        """Makes sure the value is between 0.0 and 2π"""
        if unNormAz > 0.0:
            normedAz = unNormAz % Azimuth._turn()
        else:
            normedAz = unNormAz * -1.0
            normedAz %= Azimuth._turn()
            normedAz *= -1.0
            normedAz += Azimuth._turn()
        return normedAz

    @staticmethod
    def _normalizeDeflection(unNormDefl):
        """Makes sure the value is between -π and π"""
        normedDefl = Azimuth._normalizeAzimuth(unNormDefl + math.pi) \
                     - math.pi
        return normedDefl

    def __init__(self, newVal):
        """ctor: expects newVal to be in radians. Will normalize
            non-normal values."""
        self.az = Azimuth._normalizeAzimuth(newVal)

    def __add__(self, deflection):
        """Add an Azimuth and a number (usually a float). Return another
            Azimuth."""
        if type(deflection) is 'Azimuth':
            raise ValueError("Adding two Azimuths not allowed. " +
                             "You can only add an Azimuth to a number.")
        return Azimuth(self.az + deflection)

    def __sub__(self, otherAz):
        retFloat = self.az - otherAz.az
        return Azimuth._normalizeDeflection(retFloat)

    def __eq__(self, otherAz):
        return math.isclose(self.az, otherAz.az)

    def __repr__(self):
        return "Azimuth: {0} or {1:.8f}°.".format(self.az, self.asDegrees())

    def asDegrees(self):
        """returns float: degrees of the given Azimuth."""
        return Azimuth.ToDeg(self.az)


if __name__ == "__main__" \
        and False:  # False to skip these tests. True to run them.

    print('Running module tests for class Azimuth')
    print()
    bigTurn = Azimuth(8.0)
    print(bigTurn)

    asDeg = Azimuth.CreateFromDegrees(180.0)
    print("180.0 az is", asDeg)
    convertedBack = asDeg.asDegrees()
    print("converted back: ", convertedBack)
    print()

    # Check Azimuth + float addition : Both in Quadrant 1
    anAz = Azimuth.CreateFromDegrees(12.0)
    aDeflection = Azimuth.DegToAzimuthFloat(13.0)
    AzActual = anAz + aDeflection; AzExpected = Azimuth.CreateFromDegrees(25.0)
    print('T1: AzActual expected: {0}, got {1}'.format(AzExpected, AzActual))
    assert AzActual == AzExpected, 'AzActual is {0}'.format(AzActual)
    print("Success"); print()

    # Check Azimuth + float addition : Quad 4 +defl in Quad1
    anAz = Azimuth.CreateFromDegrees(357.0)
    aDeflection = Azimuth.DegToAzimuthFloat(13.0)
    AzActual = anAz + aDeflection; AzExpected = Azimuth.CreateFromDegrees(10.0)
    print('T2: AzActual expected: {0}, got {1}'.format(AzExpected, AzActual))
    assert AzActual == AzExpected, 'AzActual is {0}'.format(AzActual)
    print("Success"); print()

    # Check Azimuth + float addition : Quad 1 -defl in Quad4
    anAz = Azimuth.CreateFromDegrees(10.0)
    aDeflection = Azimuth.DegToAzimuthFloat(-13.0)
    AzActual = anAz + aDeflection; AzExpected = \
        Azimuth.CreateFromDegrees(357.0)
    print('T3: AzActual expected: {0}, got {1}'.format(AzExpected, AzActual))
    assert AzActual == AzExpected, 'AzActual is {0}'.format(AzActual)
    print("Success"); print()


    # Check deflection = Azimuth2 - Azimuth1 : Both in Quad 1
    #   Result is positive
    Az2 = Azimuth.CreateFromDegrees(25.0)
    otherAz = Azimuth.CreateFromDegrees(12.0)
    defActualAz = Az2 - otherAz
    defActual = Azimuth.ToDeg(defActualAz); defExpected = 13.0
    print('Defl Test 1: expected: {0}, got {1}'.format(defExpected, defActual))
    assert math.isclose(defActual, defExpected), \
        'AzActual is {0}'.format(defActual)
    print("Success"); print()

    # Check deflection = Azimuth1 - Azimuth2 : Both in Quad 1
    #   Result is negative
    Az2 = Azimuth.CreateFromDegrees(25.0)
    Az1 = Azimuth.CreateFromDegrees(12.0)
    defActual = Azimuth.ToDeg(Az1 - Az2); defExpected = -13.0
    print('Defl Test 2: expected: {0}, got {1}'.format(defExpected, defActual))
    assert math.isclose(defActual, defExpected), 'AzActual is {0}'\
        .format(defActual)
    print("Success"); print()

    # Check deflection = Azimuth - Azimuth : Az1 in Quad 4, Az2 in Quad 1
    Az2 = Azimuth.CreateFromDegrees(357.0)
    Az1 = Azimuth.CreateFromDegrees(10.0)
    defActualAz = Az1 - Az2
    defActual = Azimuth.ToDeg(defActualAz); defExpected = 13.0
    print('Defl Test 3: expected: {0}, got {1}'.format(defExpected, defActual))
    assert math.isclose(defActual, defExpected), 'AzActual is {0}'\
        .format(defActual)
    print("Success"); print()


    # Check deflection = Azimuth - Azimuth : Az1 in Quad 1, Az2 in Quad 4
    Az2 = Azimuth.CreateFromDegrees(10.0)
    Az1 = Azimuth.CreateFromDegrees(357.0)
    defActualAz = Az1 - Az2
    defActual = Azimuth.ToDeg(defActualAz); defExpected = -13.0
    print('Defl Test 3: expected: {0}, got {1}'.format(defExpected, defActual))
    assert math.isclose(defActual, defExpected), 'AzActual is {0}'\
        .format(defActual)
    print("Success"); print()


    exit()

class ExtendedPoint(object):
    """
    Members:
        X - X value (float)
        Y - Y value (float)

              Note: Some members are not known until method
                  compute_arc_parameters is called.
        Derived Members:
        arc (object) - values related to the arc this point is part of
            arc.degreeCurve  (float) - degree of curve based on deflection
                over 1 unit (meters or feet - on any Planar Coordinate
                System) Derived by equation, set by method, not set by user
            arc.radius (float) radius
            arc.curveCenterPoint (Point or Extended Point) - Circular curve
                center point related to this point (self) as set by method call
            arc.lengthBack (float) - distance along the arc back to the
                previous point.
            arc.lengthAhead (float) distance along the arc ahead to the
                next point
            arc.deflection - total deflection from back point to ahead point
                as deflected along the arc defined by the three points. Value
                interpreted as radians.
            arc.radiusStartVector - vector from curve center to
                Point1 (begin point)
            arc.radiusEndVector - vector from curve center to Point3 (end point
            arc.chordVector - vector from point1 to point2
        pt2pt (object) - values related to the points as the vertex of
            a triangle.
            pt2pt.distanceBack (float) - chord distance to previous point
            pt2pt.distanceAhead (float) - chord distance to next point
            pt2pt.deflection (float) -  deflection chord to chord interpreted
                as radians.
    Methods:
        compute_arc_parameters - given 3 points, it computes parameters
            for the arc which passes through the three given points.
            Side Effect: All parameters are attached to the second
            ExtendedPoint parameter.
    """

    def __init__(self, aPoint, newY=None, newZ=None):
        """
        ctor for an Extended Point
        :param aPoint: anything with an X (float) and Y(float).
                If aPoint is a number, then newY must be define (also a number)
        :param newY: If aPoint is really X(float), then newY is the Y (float)
        :return: None
        """
        if newY is None:
            self.X = aPoint.X
            self.Y = aPoint.Y
            self.Z = getattr(aPoint, 'Z', None)
        else:
            self.X = aPoint
            self.Y = newY
            self.Z = newZ
        self.pt2pt = False
        self.arc = False

    def __repr__(self):
        return '{0}, {1}: Mag {2}  Az {3}'.format(self.X,
                                                  self.Y,
                                                  self.magnitude,
                                                  self.azimuth)

    def __str__(self):
        mainString = '{0},{1}'.format(self.X, self.Y)

        if self.pt2pt:
            p2pString = """,{0},{1},{2}
                """.format(cvt_radians_to_degrees(self.pt2pt.deflection),
                           self.pt2pt.distanceBack,
                           self.pt2pt.distanceAhead)
            p2pString = "".join(p2pString.split())
        else:
            p2pString = ',,'

        if self.arc:
            arcString = """,{0},{1},{2},{3},{4},{5}
            """.format(self.arc.degreeCurve100,
                       self.arc.radius,
                       cvt_radians_to_degrees(self.arc.deflection),
                       cvt_radians_to_degrees(self.arc.chordVector.azimuth),
                       self.arc.lengthBack,
                       self.arc.lengthAhead
                       )
            arcString = "".join(arcString.split())
        else:
            arcString = ',,,,'

        return mainString + arcString + p2pString

    def __add__(self, other):
        return ExtendedPoint(self.X + other.X,
                             self.Y + other.Y)

    def __sub__(self, other):
        newPoint = ExtendedPoint(other.X - self.X,
                             other.Y - self.Y)
        return newPoint

    @property
    def magnitude(self):
        return math.sqrt(self.X * self.X + self.Y * self.Y)

    @property
    def azimuth(self):
        return math.atan2(self.X, self.Y)

    def __hash__(self):
        return self.X - self.Y + (self.X % 17)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return self.spatiallyEquals(other, tolerance=0.0055)

    def spatiallyEquals(self, other, tolerance=0.015):
        """
        Determines whether this and the other are at the same spatial
        location within a certain tolerance
        :param other: Other point to compare against
        :param tolerance: Axis-based distance to compare for spatial equality
        :return: True if the two points are within tolerance of each other on
                both axes.
        """
        if math.fabs(self.X -other.X) > tolerance:
            return False
        if math.fabs(self.Y - other.Y) > tolerance:
            return False
        return True;

    def distanceTo(self, otherPt):
        return ((otherPt.X - self.X)** 2 + (otherPt.Y - self.Y)**2)** 0.5

    def deflectionTo(self, otherPt, preferredDir=None):
        """When interpreting both ExtendedPoints as Vectors, return the
            deflection (in units of radians). Negative deflection is left.
        :param otherPt: ExtendedPoint to be compared with for computation of
            deflection
        :param longSolution: if True, compute deflection the long way around
            the circle
        :return: a namedTuple of the interior solution azimuth and the
            exterior solution azimuth
        :rtype: namedTuple AzimuthPair
        """
        defl = otherPt.azimuth - self.azimuth
        if defl < -1.0 * math.pi:
            interiorDeflection = defl + 2 * math.pi
            exteriorDeflection = defl
        elif defl > math.pi:
            interiorDeflection = defl - 2 * math.pi
            exteriorDeflection = defl
        else:
            interiorDeflection = defl
            if defl > 0.0:
                exteriorDeflection = defl - 2 * math.pi
            else:
                exteriorDeflection = defl + 2 * math.pi
        if preferredDir == None:
            return AzimuthPair(interiorSolution = interiorDeflection,
                                exteriorSolution = exteriorDeflection)
        elif math.copysign(1, exteriorDeflection) == \
                math.copysign(1, preferredDir):
            return exteriorDeflection
        return interiorDeflection

    @staticmethod
    def header_list():
        return 'X,Y,Degree,Radius,ArcDeflection,ChordDirection,' + \
               'PointsDefl,DistanceBack,DistanceAhead,ArcLengthBack,' + \
               'ArcLengthAhead'

AzimuthPair = collections.namedtuple('AzimuthPair',
                                     'interiorSolution exteriorSolution')

def cvt_radians_to_degrees(rad):
    return rad * 180.0 / math.pi

class struct():
    """
    Named for and serving a similar purpose as the C concept of Struct.
    This class exists as something to add attributes to dynamically.
    (Python would not let me do this with Object, so struct.)
    """
    pass

def any_in_point_equals_any_in_other(pointList, other, tolerance=0.005):
    """
    True if any point in pointList equals and point in other
    :param pointList: iterable of Points
    :param other: iterable of Points
    :return: False or Tuple of matching indices
    :rtype: False or Tuple
    """
    for index1, pt1 in enumerate(pointList):
        for index2, pt2 in enumerate(other):
            if pt1.spatiallyEquals(pt2, tolerance):
                return (index1, index2)
    return False

class IntersectionError(Exception):
    def __init__(self, newMessage=None):
        if(newMessage == None):
            self.message =  "No intersection found for the two items."
        else:
            self.message = newMessage

class Ray2D():
    """
    Represents a bidirectional ray, usually used for finding intersections.
    Also known as a line (as in, unbounded line).
    If the ray is vertical, slope and yIntercept are float("inf")
    """
    def __init__(self, extendedPt, azimuth):
        self.extendedPoint = extendedPt
        self.azimuth =  azimuth
        acos = math.cos(azimuth)
        asin = math.sin(azimuth)
        if azimuth == 0.0:
            self._slope = float("inf")
        elif azimuth == math.pi:
            self._slope = float("inf")
        else:
            self._slope = math.cos(azimuth) / math.sin(azimuth)
        self._yIntercept = extendedPt.Y - self.slope * extendedPt.X

    @property
    def slope(self):
        return self._slope

    @property
    def yIntercept(self):
        return self._yIntercept

    def __repr__(self):
        if self.slope == float(inf):
            str = 'Vertical @ X = {0}'.format(self.extendedPoint.X)
        else:
            str = 'Slope: {0}  yIntercept: {1}'.format(self.slope,
                                                       self.yIntercept)
        return str

    def given_X_get_Y(self, xValue):
        """Return Y using the y = mx + b equation of a line."""
        return self.slope * xValue + self.yIntercept

    def given_Y_get_X(self, yValue):
        """Return X using y = mx + b solved for x."""
        if self.slope == float("inf"):
            return self.extendedPoint.X
        return (yValue - self.yIntercept) / self.slope

    def intersectWith(self, otherRay):
        """
        Given this ray and another, find the intersection point of the two.
        :param otherRay: Ray to be intersected
        :return: ExtendedPoint of the Intersection
        :raises: IntersectionError if rays are parallel
        """
        if self.azimuth == otherRay.azimuth or \
                (self.slope - otherRay.slope) == 0.0:
            raise IntersectionError()
        if math.isinf(otherRay.slope):
            newX = otherRay.extendedPoint.X
            newY = self.yIntercept + self.slope * newX
        elif math.isinf(self.slope):
            newX = self.extendedPoint.X
            newY = otherRay.yIntercept + otherRay.slope * newX
        else:
            yInt = self.yIntercept
            newX = (otherRay.yIntercept - yInt) / \
                 (self.slope - otherRay.slope)
            newY = self.yIntercept + self.slope * newX
        return ExtendedPoint(newX, newY)

    @staticmethod
    def get_csv_header_string():
        return 'X,Y,ArcDeflection,DegreeCurve,DegreeCurveEnglish,' + \
                'Radius,'

    @staticmethod
    def get_bisecting_normal_ray(firstPt, otherPt):
        """
        Given this point and another, return the ray which bisects the
            line segment between the two.
        :rtype: Ray2D
        :param otherPt: Second point of the line segment to be bisected.
        :return: Ray2d with origin point at the bisector of the line segment
            and ahead direction 90 degrees to the right of the line segment.
        """
        if otherPt.pt2pt:
            distBack = otherPt.pt2pt.distanceBack
        else:
            distBack = getDist2Points(firstPt, otherPt)
        az12 = getAzimuth(firstPt, otherPt)
        halfVec12 = vectorFromDistanceAzimuth(distBack / 2.0, az12)
        midPoint12 = firstPt + halfVec12
        return Ray2D(midPoint12, az12 + math.pi / 2.0)

def getDist2Points(p1, p2):
    """
    returns the distance between two points.
    :param p1: First point (required)
    :param p2: Second point (required)
    :return: float of the distance
    """
    return ((p2.X - p1.X)** 2 + (p2.Y - p1.Y)**2)** 0.5

def getAzimuth(p1, p2):
    """
    Returns the Azimuth of the vector between the two points in which
            0.0 is North, positive is clockwise, and 0.0 <= Azimuth < 360.0
    :param p1: First Point (required)
    :param p2: Second Point (required)
    :return: float of the Azimuth.
    """
    dy = p2.Y - p1.Y
    dx = p2.X - p1.X
    return math.atan2(dx, dy)

def vectorFromDistanceAzimuth(length, az):
    """
    Given a vector in the form of length and azimuth,
        compute the vector values of dX and dY.
    :rtype: ExtendedPoint
    :param length: length of the vector
    :param az: azimuth of the vector
    :return: ExtendedPoint with values X =dX, Y = dY, being considered a vector
    """
    dx = length * math.sin(az)
    dy = length * math.cos(az)
    return ExtendedPoint(dx, dy)

def normalizeAzimuth(defl):
    returnDef = defl
    if defl < 0.0:
        returnDef = defl + 2.0 * math.pi
    elif defl > 2.0 * math.pi:
        returnDef = defl - 2.0 * math.pi
    return returnDef

def normalizeDeflection(defl):

    returnDef = defl
    if defl < -2.0 * math.pi:
        returnDef = defl + 2.0 * math.pi
    elif defl > 2.0 * math.pi:
        returnDef = defl - 2.0 * math.pi
    return returnDef

def compute_arc_parameters(point1, point2, point3):
    """
    Computes all relevatnt parameters to the trio of points.
    Side Effects: The computed parameters are added to pt2.
    Assumptions: Total arc deflection from point1 to point3 is less than
            180 degrees.
            Todo: Revisit this assumption for hi deflection point triples.
    :param point1: Back point
    :param point2: Current point
    :param point3: Ahead point
    :requirement: Each point must have X and Y values (note capitals).
    :return: None
    """
    point2.pt2pt = struct()
    point2.pt2pt.distanceBack = getDist2Points(point2, point1)
    point2.pt2pt.distanceAhead = getDist2Points(point3, point2)
    azimuth12 = getAzimuth(point1, point2)
    azimuth23 = getAzimuth(point2, point3)
    defl = Azimuth._normalizeDeflection(azimuth23 - azimuth12)

    deflSign = 1
    if defl < 0:
        deflSign = -1
    point2.pt2pt.deflection = defl

    point2.arc = struct()
    point2.arc.chordVector = point1 - point3

    if defl == 0.0:
        point2.arc.degreeCurve = 0.0
        point2.arc.degreeCurve100 = 0.0
        point2.arc.radius = float('inf')
        point2.arc.curveCenter = False
        point2.arc.lengthBack = False
        point2.arc.lengthAhead = False
        point2.arc.radiusStartVector = False
        point2.arc.radiusEndVector = False
        point2.arc.deflection = 0.0
        point2.arc.ArcLengthBack = 0.0
        point2.arc.ArcLengthAhead = 0.0
        return

    # compute Center point of resulting arc
    # taken from http://stackoverflow.com/a/22792373/1339950
    # Answer to:
    # "Algorithm to find an arc, its center, radius and angles given 3 points"

    # Get the ray bisecting and normal to secant12 and secant23
    biRay12 = Ray2D.get_bisecting_normal_ray(point1, point2)
    biRay23 = Ray2D.get_bisecting_normal_ray(point2, point3)

    cc = biRay12.intersectWith(biRay23)
    point2.arc.curveCenter = cc

    radStartV = cc - point1
    point2.arc.radius = radStartV.magnitude
    point2.arc.radiusStartVector = radStartV
    radEndV = cc - point3
    point2.arc.radiusEndVector = radEndV
    point2.arc.degreeCurve = 1.0 / point2.arc.radius
    point2.arc.deflection = radStartV.deflectionTo(radEndV, preferredDir=defl)

    p2Vector = point2.arc.curveCenter - point2
    defl12 = p2Vector.azimuth - point2.arc.radiusStartVector.azimuth
    defl23 = point2.arc.deflection - defl12
    point2.arc.lengthBack = defl12 * point2.arc.radiusStartVector.magnitude
    point2.arc.lengthAhead = defl23 * point2.arc.radiusStartVector.magnitude
    point2.arc.length =point2.arc.lengthBack + point2.arc.lengthAhead
    point2.arc.degreeCurve = deflSign / point2.arc.radius
    point2.arc.degreeCurve100 = 100.0 * \
                               cvt_radians_to_degrees(point2.arc.degreeCurve)


def _assertFloatsEqual(f1, f2):
    """Test whether two floats are approximately equal.
    The idea for how to add the message comes from
    http://stackoverflow.com/a/3808078/1339950
    """
    customMessage = "{0} (Actual) does not equal {1} (Expected)".format(f1, f2)
    assert math.fabs(f1 - f2) < 0.000001, customMessage

def _assertPointsEqualXY(p1, p2):
    """Test whether two points are approximately equal.
    Only tests equality of X and Y.  Other extended properties
    are ignored
    """
    customMessage = "{0} does not equal {1}".format(p1, p2)
    assert math.fabs(p1.X - p2.X) < 0.000001, customMessage
    assert math.fabs(p1.Y - p2.Y) < 0.000001, customMessage

if __name__ == '__main__':
    print('running module tests for ExtendedPoint.py')
    print()

    # Test Point Creation by 2 floats
    point1 = ExtendedPoint(10.0, 20.0)
    assert point1.X == 10.0
    assert point1.Y == 20.0

    point2 = ExtendedPoint(20.0, 25.0)
    distance12 = getDist2Points(point1, point2)
    expected = 11.18033989
    _assertFloatsEqual(distance12, expected)

    azmuth12 = getAzimuth(point1, point2)
    expected = 1.10714940556
    _assertFloatsEqual(azmuth12, expected)

    #Test point equality and hashing.
    point98 = ExtendedPoint(20.0, 25.0)
    point99 = ExtendedPoint(20.01, 25.01)
    _assertPointsEqualXY(point2, point98)
    assert(point2 == point98)
    assert(point2 != point99)
    assert(point2.__hash__() == point98.__hash__())
    assert(point2.__hash__() != point99.__hash__())

    # Test vector creation
    vec12 = vectorFromDistanceAzimuth(distance12, azmuth12)
    expected = ExtendedPoint(10.0, 5.0)
    _assertPointsEqualXY(vec12, expected)

    # Test add Point to Point (treated as a Vector)
    point3 = point1 + point2
    expected = ExtendedPoint(30.0, 45.0)
    _assertPointsEqualXY(point3, expected)

    # Test 2D Ray Creation
    az = math.pi * 0.75
    aRay = Ray2D(point1, az)
    expected = -1.0
    _assertFloatsEqual(aRay.slope, expected)
    expected = 30.0
    _assertFloatsEqual(aRay.yIntercept, expected)

    az = math.pi / 4.0
    anotherRay = Ray2D(point2, az)
    expected = 1.0
    actual = anotherRay.given_Y_get_X(6.0)
    _assertFloatsEqual(actual, expected)
    expected = 6.0
    actual = anotherRay.given_X_get_Y(1.0)
    _assertFloatsEqual(actual, expected)

    # Test ray intersecting another ray
    point4 = aRay.intersectWith(anotherRay)
    expected = ExtendedPoint(12.5, 17.5)
    _assertPointsEqualXY(point4, expected)

    # Test ray intersecting a vertical ray
    verticalRay = Ray2D(ExtendedPoint(11.0, 1.0), math.pi)
    point5 = aRay.intersectWith(verticalRay)
    expected = ExtendedPoint(11.0, 19.0)
    _assertPointsEqualXY(point5, expected)

    point5 = verticalRay.intersectWith(aRay)
    expected = ExtendedPoint(11.0, 19.0)
    _assertPointsEqualXY(point5, expected)

    # Test get_bisecting_normal_ray
    p1 = ExtendedPoint(0, 0)
    p2 = ExtendedPoint(10, 10)
    aRay = Ray2D.get_bisecting_normal_ray(p1, p2)
    expected = ExtendedPoint(5.0, 5.0)
    _assertPointsEqualXY(aRay.extendedPoint, expected)
    expected = -1.0
    _assertFloatsEqual(aRay.slope, expected)
    expected = 10
    _assertFloatsEqual(aRay.yIntercept, expected)

    # test creation of arc values from 3 points
    # the attributes are added to pt2.
    pt2Coord = (9.0 / math.sqrt(2.0)) + 1.0
    p1 = ExtendedPoint(1,10)
    p2 = ExtendedPoint(pt2Coord, pt2Coord)
    p3 = ExtendedPoint(10,1)
    compute_arc_parameters(p1, p2, p3)
    someStr = str(p1)
    someStr = str(p2)
    expected = ExtendedPoint(1,1)
    _assertPointsEqualXY(p2.arc.curveCenter, expected)
    expected = 1.0 / 9.0
    _assertFloatsEqual(p2.arc.degreeCurve, expected)
    expected = math.pi / 2.0
    _assertFloatsEqual(p2.arc.deflection, expected)
    expected = 9.0 * math.pi / 4.0
    _assertFloatsEqual(p2.arc.lengthAhead, expected)
    _assertFloatsEqual(p2.arc.lengthBack, expected)

    # Test deflections which cross due north
    p1 = ExtendedPoint(-1.0, 1.0)
    p2 = ExtendedPoint(2, 2)
    expected = AzimuthPair(math.pi / 2.0, -2 * math.pi + math.pi / 2.0)
    az12 = p1.deflectionTo(p2)
    _assertFloatsEqual(az12.interiorSolution, expected.interiorSolution)
    _assertFloatsEqual(az12.exteriorSolution, expected.exteriorSolution)
    az21 = p2.deflectionTo(p1)
    expected = AzimuthPair(- expected[0], - expected[1])
    _assertFloatsEqual(az21.interiorSolution, expected.interiorSolution)
    _assertFloatsEqual(az21.exteriorSolution, expected.exteriorSolution)

    print('tests successfully completed.')