# Copyright (c) 2014-2017 National Technology and Engineering
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

import networkx as nx
import numpy as np
from math import sqrt, fabs

import scipy
from tracktable.analysis.sliceList import SliceList
from tracktable.analysis.sliceList import sliceRange as slice_range_class
import tracktable.analysis.ExtendedPoint
from tracktable.analysis.ExtendedPointList import ExtendedPointList as EPL
import tracktable.analysis.ExtendedPointList as EPLmod
import tracktable.analysis.sliceList as SL
import types
from math import isclose
from collections import defaultdict
import math

class NormalizedDistanceMatrix:
    """Generates a matrix giving the ratio of the distance along each
    sub-trajectory to the distance from the start to the end of that
    sub-trajectory"""

    def __init__(self, coords, threshold=1.1):
        self.dist_mat = np.zeros(shape=(len(coords), len(coords)))
        self.threshold = threshold

        for x in range(1, len(coords)):
            self.dist_mat[0, x] = \
            self.dist(coords[x], coords[x-1]) + self.dist_mat[0,x-1]
            self.dist_mat[x, 0] = self.dist_mat[0, x]

        for start in range(1, len(coords)):
            for end in range(start+1, len(coords)):
                self.dist_mat[start,end] = \
                self.dist_mat[start-1, end] - self.dist_mat[start-1,start]
                self.dist_mat[end,start] = self.dist_mat[start,end]

        #ratio of distance traveled to separation distance of start and end
        self.norm_dist_mat = np.copy(self.dist_mat)
        for start in range(0, len(coords)):
            for end in range(start+1, len(coords)):
                dist = self.dist(coords[start], coords[end])
                if dist != 0.0:
                    self.norm_dist_mat[start,end] /= self.dist(coords[start],
                                                               coords[end])
                else:
                    self.norm_dist_mat[start,end]= 0.0 #is this okay?
                self.norm_dist_mat[end,start] = self.norm_dist_mat[start,end]

    def squared_dist(self, a, b):
        return (b[0] - a[0])*(b[0] - a[0]) + (b[1] - a[1])*(b[1] - a[1])

    def dist(self, a, b):
        return sqrt(self.squared_dist(a,b))

    def is_straight(self, start, end):
        return self.norm_dist_mat[start,end] < self.threshold

class SubTrajerStraight:
    'Splits a trajectory into straight-ish segments'
    def __init__(self, straightness_threshold=1.1, length_threshold_samples=2): #2 is minimum
        self.threshold = straightness_threshold
        self.length_threshold_samples = length_threshold_samples
        self.currentNodeIndex = 1 #change to 0
        self.norm_dist_mat = NormalizedDistanceMatrix([]) #todo better way?

    def split_at_indices(self, indices, start, end):
        """returns a list of index pairs, and/or "None" objects.  Even
        elements are not straight segments or are None.  Odd elements are the
        straight segments"""
        segments = []
        remainderStart = start
        remainderEnd = end
        for i in indices:
            if i >= remainderStart:
                if i == start:
                    segments.append(None)
                elif i== remainderStart:
                    segments.append(None)
                else:
                    segments.append([remainderStart, i])
                    remainderStart = i
            else: #overalpping segments, ignore second one.  TODO, later may
                #want to use a better way to determine which overlapping
                #segment to use
                segments.append(None)
        if remainderStart == remainderEnd:
            segments.append(None)
        else:
            segments.append([remainderStart, remainderEnd])
        return segments

    def longest_straight_segments(self, G, coords, thisIndex,
                                       start_length, start, end):
        if start_length >= (end-start+1):
            start_length = end-start
        #print(start, end, start_length)
        if (not self.norm_dist_mat.is_straight(start, end)) and (end-start+1) > self.length_threshold_samples :
            indices = []
            new_start_length = start_length
            for segment_length in range(start_length, 1, -1):
                num_segments_of_length = ((end-start+1)-segment_length)+1
                for start_index in range(num_segments_of_length):
                    end_index = start_index+segment_length-1
                    if self.norm_dist_mat.is_straight(start_index+start,
                                                         end_index+start):
                        indices.append(start_index+start)
                        indices.append(end_index+start)
                if indices:
                    new_start_length = segment_length-1
                    break
            segs = self.split_at_indices(indices, start, end)
            for i in range(len(segs)):
                if i%2 == 0: #even = not straight, recurse
                    if segs[i] != None:
                        G.add_node(self.currentNodeIndex, s=segs[i][0],
                                   e=segs[i][1])
                        G.add_edge(thisIndex, self.currentNodeIndex)
                        self.currentNodeIndex+=1
                        self.longest_straight_segments(G, coords,
                                                       self.currentNodeIndex-1,
                                                       new_start_length,
                                                       segs[i][0],
                                                       segs[i][1])
                else: #odd = straight, make leaf node
                    G.add_node(self.currentNodeIndex, s=segs[i][0],
                               e=segs[i][1])
                    G.add_edge(thisIndex, self.currentNodeIndex)
                    self.currentNodeIndex+=1

    def subtrajectorize(self, trajectory, returnGraph=False): #can take coordinate list or a trajectory.
        coordinates = []
        for point in trajectory: #make into coordinate list
            coordinates.append([point[0], point[1]])
        self.currentNodeIndex = 1
        self.norm_dist_mat = NormalizedDistanceMatrix(coordinates,
                                                      threshold=self.threshold)

        G = nx.DiGraph()
        start = 0
        end = len(coordinates)-1
        G.add_node(self.currentNodeIndex, s=start, e=end)
        self.currentNodeIndex += 1
        self.longest_straight_segments(G, coordinates, 1,
                                            len(coordinates), start, end)
        leaves = [(G.node[x]['s'], G.node[x]['e'])
                  for x in G.nodes() if G.out_degree(x)==0 and
                  G.in_degree(x)==1]
        if len(G) == 1:
            leaves = [(G.node[1]['s'], G.node[1]['e'])] #just root node #change 1's to 0's

        if returnGraph:
            return leaves, G
        else:
            return leaves

