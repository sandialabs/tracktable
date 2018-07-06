import math
import networkx as nx
from typing import List, Any, Union
# from tracktable.analysis.parseTreeCategorizations import CategoryBase


class Parse_Tree_Node(list):

    def __init__(self, point_range: List[int], my_traj=None,
                 associatedSlice=None,
                 ndx=-1):
        # self.my_slice = associatedSlice
        self.my_trajectory = my_traj
        if ndx > -1:
            self.index = ndx
        for itm in point_range:
            self.append(itm)

    def __hash__(self):
        multiplier = math.pow(20, self.depth_level+0.05)
        return int(multiplier + self[0])

    def __eq__(self, other):
        return self.depth_level == other.depth_level and \
                self[0] == other[0]

    def __str__(self):
        return '{0} Level {1}'.format(super().__str__(), self.depth_level)

    def _set_start(self, new_start_val):
        self[0] = new_start_val

    @property
    def start(self):
        return self[0]

    @property
    def stop(self):
        return self[1]

    @property
    def index_range(self):
        return self.start, self.stop

    @property
    def my_slice(self):
        return self.my_trajectory[self.start:self.stop]

    @property
    def depth_level(self):
        raise AttributeError("Depth Level is meaningless on class " + \
            self.__class__.__name__)

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

    def report_header_string(self, g: nx.DiGraph) -> str:
        raise NotImplementedError

    def report_data_lines(self, g: nx.DiGraph) -> Union[List[str],str]:
        raise NotImplementedError

    # _the_category: CategoryBase = None
    @property
    def category_str(self) -> str:
        return 'No Cat.'
    # @category.setter
    # def category(self, value: CategoryBase) -> None:
    #     self._the_category = value

    @property
    def description(self):
        retList = list()
        try:
            catstr = str(self.category).split('.')[1].title()
            retString = ('Segment: Index: {3} Target Index: {0} - {1}\n'
                         'Seg Category: {2}') \
                .format(self.start, self.stop - 1,
                        catstr, self.index)
        except Exception:
            retString = ('Segment: Index: {3} Target Index: {0} - {1}\n') \
                .format(self.start, self.stop - 1,
                        None, self.index)

        retList.append(retString)

        try:
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
        except AttributeError:
            retList.pop()

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

class Parse_Tree_Root(Parse_Tree_Node):
    def __init__(self, point_range, my_traj=None, associatedSlice=None,
                 ndx=-1):
        super().__init__(point_range, my_traj, associatedSlice, ndx)
        self.my_trajectory = None

    @property
    def depth_level(self):
        return 0

    def report_header_string(self, g: nx.DiGraph) -> str:
        first_successor = next(g.successors(self))
        ret_val = 'trajectory id,trajectory cat,' + \
                  first_successor.report_header_string(g)
        return ret_val

    def report_data_lines(self, g: nx.DiGraph) -> str:
        successors = list(g.successors(self))
        successors.sort(key=lambda node:node.start)
        prefix_str = 'No Name Root,No Category,'
        ret_list = []
        for a_node in successors:
            row_str = prefix_str + a_node.report_data_lines(g)
            ret_list.append(row_str)
            prefix_str = ',,'

        return '\n'.join(ret_list)

class ParseTreeNodeL1(Parse_Tree_Node):
    def __init__(self, point_range, my_traj=None, associatedSlice=None,
                 ndx=-1):
        super().__init__(point_range, my_traj, associatedSlice, ndx)
        self.my_trajectory = None

    @property
    def depth_level(self):
        return 1

    def report_header_string(self, g: nx.DiGraph) -> str:
        def report_header_string(self) -> str:
            return 'L1id, L1cat,' \
                   + self.my_trajectory[self.start].report_header_string

    def report_data_lines(self, g: nx.DiGraph) -> str:
        raise NotImplementedError


class ParseTreeNodeL2(Parse_Tree_Node):
    def __init__(self, point_range, my_traj=None, associatedSlice=None,
                 ndx=-1):
        super().__init__(point_range, my_traj, associatedSlice, ndx)

    @property
    def depth_level(self):
        return 2

    @property
    def point_count(self):
        return self.stop - self.start + 1

    @property
    def category_str(self) -> str:
        pre, post = str(self.category).split('.')
        return pre[:3] + '.' + post

    def report_header_string(self, g: nx.DiGraph) -> str:
        first_successor = next(g.successors(self))
        ret_val = 'L2id, L2cat,' + first_successor.report_header_string(g)
        return ret_val

    def report_data_lines(self, g: nx.DiGraph) -> str:
        ret_str_prefix = '{0} L2,{1},'.format(self.index, self.category_str)
        successors = list(g.successors(self))
        successors.sort(key=lambda node: node.start)
        ret_list = []
        for a_node in successors:
            ret_string = ret_str_prefix
            point_csv = a_node.report_data_lines(g)
            ret_string = ret_string + point_csv
            ret_list.append(ret_string)
            ret_str_prefix = ',,,,'

        return '\n'.join(ret_list)


