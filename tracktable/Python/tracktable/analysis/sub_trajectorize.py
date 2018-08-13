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
import tracktable.inout.trajectory as trajectory
from tracktable.analysis.sliceList import SliceList
from tracktable.analysis.sliceList import sliceRange as slice_range_class
import tracktable.analysis.ExtendedPoint
from tracktable.analysis.ExtendedPointList import ExtendedPointList as EPL
import tracktable.analysis.ExtendedPointList as EPLmod
import tracktable.analysis.sliceList as SL
import types
from math import isclose
from collections import defaultdict
import tracktable.analysis.nx_graph as nxg
import tracktable.analysis.parseTreeCategorizations as PTcats
import tracktable.analysis.parseTreeNode as ParseTreeNode
import tracktable.analysis.nx_graph as nxg
import os


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

    def splitAndClassify(self, trajectory, returnGraph=False):
        if returnGraph:
            leaves, G = self.subtrajectorize(trajectory, returnGraph=returnGraph)
        else:
            leaves = self.subtrajectorize(trajectory, returnGraph=returnGraph)
        segments = []
        straight=False
        if self.norm_dist_mat.is_straight(leaves[0][0], leaves[0][1]):
            straight=True

        for seg in leaves:
            if straight:
                segments.append((seg[0], seg[1], "straight"))
            else:
                segments.append((seg[0], seg[1], "turn"))
            straight = not straight #flip boolean
        return segments

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
    'Splits a trajectory into phases of flight segments'
    def __init__(self, straightness_threshold=1.1, length_threshold_samples=2): #2 is minimum
        self.threshold = straightness_threshold
        self.length_threshold_samples = length_threshold_samples
        self.currentNodeIndex = 1 #change to 0
        self.norm_dist_mat = NormalizedDistanceMatrix([]) #todo better way?

    def splitAndClassify(self, trajectory, returnGraph=False): #can take coordinate list or a trajectory.
        coordinates = []
        for point in trajectory: #make into coordinate list    #todo duplicated in example_sub_trajectorize.  Consolidiate
            if 'altitudes' in point.properties.keys(): #add altitude if exists
                coordinates.append([point[0], point[1], point.properties['altitudes']]) #changed from altitudes not sure why it was wrong
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
        landingStart= lastSample
        includeTakeoff=False
        if coordinates[0][2]: #has altitude
            if coordinates[0][2] < takeoffThreshold: #starts less than 10k feet
                #print("has alt at start less 10k", coordinates[0][2])
                for i in range(1,lastSample):#find where crosses 10k ft
                    if coordinates[i][2] > takeoffThreshold:
                        takeOffEnd = i
                        break
                if takeOffEnd == 0: #it never got over takeoff threshold
                    if coordinates[0][2] < coordinates[lastSample][2]:  # it rose from start to finish
                        print("assuming complete flight is a takeoff")
                        return [(0, lastSample, "takeoff")]
                    else:
                        print("assuming complete flight is a landing")
                        return [(0, lastSample, "landing")]  #could have other category for just flying around below 10k?
                includeTakeoff=True
                print("take off ends at sample ", takeOffEnd)
            #isolate landing based on altitude
            if coordinates[lastSample][2] < landingThreshold: #ends less than 10k feet
                for i in range(lastSample,-1, -1):#find where crosses 10k ft
                    if coordinates[i][2] > landingThreshold:
                        landingStart = i
                        break
                print("landing starts at sample ", landingStart)

        cruisingStart = None
        cruisingEnd = None
        #print(coordinates)
        #todo, below we must quit if there is not altituted values?
        h = np.histogram(list(zip(*coordinates))[2], bins=np.append(np.append(0, np.arange(10500,46500,1000)), 60000), density=True)  #to determine where the cruising altitude was?
        #print(h[0]*1000)
        includeCruise=False
        if np.max(h[0]) > cruisingThreshold: #multiply by 1000 to get approx ratio of samples in this bin
            includeCruise=True
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
        if includeTakeoff:
            if includeCruise:
                segments = [(0,takeOffEnd, "takeoff"), (takeOffEnd, cruisingStart, "climb"), (cruisingStart, cruisingEnd, "cruise"), (cruisingEnd, landingStart, "descent"), (landingStart, lastSample, "landing")] #later add sub segments
            else:
                maxAlt = coordinates[takeOffEnd][2]
                maxAltInd = takeOffEnd
                for i in range(takeOffEnd,landingStart):
                    if coordinates[i][2] > maxAlt:
                        maxAlt = coordinates[i][2]
                        maxAltInd = i
                if maxAltInd == takeOffEnd:
                    segments = [(0,takeOffEnd, "takeoff"), (takeOffEnd, landingStart, "descent"), (landingStart, lastSample, "landing")]
                elif maxAltInd ==landingStart:
                    segments = [(0,takeOffEnd, "takeoff"), (takeOffEnd, landingStart, "climb"), (landingStart, lastSample, "landing")]
                else:
                    segments = [(0,takeOffEnd, "takeoff"), (takeOffEnd, maxAltInd, "climb"), (maxAltInd, landingStart, "descent"), (landingStart, lastSample, "landing")] #later add sub segments
        else:
            if includeCruise:
                if cruisingStart == 0:
                    segments = [(cruisingStart, cruisingEnd, "cruise"), (cruisingEnd, landingStart, "descent"), (landingStart, lastSample, "landing")] #later add sub segments
                else:
                    segments = [(0, cruisingStart, "climb"), (cruisingStart, cruisingEnd, "cruise"), (cruisingEnd, landingStart, "descent"), (landingStart, lastSample, "landing")] #later add sub segments
            else:
                segments = [(0, landingStart, "descent"), (landingStart, lastSample, "landing")] #assumed the part before is descent.  May need another case here?
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

    def subtrajectorize(self, trajectory, returnGraph=False): #can take coordinate list or a trajectory.
        segments = self.splitAndClassify(trajectory, returnGraph=returnGraph)
        segs = []
        for seg in segments:
            segs.append((seg[0], seg[1])) #strip off "segment type"
        return segs


