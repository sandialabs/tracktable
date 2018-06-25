"""
Classes to support automatic slicing of sequences. The primary class
    (the one you will usually instantiate and use) is SliceList. The
    other, sliceRange, makes up the individual slices in the SliceList.

The purpose of SliceList is to automate and convenientize the overlapping
    slicing of sequences the running of statistics on each slice, and
    then the consolidation of like nodes (when they are adjacent).

This approach allows for an unofficial but useful "Time Series" analysis,
    grouping similar segments into a collection of segments with some
    pre-defined thing in common.

The term "sequence" is used instead of "collection" because it only makes
    sense to operate on ordered collections: Lists, Deques, Tuples, or Strings,
    but not Sets or Dictionaries (because their order is not guaranteed).
    Not sure about Ordered Dictionaries. They have not been tested.
"""

from collections import deque
# import statistics
from tracktable.analysis.parseTreeNode import ParseTreeNode
# from tracktable.Python.tracktable.analysis.parseTreeNode import ParseTreeNode

lavendar_color = 'FFB57EDC'
red_color = 'FF0000FF'
white_color = 'FFFFFFFF'




class sliceRange():
    """
    A single slice (range from n to m) into a sequence. Note: This is not
    Python's slice object, but it works like it, and it can be converted
    to a slice object via the getSlice() method.
    """

    straight_color = white_color
    turn_color = lavendar_color

    def __init__(self, TargetSequence, Start, Stop, Step=None):
        """
        Creates new instance of a SliceRange.
        :param TargetSequence: Reference to the sequence being sliced.
        :param Start: Begin Index of this slice.
        :param Stop: End Index of this slice.
        :param Step: Not Implemented: Always 1. Step value through this slice.
        """
        self.target = TargetSequence
        self.start = Start
        self.stop = Stop
        self.step = Step
        self.iChanged = True

    def getSlice(self):
        """Converts self to a Python slice object."""
        return slice(self.start, self.stop, self.step)

    def getSegment(self):
        """Returns the slice of the target sequence."""
        return self.target[self.getSlice()]

    @property
    def segment(self):
        """Returns the slice of the target sequence."""
        return self.getSegment()

    def __repr__(self):
        attribs = [x for x in self.__dict__
                   if 'target' not in x and 'iChanged' not in x]
        atDict = {k : self.__dict__[k] for k in attribs}
        retStr = str(self.getSlice()) +' ' + str(len(self)) + \
                 ' items, ' + str(atDict)
        return retStr

    def __len__(self):
        return self.stop - self.start