class Parse_Tree_Leaf(Parse_Tree_Node):
    def __init__(self, point_range, my_traj=None, associatedSlice=None,
                 ndx=-1):
        super().__init__(point_range, my_traj, associatedSlice, ndx)

    @property
    def depth_level(self):
        return 3

    @property
    def my_point(self):
        return self.my_slice[0]

    def _shorten_category_strings(self, the_str: str) -> str:
        ret_str = ['']
        str_list = the_str.split('|')
        for a_str in str_list:
            if '.' in a_str:
                tmp = a_str.strip()
                tmp = tmp.split('.')
                ret_str.append('.'.join([tmp[0][:3], tmp[1]]))
            else:
                ret_str.append('None')

        return '|'.join(ret_str)


    @property
    def category_str(self) -> str:
        pt = self.my_point
        ret_str = '{0} | {1} | {2}'.format(pt.curvature_cat,pt.deflection_cat,
                                       pt.leg_length_cat)
        ret_str = self._shorten_category_strings(ret_str)
        return ret_str

    def report_header_string(self, g: nx.DiGraph) -> str:
        return \
        'L4id, L4cat, Long, Lat, radius_mi, Arc Dc°, Arc Δ°, ' \
        'Chord Δ°, ℓ_Back_mi, ℓ_Ahead_mi' \
        '\n'
        # 'seconds, speed_mph, Radial_μgn'

    _format_str = '{0},{1},{2:0.2f},{3:0.2f},{4:0.2f},{5:0.2f},' \
                    '{6:0.2f},{7:0.2f},{8:0.2f},{9:0.2f}'
    def report_data_lines(self, g: nx.DiGraph) -> str:
        pt = self.my_point
        if not pt.pt2pt:
            ret_str = '{0},,,,,,,,,'.format(pt.my_index)
            return ret_str

        ret_str = self._format_str.format(\
            pt.my_index, self.category_str, pt.Y, pt.X,
            math.fabs(pt.arc.radius),pt.arc.degree_curvature,
            pt.arc.deflection_deg,pt.pt2pt.deflection_deg,
            pt.pt2pt.distanceBack,pt.pt2pt.distanceAhead)
            # ,pt.pt2pt.seconds_back,pt.pt2pt.speed_back_mph,
            # pt.arc.radial_acceleration[0]
        return ret_str


class NodeListAtLevel(list):
    def __init__(self, the_level: int, from_list: List[Any]=[]):
        self.my_level = the_level
        self.end_index = 1
        # if from_list:
        #     for item in from_list:
        #         self.append(item)
        #     self.current = self[-1]

    def extend_with(self, next_child_node: Parse_Tree_Node):
        self.current[1] += 1
        self.end_index = self.current[1]

    def start_new_with(self, next_child_node: Parse_Tree_Node,
                       start_index: int = -1):
        if next_child_node.depth_level - self.my_level != 1:
            raise AttributeError("Level mismatch between NodeList and "
                                 "ParseTreeNode.")
        if self.my_level == 2:
            self.append(ParseTreeNodeL2([0, 1], self))
        elif self.my_level == 1:
            self.append(ParseTreeNodeL1([0, 1], self))
        else:
            raise Exception("Should not get to this point in "
                "parseTreeNode.py")

        self.current[0] = self.end_index
        self.end_index += 1
        self.current[1] = self.end_index

    @property
    def current(self):
        if len(self) == 0:
            return None
        return self[-1]

    def insert_into_tree_graph(self, g: nx.DiGraph) -> None:
        """
        Takes the current list of nodes (self), and inserts all in the list
        into graph g at the level of self.
        Side effects: Everything is a side effect, operating on graph g.
        :param g:
        :return:
        """
        pass


def get_all_by_level(g: nx.DiGraph) -> tuple:
    """
    Performs a "row-based" filter of a tree graph. For every level of a tree
    graph (number of edges from root to a node), returns a list of all nodes
    on that level, then retuns the whole thing in a tuple of those lists.
    :param g: Graph to operate on.
    :return: tuple of all nodes for each level
    """
    node_count = g.number_of_nodes()
    lev_0 = None
    for node in g:
        if node.depth_level == 0:
            lev_0 = Parse_Tree_Root(list(node))
            break

    lev_3 = [n for n in g if n.depth_level == 3]
    lev_1 = []
    lev_2 = []
    if len(lev_0) + len(lev_3) < node_count:
        lev_1 = [n for n in g if n.depth_level == 1]
        lev_2 = [n for n in g if n.depth_level == 2]

    return (lev_0, lev_1, lev_2, lev_3)


if __name__ == '__main__':
    print("parseTreeNode successfully loaded and run.")