def trajName(aTraj):
    ts = aTraj[0].timestamp.strftime('%m%d%H%M')
    oid = ts + '_' + aTraj[0].object_id
    return oid

_isSubTrajerCurvatureAvailable = True

def compute_everything_else(aVar: tracktable.analysis.ExtendedPoint)\
        -> tuple:
    return 0.0, 0.2

counter = 0


class SubTrajerCurvature:
    """Breaks up a trajectory into subtrajectories based on curvatures of
    each point triplet. Multiple approaches to consolidating sequential
    curvature values into point ranges are available."""
    def __init__(self):
        self.summary_output = None
        self.plot_graph = False
        if not _isSubTrajerCurvatureAvailable:
            raise NotImplementedError(
                "The class SubTrajerCurvature is not available due " +
                "to import issues.")

    def request_summary_csv(self, outpath, basename):
        bname = os.path.splitext(basename)[0]
        self.summary_output = os.path.join(outpath, bname + '.csv')

    def request_plot_graph(self):
        self.plot_graph = True

    def request_no_plot_graph(self):
        self.plot_graph = False

    def _individCurvaturesMethod(self, aPointList, dcStraightThreshold=4.0,
                        request_graph_plot: bool =False) -> nx.DiGraph:
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
        :param request_graph_plot: when True, immediately opens a window of
            showing the tree graph of the categorized subtrajectories.
        :return: all subtrajectories in two forms
        :rtype: tuple: SliceList, graph
        """

        def tag_jitter_segments(aSliceRange):
            '''Likely no longer used. Might be deleteable.'''
            aSegment = aSliceRange.getSegment()

            aSliceRange.DegreeOfCurve = 'straight' \
                if fabs(aSegment[0].arc.degree_curvature) < \
                   dcStraightThreshold \
                else 'turn'

            aSliceRange.color = slice_range_class.straight_color
            if aSliceRange.DegreeOfCurve is not 'straight':
                aSliceRange.color = slice_range_class.turn_color

        aPointList.categorize_points()

        G = aPointList.create_minimal_digraph()
        G.name = aPointList.name
        PTcats.categorize_level3_to_level2(G)
        root, Level1, Level2, Level3 = G.get_all_by_level()   # may not be necessary
        try:
            PTcats.categorize_level2_to_level1(G)
        except IndexError:
            # print('IndexError in sub_trajectorize.py Line 496')
            return
        root, Level1, Level2, Level3 = G.get_all_by_level()

        # print('Nodes:', G.number_of_nodes(), 'Edges:', G.number_of_edges())
        # if request_graph_plot:
        if self.plot_graph:
            # if 'A3A458'in G.name:
            nxg.plot_graph(G)

        if self.summary_output:
            G.output_short_summary(self.summary_output)

        temp_test_str = None
        if False:   # 'CLX4' in aPointList.name:
            temp_test_str = G.csv_report
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


        # At this point, G is a NetworkX graph (Digraph, single root). But
        # the calling code needs it to be a list of
        # tuples: (start, stop-1, category_string)
        # so we must convert G to that kind of tuple.
        return_list = []
        root, Level1, Level2, Level3 = G.get_all_by_level()
        if len(Level1) == 1:
            start = 0
            stop = 1
            category = Level1[0].category_str
            return_list.append((start, stop, category))
        else:
            a_node: ParseTreeNode
            for a_node in Level1:
                try:
                    start = a_node.point_starting # there is an indexing bug in here which must be fixed.
                except IndexError:
                    return None, None
                stop = a_node.point_stopping
                category = a_node.category_str
                return_list.append((start, stop, category))

        return return_list, G


    def subtrajectorize(self,
                        trajectory,
                        returnGraph=False,
                        useMethod='individualCurvatures_preferred',
                        request_graph_plot: bool =True):
        trName = trajName(trajectory)
        segments, g = self.splitAndClassify(trajectory, returnGraph=returnGraph)
        if not segments:
            return None, None

        segs = []
        for seg in segments:
            segs.append((seg[0], seg[1])) #strip off "segment type"
        return segs, g

    def splitAndClassify(self, trajectory, returnGraph=False,
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

        aPointList = EPLmod.CreateExtendedPointList(trajectory)
        pointCount = len(aPointList)
        if pointCount < 20:
            return None, None

        try:
            aPointList.computeAllPointInformation(account_for_lat_long=True)
        except ZeroDivisionError:
            print('ZeroDivError in sub_trajecorize.py Line 588')
            return None, None

        try:
            global counter
            counter += 1
            leaves, g = \
                self._individCurvaturesMethod(aPointList,
                    request_graph_plot=returnGraph)
        except KeyboardInterrupt:
            exit(0)
        # except TypeError as te:
        #     try:
        #         tName = trajectory.traj_name(trajectory)
        #     except AttributeError:
        #         tName = '>> name not available.'
        #     # print(f'TypeError sub_rajectorize.py Line 607 count = {counter}' \
        #     #       f' name is {tName}.')
        #     leaves = None
        #     g = None

        if returnGraph:
            return leaves, g
        return leaves


