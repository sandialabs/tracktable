import math

class Parse_Tree_Node(list):
    def __init__(self, sourceList, my_traj, associatedSlice=None,
                 ndx=-1):
        self.my_slice = associatedSlice
        self.my_trajectory = my_traj
        if ndx > -1:
            self.index = ndx
        for itm in sourceList:
            self.append(itm)

    @property
    def start(self):
        return self[0]

    @property
    def stop(self):
        return self[1]

    def _traj_get_time_str(self, idx):
        return self.my_trajectory[idx].timestamp.strftime('%H:%M:%S')

    def _traj_get_duration_str(self, start, stop):
        duration = self.my_trajectory[stop].timestamp - \
                   self.my_trajectory[start].timestamp
        return str(duration)

    def _traj_get_alt_str(self, idx):
        return str(self.my_trajectory[idx].Z)

    def _traj_get_mid_alt_str(self):
        traj_mid_point_count = len(self.my_trajectory) // 2
        return str(self.my_trajectory[traj_mid_point_count].Z)

    @property
    def horizontal_distance(self):
        accum_dist = 0.0
        for a_seg in self.my_trajectory[self.start, self.stop]:
            accum_dist += a_seg.pt2pt.distanceBack
        return accum_dist

    @property
    def description(self):
        retList = list()
        retString = ('Segment: Index: {3} Target Index: {0} - {1}\n'
                     'Seg Type: {2}') \
            .format(self.start, self.stop - 1,
                    self.my_slice.DegreeOfCurve, self.index)
        retList.append(retString)

        retList.append('\nWhole Trajectory:')
        retList.append('Start Time: {0}' \
                       .format(self._traj_get_time_str(0)))
        retList.append('End   Time: {0}' \
                       .format(self._traj_get_time_str(-1)))
        retList.append('Duration: {0}' \
                       .format(self._traj_get_duration_str(0, -1)))

        retList.append('\nStart Alt: {0}' \
                       .format(self._traj_get_alt_str(0)))
        retList.append('Mid Alt: {0}' \
                       .format(self._traj_get_mid_alt_str()))
        retList.append('End Alt: {0}' \
                       .format(self._traj_get_alt_str(-1)))

        return '\n'.join(retList)

    def create_debug_report_string1(self):
        pt1 = self.my_trajectory[self.start]
        build_string = ''
        if self.start == 0:
            real_start = 1
        else:
            real_start = self.start
            pt1 = self.my_trajectory[real_start - 1]

        build_string += '{0},{1},'.format(self.index,
                                          self.my_slice.DegreeOfCurve)
        main_string = '{2},{3:.3f},{4:.3f},{5:.3f},{6:+.3f},' \
                      '{7:+.3f},{8:+.3f},{9:.3f},' \
                      '{10:.4f},{11:.1f},{12:.1f},' \
                      '{13:.3f}\n'
        build_string += main_string \
            .format(self.index, self.my_slice.DegreeOfCurve,
                    pt1.my_index, pt1.Y, pt1.X,
                    math.fabs(pt1.arc.radius),
                    pt1.arc.degreeCurveDeg, pt1.arc.deflection_deg,
                    pt1.pt2pt.deflection_deg, pt1.pt2pt.distanceBack,
                    pt1.pt2pt.distanceAhead, pt1.pt2pt.seconds_back,
                    pt1.pt2pt.speed_back_mph,
                    pt1.arc.radial_acceleration[0])
        for pt1 in self.my_trajectory[real_start:self.stop - 2]:
            build_string += ',,'
            build_string += main_string \
                .format(self.index, self.my_slice.DegreeOfCurve,
                        pt1.my_index, pt1.Y, pt1.X,
                        math.fabs(pt1.arc.radius),
                        pt1.arc.degreeCurveDeg,
                        pt1.arc.deflection_deg,
                        pt1.pt2pt.deflection_deg,
                        pt1.pt2pt.distanceBack,
                        pt1.pt2pt.distanceAhead,
                        pt1.pt2pt.seconds_back,
                        pt1.pt2pt.speed_back_mph,
                        pt1.arc.radial_acceleration[0])

        build_string += ',,,,,,\n'
        return build_string