class SliceList(deque):
    """
    An ordered collection of sliceRanges which cover an entire
        sequence (target) -- actually a Python deque -- with customizable
        parameters attached to each sliceRange (such as mean, stdDev, or
        anything you need.
    (Deque is used for efficient interior deletions for large datasets.)
    Upon running consolidateNodeIf(), all nodes which are similar
        according to how you define similar are consolidated into
        a single node -- so long as the similar nodes are adjacent.
    The Slices may overlap if called for via the Overlap parameter.
    """

    straight_color = white_color
    turn_color = lavendar_color

    def computeDesiredAttributes(self):
        compute = self.computeParams
        if compute:
            for item in self:
                if item.iChanged:
                    compute(item)
                    item.iChanged = False

    def __init__(self,
                 TargetSequence,
                 RangeWidth,
                 Overlap=0,
                 computeAttribs=None):
        """
        :param TargetSequence: The underlying sequence being sliced.
        :param RangeWidth: How many items are included in each slice (before
                consolidating, which may change the width of slices.
        :param Overlap: The number of elements included in both of two
                adjacent slices.
        :param computeAttribs: When a custom parameter is desired, they are
                added in this function.
        :type computeAttribs: callbackFunction(SliceList) -> None
        """
        super().__init__()

        self.target = TargetSequence
        targetLen = len(TargetSequence)
        self.overlap = Overlap
        advanceDelta = RangeWidth - Overlap
        endOffset = RangeWidth
        self.append(sliceRange(self.target, 0, endOffset))
        while endOffset < targetLen:
            endOffset += advanceDelta
            startOffset = endOffset - RangeWidth
            if endOffset + 3 >= targetLen:
                endOffset = targetLen
            self.append(sliceRange(TargetSequence, startOffset, endOffset))

        if self[-1].stop > targetLen:
            self[-1].stop =  targetLen
        if len(self) > 2 and self[-2].stop > targetLen:
            self[-2].stop =  targetLen

        for item in reversed(self):
            if len(item) < 3:
                item.delme = True
            else:
                item.delme = False
                break

        # Remove SliceRanges if marked delme.
        removeList = [x for x in reversed(self)
                      if hasattr(x, 'delme') and getattr(x, 'delme')]
        for item in reversed(removeList):
            try:
                if item.delme:
                    self.remove(item)
                else:
                    break
            except AttributeError:
                break

        self.computeParams = computeAttribs
        self.computeDesiredAttributes()
        self._recompute_indexes()


        self.color = self.straight_color

    def _recompute_indexes(self):
        for index, item in enumerate(self):
            self.my_index = index

    @property
    def AsLeaves(self):
        """Returns the slice list as a list of 'leaves', which are tuples
            of (begin-slice-index, end-slice-index) When there is overlap in
            the slice list, that overlap is removed and half the items are
            assigned to previous and half are assigned to next."""

        slices = [x for x in self.allSlices()]
        if len(slices) < 1:
            return None

        adjustBack = int(self.overlap // 2.0) - 1
        adjustFront = int(self.overlap // 2.0)
        leafList = [
            ParseTreeNode([sl.start + adjustFront, sl.stop - adjustBack],
                          self.target, sl, index)
            for index, sl in enumerate(slices)]

        for a_leaf, a_slice in zip(leafList, slices):
            a_leaf.color = a_slice.color

        leafList[0][0] = 0
        leafList[-1][1] = len(self.target)
        return leafList

    def allSlices(self, firstSlice=0, lastSlice=-1, stepBy=1):
        """Generator to return each slice range one at a time. Mainly intended
        for internal use of the class, but it is not private. Overlap is not
        eliminated in this method."""
        if lastSlice == -1:
            lastSlice = len(self)
        for s in range(firstSlice, lastSlice, stepBy):
            yield self[s]

    def allSegments(self, firstSlice=0, lastSlice=-1, stepBy=1):
        """Generator to return all segments of the target sequence. Overlap
        is not eliminated in this method."""
        if lastSlice == -1:
            lastSlice = len(self)
        for s in range(firstSlice, lastSlice, stepBy):
            yield self[s].getSegment()

    def allCombined(self, firstSlice=0, lastSlice=-1, stepBy=1):
        """Generator to return tuples in which [0] is the slice range and
            [1] is the segment from the target sequence."""
        if lastSlice == -1:
            lastSlice = len(self)
        for s in range(firstSlice, lastSlice, stepBy):
            yield (self[s], self[s].getSegment())

    def shiftInteriorBoundariesBy(self, shiftDistance,
                                  recomputeParameters=False):
        """
        Grows the first SliceRange by shiftDistance, shrinks the last by
            the same amount, and shifts all internal SliceRanges by
            shiftDistance.
        :param shiftDistance: Integer of how far to shift the SliceRange
                boundaries.
        :param recomputeParameters: Whether or not to recompute parameters
            after the shift. The default is don't (False).
        :return: None
        """
        if len(self) == 0:
            return

        for aSlice in self:
            aSlice.start += shiftDistance
            aSlice.stop += shiftDistance
        self[0].start -= shiftDistance
        self[-1].stop -= shiftDistance

        if recomputeParameters:
            self.computeParams()


    def consolidateNodeIf(self, predicate):
        """
        From start+1 to the end, consolidates two adjacent nodes if the nodes
            have some similarity based on a filter function (predicate).
            After doing all consolidation, it automatically recomputes all
            attributes for all remaining sliceRanges.
        :param predicate: Determines when to consolidate two adjacent
                sliceRanges.
        :type predicate: callbackFunction(sliceRange, sliceRange) -> bool
        :return: None
        """
        prev = None
        for item in self:
            item.delme = False
            if prev == None:
                prev = item
                continue


            try:
                pred = predicate(prev, item)
                if pred:
                    item.start = prev.start
                    prev.delme = True
                    item.iChanged = True
            except AttributeError:
                raise

            prev = item

        # How to remove deletable items is adapted from
        # https://stackoverflow.com/a/10665631/1339950
        # Note: List of items to be removed has to be a new list.
        removeList = [x for x in self if x.delme]
        for item in removeList:
            if item.delme:
                self.remove(item)

        self.computeDesiredAttributes()

    def __str__(self):
        retStr = ''
        for itm in self:
            retStr = retStr +  str(itm) + '\n'
        return retStr

def get_customizable_report_string(some_leaves):
    accumulate_string = 'id,class,ndx,Long,Lat,radius_mi,Dc°,Δ°,' \
                        'Chord Δ°,ℓ_Back_mi,ℓ_Ahead_mi,' \
                        'seconds,speed_mph,Radial_μg\n'

    try:
        for a_leaf in some_leaves:
            accumulate_string += a_leaf.create_debug_report_string1()
    except Exception:
        pass

    return accumulate_string

if __name__ == '__main__':
    import statistics, math

    # Test 1

    if True:
        col1 = [1.2, 4.4, 0.2, -1.1, 8.9, 1.4, 1.5, 1.6, 1.4, 1.3, 1.45,
                1.55, 1.45, 1.22]
        def computeAttributes(aSliceRange):
            aSliceRange.mean = statistics.mean(aSliceRange.getSegment())
            aSliceRange.stdDev = statistics.stdev(aSliceRange.getSegment())

        computeFunc = lambda each: computeAttributes(each)
        aSliceList = SliceList(col1, RangeWidth=5, Overlap=2,
                               computeAttribs= computeFunc)
        print(aSliceList)
        for s in aSliceList.allSlices():
            print(s)
        for s in aSliceList.allSegments():
            print(s)
        for s in aSliceList.allCombined():
            print(s)

        print(); print('Before Consolidating:')
        print('Slice ID          Slice Mean   Slice StdDev')
        for s in aSliceList.allSlices():
            print(s, '  ', s.mean, '  ', s.stdDev)

        # predicate = lambda a, b: \
        #     math.isclose(a.stdDev, b.stdDev, abs_tol=0.025)
        predicate = lambda a, b: \
            a.may_be_zigzag ^ b.may_be_zigzag
        aSliceList.consolidateNodeIf(predicate=predicate)
        print(); print('After Consolidating:')

        print('Slice ID          Slice Mean   Slice StdDev')
        for s in aSliceList.allSlices():
            print(s, '  ', s.mean, '  ', s.stdDev)

    # Test 2

    secondList = [ (1.2, 0.2), (2.0, 0.1), (2.9, 0.3),
                   (4.2, 0.2), (5.0, 0.1), (5.9, 0.3),
                   (7.2, 0.2), (8.0, 0.1), (8.9, 0.3),
                   (10.2, 0.2), (12.0, 0.1), (12.9, 0.3),
                   (14.2, 0.2), (15.0, 0.1), (15.9, 0.3),
                   (17.2, 0.2), (18.0, 0.1), (18.9, 0.3),
                   (21.2, 0.2), (22.0, 0.1), (22.9, 0.3),
                   (24.2, 0.2), (25.0, 0.1), (25.9, 0.3),
                   (27.2, 0.2), (28.0, 0.1), (28.9, 0.3),
                   (31.2, 0.2), (32.0, 0.1), (32.9, 0.3),
                   (34.2, 0.2), (35.0, 0.1), (35.9, 0.3),
                   (37.2, 0.2), (38.0, 0.1), (38.9, 0.3),
                   ]

    def computeAttribs(aSliceRange):
        something = aSliceRange.getSegment()
        myTp = type(something)
        extractedList = [x[1] for x in something]
        aSliceRange.ave = statistics.mean(extractedList)
        aSliceRange.count = len(extractedList)
        aSliceRange.stdDev = statistics.stdev(extractedList)

    sliceList2 = SliceList(secondList, RangeWidth=5, Overlap=2,
                           computeAttribs=computeAttribs)

    print(); print("Test 2")
    print(sliceList2)
    print(len(sliceList2))

    predicate = lambda a, b: math.isclose(a.stdDev, b.stdDev, abs_tol=0.01)
    # sliceList2.consolidateNodeIf(predicate)
    print(sliceList2)
    print(len(sliceList2))

    print(sliceList2.AsLeaves)

    sl3 = SliceList(secondList, RangeWidth=5, Overlap=0,
                    computeAttribs=computeAttribs)
    print(); print('--------------')
    print('sl3: '); print()
    print(sl3)
    print(); print(sl3.AsLeaves)

    print();
    print('--------------')
    print('sl4: ');
    print()

    def computeDcOnly(aSliceRange):
        aSliceRange.val1 = aSliceRange.getSegment()[0][0]
        aSliceRange.val2 = aSliceRange.getSegment()[0][1]
        aSliceRange.classification = \
            'Straight' if aSliceRange.val2 < 0.15 else "Curved"


    sl4 = SliceList(secondList, RangeWidth=1, Overlap=0,
                    computeAttribs=computeDcOnly)

    print("Before consolidating:", len(sl4))
    print(sl4)
    print(); print()

    predicate = lambda a, b: a.classification == b.classification
    # predicate = lambda a, b: a.val2 < b.val2
    sl4.consolidateNodeIf(predicate)
    print()
    print("After consolidating", len(sl4))
    print(sl4)
    print()
    print(sl4.AsLeaves)