class SubTrajerAccel:
    'Splits a trajectory where the change in accelleration exceeds some threshold'
    def __init__(self, accel_threshold=0.025, tight=False): #not tight means include segment before and after a turn
        self.accel_threshold = accel_threshold
        self.tight = tight
        self.currentNodeIndex = 1 #change to 0

    def acceleration(self, coords):  #x as array and y's as array   array 2,N
        first = scipy.gradient(coords)[1]  #Derivative along columns is result [1]
        second = scipy.gradient(first)[1]
        mag = np.sqrt(second[0]**2 + second[1]**2)
        return mag

    def find_turns(self, acc):
        if self.tight:
            return np.where(acc > self.accel_threshold, True, False)[:-1]
        else:
            bin_acc = np.concatenate([[True], np.where(acc > self.accel_threshold, True, False)])
            bin_acc = (bin_acc[:-1] + bin_acc[1:])[:-1] #segment before AND after are part of the curve
            return bin_acc

    def subtrajectorize(self, trajectory, returnGraph=False): #can take coordinate list or a trajectory.
        coordinates = []
        for point in trajectory: #make into coordinate list
            coordinates.append([point[0], point[1]])
        #print(len(coordinates))

        coords = np.array(coordinates).transpose()
        acc = self.acceleration(coords)
        bin_acc = self.find_turns(acc)
        #print(bin_acc)
        #print(len(bin_acc))
        shifts = [bin_acc[:-1] != bin_acc[1:]]
        #print(shifts)
        inflections = np.argwhere(shifts)#.flatten()
        #print(inflections[:,1])
        leaves = []
        prev = 0
        for inf in inflections[:,1]:
            leaves.append((prev, inf+1))
            prev = inf+1
        leaves.append((prev, len(coordinates)-1)) #add a segment to the end
        return leaves
        #print("********8")
        #print(leaves)
        #[0 1 4 16
        #1      2     5     17    end
        #(0 1) (1 2) (2 5) (5 17) (17 19)

        #for i in range(len(bin_acc)):
            
        #bin_mag[:-1]!=bin_mag-1:]
        #inflections = np.argwhere(shifts).flatten()
        #inflections = np.conacat(....
        #print(bin_acc)
        
        #self.currentNodeIndex = 1 #todo duplicate
        
        #G = nx.DiGraph()
        #start = 0
        #end = len(coordinates)-1
        #G.add_node(self.currentNodeIndex, s=start, e=end)
        #self.currentNodeIndex += 1
        #self.longest_straight_segments(G, coordinates, 1,
        #                                    len(coordinates), start, end)
        #leaves = [(G.node[x]['s'], G.node[x]['e'])
        #          for x in G.nodes() if G.out_degree(x)==0 and
        #          G.in_degree(x)==1]
        #if len(G) == 1:
        #    leaves = [(G.node[1]['s'], G.node[1]['e'])] #just root node #change 1's to 0's

        #if returnGraph:
        #    return leaves, G
        #else:
        #    return leaves



