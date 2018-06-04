'''
Classes to support automatic slicing of sequences. The primary class
    (the one you will usually instantiate and use) is SliceList. The
    other, sliceRange, makes up the individual slices in the SliceList.

The purpose of SliceList is to automate and convenientize the overlapping
    slicing of sequences the running of statistics on each slice, and
    then the consolidation of like nodes (when they are adjacent).

This approach allows for an unofficial but useful "Time Series" analysis,
    grouping similar segments into a collection of segments with some
    pre-defined thing in common.
'''

from collections import deque

class sliceRange():
    '''
    A single slice (range from n to m) into a sequence.
    '''
    def __init__(self, TargetSequence, Start, Stop, Step=None):
        self.target = TargetSequence
        self.start = Start
        self.stop = Stop
        self.step = Step
        self.iChanged = True

    def getSlice(self):
        return slice(self.start, self.stop, self.step)

    def getSegment(self):
        return self.target[self.getSlice()]

    def __repr__(self):
        return str(self.getSlice())

class SliceList(deque):
    '''
    An ordered collection of sliceRanges which cover an entire
        sequence (target) with customizable parameters attached
        to each sliceRange (such as mean, stdDev, or anything you
        need.
    Upon running consolidateNodeIf(), all nodes which are similar
        according to how you define similar are consolidated into
        a single node -- so long as the similar nodes are adjacent.
    '''
    def computeDesiredParameters(self):
        compute = self.computeParams
        if compute:
            for item in self:
                if item.iChanged:
                    compute(item)
                    item.iChanged = False

    def __init__(self, TargetSequence, RangeWidth, Overlap=0, computeParams=None):
        super().__init__()
        self.target = TargetSequence
        self.overlap = Overlap + 1
        self.startDelta = RangeWidth - Overlap - 1
        initialCount = len(self.target) // self.startDelta
        for r in range(0, 1+initialCount, self.startDelta+1):
            end = r + self.startDelta + self.overlap
            self.append(sliceRange(self.target, r, end))
        stopEnd = self[-1].stop; targetLen = len(self.target)
        if self[-1].stop < len(self.target):
            begin = self[-1].stop - self.overlap + 1
            self.append(sliceRange(self.target, begin, targetLen))

        self.computeParams = computeParams
        self.computeDesiredParameters()


    def allSlices(self, firstSlice=0, lastSlice=-1, stepBy=1):
        if lastSlice == -1:
            lastSlice = len(self)
        for s in range(firstSlice, lastSlice, stepBy):
            yield self[s]

    def allSegments(self, firstSlice=0, lastSlice=-1, stepBy=1):
        if lastSlice == -1:
            lastSlice = len(self)
        for s in range(firstSlice, lastSlice, stepBy):
            yield self[s].getSegment()

    def allCombined(self, firstSlice=0, lastSlice=-1, stepBy=1):
        if lastSlice == -1:
            lastSlice = len(self)
        for s in range(firstSlice, lastSlice, stepBy):
            yield (self[s], self[s].getSegment())

    def consolidateNodeIf(self, predicate):
        prev = None
        for item in self:
            item.delme = False
            if prev == None:
                prev = item
                continue


            pred = predicate(item, prev)
            if pred:
                item.start = prev.start
                prev.delme = True
                item.iChanged = True

            prev = item

        # How to remove deletable items adapted from
        # https://stackoverflow.com/a/10665631/1339950
        # Note: It has to be a new list.
        removeList = [x for x in self if x.delme]
        for item in removeList:
            if item.delme:
                self.remove(item)

        self.computeDesiredParameters()

if __name__ == '__main__':
    import statistics, math

    
    # Test 1

    col1 = [1.2, 4.4, 0.2, -1.1, 8.9, 1.4, 1.5, 1.6, 1.4, 1.3, 1.45, 1.55]
    def computeParameters(aSliceRange):
        aSliceRange.mean = statistics.mean(aSliceRange.getSegment())
        aSliceRange.stdDev = statistics.stdev(aSliceRange.getSegment())

    computeFunc = lambda each: computeParameters(each)
    aSliceList = SliceList(col1, RangeWidth=5, Overlap=2,
                           computeParams= computeFunc)
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

    predicate = lambda a, b: math.isclose(a.stdDev, b.stdDev, abs_tol=0.025)
    aSliceList.consolidateNodeIf(predicate= predicate)
    print(); print('After Consolidating:')

    print('Slice ID          Slice Mean   Slice StdDev')
    for s in aSliceList.allSlices():
        print(s, '  ', s.mean, '  ', s.stdDev)


    import sys
    sys.exit(0)