class SubTrajerSemantic:
    'Splits a trajectory into straight-ish segments'
    def __init__(self, straightness_threshold=1.1, length_threshold_samples=2): #2 is minimum
        self.threshold = straightness_threshold
        self.length_threshold_samples = length_threshold_samples
        self.currentNodeIndex = 1 #change to 0
        self.norm_dist_mat = NormalizedDistanceMatrix([]) #todo better way?

    def subtrajectorize(self, trajectory, returnGraph=False): #can take coordinate list or a trajectory.
        coordinates = []
        for point in trajectory: #make into coordinate list    #todo duplicated in example_sub_trajectorize.  Consolidiate
            if 'altitudes' in point.properties.keys(): #add altitude if exists
                coordinates.append([point[0], point[1], point.properties['altitudes']])
                #print(len(coordinates)-1, point.properties['altitudes']) #remove
            else:
                coordinates.append([point[0], point[1], None])

        self.currentNodeIndex = 1
        self.norm_dist_mat = NormalizedDistanceMatrix(coordinates,
                                                      threshold=self.threshold)
        takeoffThreshold = 10500
        landingThreshold = 10500
        cruisingThreshold = 0.00033 #essentially 33% of the flight must be in a bin?   not sure this is good or not
        lastSample = len(coordinates)-1
        #start out by removing the takeoff and landing.
        takeOffEnd=0
        if coordinates[0][2]: #has altitude
            if coordinates[0][2] < takeoffThreshold: #starts less than 10k feet
                print("has alt at start less 10k", coordinates[0][2])
                for i in range(1,lastSample):#find where crosses 10k ft
                    if coordinates[i][2] > takeoffThreshold:
                        takeOffEnd = i
                        break
                print("take off ends at sample ", takeOffEnd)
        #isolate landing based on altitude
        landingStart= lastSample
        if coordinates[lastSample][2]: #has altitude
            if coordinates[lastSample][2] < landingThreshold: #starts less than 10k feet
                for i in range(lastSample,-1, -1):#find where crosses 10k ft
                    if coordinates[i][2] > landingThreshold:
                        landingStart = i
                        break
                print("landing starts at sample ", landingStart)

        cruisingStart = None
        cruisingEnd = None
        #todo, below we must quit if there is not altituted values?
        h = np.histogram(list(zip(*coordinates))[2], bins=np.append(np.append(0, np.arange(10500,46500,1000)), 60000), density=True)  #to determine where the cruising altitude was?
        if np.max(h[0]) > cruisingThreshold: #multiply by 1000 to get approx ratio of samples in this bin
            cruisingBin = np.argmax(h[0])
            cruisingMin = h[1][cruisingBin]
            cruisingMax = h[1][cruisingBin+1]
            for i in range(takeOffEnd, landingStart):
                if coordinates[i][2] > cruisingMin:
                    cruisingStart = i
                    print("cruising starts at sample ", cruisingStart)
                    break
            for i in range(landingStart, takeOffEnd, -1):
                if coordinates[i][2] > cruisingMin:
                    cruisingEnd = i
                    print("descent starts at sample ", cruisingEnd)
                    break


        #need to check below if not found
        segments = [(0,takeOffEnd), (takeOffEnd, cruisingStart), (cruisingStart, cruisingEnd), (cruisingEnd, landingStart), (landingStart, lastSample)] #later add sub setments
        return segments
#        G = nx.DiGraph()
#        start = takeOffEnd
#        end = landingStart
#        G.add_node(self.currentNodeIndex, s=start, e=end)
#        self.currentNodeIndex += 1
#        self.longest_straight_segments(G, coordinates, 1,
#                                            len(coordinates), start, end)
#        leaves = [(G.node[x]['s'], G.node[x]['e'])
#                  for x in G.nodes() if G.out_degree(x)==0 and
#                  G.in_degree(x)==1]
#        if len(G) == 1:
#            leaves = [(G.node[1]['s'], G.node[1]['e'])] #just root node #change 1's to 0's
#
#        if returnGraph:
#            return leaves, G
#        else:
#            return leaves

        #take off
        #climb
        #cruise
        #descent
        #landing

def trajName(traj):
    return traj[0].object_id


_isSubTrajerCurvatureAvailable = True

def compute_everything_else(aVar: tracktable.analysis.ExtendedPoint)\
        -> tuple:
    return 0.0, 0.2

class SubTrajerCurvature:
    """Breaks up a trajectory into subtrajectories based on curvatures of
    each point triplet. Multiple approaches to consolidating sequential
    curvature values into point ranges are available."""
    def __init__(self):
        if not _isSubTrajerCurvatureAvailable:
            raise NotImplementedError(
                "The class SubTrajerCurvature is not available due " +
                "to import issues.")

    def _pyramidGrowingWindowMethod(self, aPointList):
        """
        A possible nuther method which considers growing windows on a pyramid
            (multipass) sampling approach instead of a sequential sampling
            approach like movingGrowingWindow does.
        :param aPointList: sequence of points constituting the trajectory
        :type aPointList: ExtendedPointList
        :return: all subtrajectories
        :rtype: SliceList
        """
        raise NotImplementedError('Try this later.')

    def _movingGrowingWindowMethod(self, aPointList):
        """
        Overlaps each slice a little, takes mean and stdev of curvature for
            each slice, compares stdev, consolidates slices when the stdevs
            of two adjacent slices are close to each other. When they are,
            the consolidation causes the window to grow towards the right.
        :param aPointList: sequence of points constituting the trajectory
        :type aPointList: ExtendedPointList
        :return: all subtrajectories
        :rtype: SliceList
        """

        # Create a profile, x = length along, y = Degree of Curve
        dcProfile = []
        accumulatedX = 0.0
        myIndex = 1
        for pt in aPointList[1:-1]:
            accumulatedX += pt.pt2pt.distanceBack

            # SimpleNamespace is
            # from https://stackoverflow.com/a/13828824/1339950
            length_degree_pair = \
                types.SimpleNamespace(x = accumulatedX,
                                      degC=pt.arc.degreeCurve,
                                      rad=pt.arc.radius,
                                      myIndex=myIndex,
                                      chordAzimuth=pt.arc.chordVector.azimuth,
                                      deflection=pt.pt2pt.deflection)

            dcProfile.append(length_degree_pair)
            myIndex += 1

        import statistics
        def computeParams(aSliceRange):
            aSegment = aSliceRange.getSegment()
            extractedListDc = [x.degC for x in aSegment]
            aSliceRange.DcAve = statistics.mean(extractedListDc)
            # try:
            aSliceRange.DcStdDev = statistics.stdev(extractedListDc)

        aSliceList = SliceList(dcProfile, RangeWidth=5, Overlap=3,
                               computeParams=computeParams)

        print("Using the Moving/Growing Window Method.")
        print(); print('Length before consolidation: {0}'
                       .format(len(aSliceList)))
        predicate = lambda a, b: isclose(a.DcStdDev, b.DcStdDev, abs_tol=0.01)
        aSliceList.consolidateNodeIf(predicate)
        print(); print('Length after  consolidation: {0}'
                       .format(len(aSliceList)))

        # aSliceList.computeAttribs
        predicate = lambda a, b: int(a.DcStdDev // 6) == 0 and \
                                 int(b.DcStdDev // 6) == 0

        aSliceList.consolidateNodeIf(predicate)
        predicate = lambda a, b: int(a.DcStdDev // 6) > 0 and \
                                 int(b.DcStdDev // 6) > 0

        aSliceList.consolidateNodeIf(predicate)
        return aSliceList

    def _individCurvaturesMethod(self, aPointList, dcStraightThreshold=4.0):
        """
        First, classifies each point triplet as curved or straight based on
            a Degree of Curve threshold. Then consolidates slices when two
            adjacent slices have the same classification.
            Suggested by Ben Newton.
        :param aPointList: sequence of points constituting the trajectory
        :type aPointList: ExtendedPointList
        :param dcStraightThreshold: border between classifying a point triplet
            as straight or curved.
        :type dcStraightThreshold: float (positive)
        :return: all subtrajectories
        :rtype: SliceList
        """

        segmentPrimitives = ['straight', 'turn']

        def tag_zigzag_segments(aSliceRange):
            aSegment = aSliceRange.getSegment()

            aSliceRange.DegreeOfCurve = 'straight' \
                if fabs(aSegment[0].arc.degree_curvature) < dcStraightThreshold \
                else 'turn'

            # aSliceRange.DegreeOfCurve = 'straight' \
            #     if aSegment[0].may_be_zigzag \
            #     else 'turn'
            aSliceRange.color = slice_range_class.straight_color
            if aSliceRange.DegreeOfCurve is not 'straight':
                aSliceRange.color = slice_range_class.turn_color

        aPointList.categorize_points()

        pointCount = len(aPointList)
        aPointList = aPointList[1:-1]
        aSliceList = SliceList(aPointList, RangeWidth=1, Overlap=0,
                               computeAttribs=tag_zigzag_segments)

        # vad = aSliceList.AsLeaves[4].my_slice.segment[0].arc.degreeCurve
        vad = aSliceList.AsLeaves[4]
        dbg = True

        x = [(sl.index, sl.my_slice.segment[0].arc.degree_curvature,
              sl.my_slice.segment[0].pt2pt.deflection_deg,
              sl.my_slice.segment[0].pt2pt.distanceBack,
              sl.my_slice.segment[0].may_be_zigzag)+
              compute_everything_else(sl.my_slice.segment[0])

             for sl in aSliceList.AsLeaves[240:265]]

        dt = np.dtype('int,float,float,float,bool,float,float')
        xarr = np.array(x, dtype=dt)
        # xarr.dtype.names = ['idx', 'Dc', 'Δ_chords', 'dist', 'zigzags' \
        #                     'val1, val2']
        print(xarr[:4])
        # newCol = np.array()



        predicate = lambda a, b: a.DegreeOfCurve == b.DegreeOfCurve
        aSliceList.consolidateNodeIf(predicate)

        aSliceList.shiftInteriorBoundariesBy(1)
        aSliceList.pointCount = pointCount

        return aSliceList


    def subtrajectorize(self,
                        trajectory,
                        returnGraph=False,
                        useMethod='individualCurvatures_preferred'):
        """
        Decomposes a Trajectory into subtrajectories based on an analysis of
            the curvature of each point triplet. Multiple methods are
            available for this. Client code indicates which method to use by
            setting useMethod. See the findMethod dictionary (in this function)
            to see which methods are currently available.
        :param trajectory: Trajectory to be processed.
        :type trajectory: Trajectory
        :param returnGraph: Return a NetworkX graph of the parse tree (Not
                Implemented).
        :type returnGraph: bool
        :param useMethod:
            'individualCurvatures_preferred' (default) - compare just the
                straight/turn classification to grow subtrajectory segments.
            'movingGrowingWindow' - Overlaps each slice a little, takes mean
                and stdev of curvature for each slice, compares stdev,
                consolidates slices when the stdevs of two adjacent slices are
                close to each other. When they are, the consolidation causes
                the window to grow towards the right.
        :type useMethod: str
        :return: leaves, pointCount, and number of leaves
        :rtype: list of tuples(startIndex, endIndex) and int and int
        """

        if returnGraph:
            raise NotImplementedError("Currently return of a graph "
                                      "is not implemented. Always pass False "
                                      "for returnGraph.")

        findMethod = \
            {'movingGrowingWindow': __class__._movingGrowingWindowMethod,
            'individualCurvatures_preferred':
                                    __class__._individCurvaturesMethod}

        aPointList = EPLmod.CreateExtendedPointList(trajectory)
        aPointList.computeAllPointInformation(account_for_lat_long=True)

        aPointList.mark_likely_zigzags()

        pointCount = len(aPointList)
        if pointCount < 4:
            return None

        try:
            aSliceList = findMethod[useMethod](self, aPointList)
        except KeyboardInterrupt:
            exit(0)
        except KeyError:
            msg = '"{0}" is not an available method.\n  '.format(useMethod)
            msg = msg + 'Available methods are are: {0}.'\
                .format([x for x in findMethod.keys()])
            raise AttributeError(msg)

        leafList = aSliceList.AsLeaves
        temp_test_str = None
        if 'CLX4' in aPointList.name:
            temp_test_str = SL.get_customizable_report_string(leafList)
        if temp_test_str:
            import os
            outFileName = os.path.join(os.path.expanduser(
                '~/Documents/tracktableTesting/testResults/'),
                aPointList.name + '_report.csv')
            try:
                with open(outFileName, 'wt') as outF:
                    outF.write(temp_test_str)
                print()
                print('report written to:  ', outFileName)
            except Exception:
                print()
                print('Could not write report csv file.')

        llSize = 0
        if leafList is not None:
            llSize = len(leafList)

        return leafList, pointCount, llSize
