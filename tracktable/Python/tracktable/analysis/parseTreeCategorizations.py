import enum
import tracktable.analysis.parseTreeNode as ParseTreeNode
from typing import Any, Union
from networkx import NetworkXError
from tracktable.analysis.ExtendedPoint import ExtendedPoint as EP
import tracktable.analysis.nx_graph as nxg
from tracktable.analysis.symbology_kml import kml_symbology
import math

_huge_number = 1000000

class CategoryBase(enum.Enum):
    """Base class for all parse tree categorizations."""
    def __init__(self, num, criteria=None):
        self.num = num
        self.criteria_lambda = criteria

    @property
    def as_int(self):
        try:
            return self.value[0]
        except:
            return self.value

    def __lt__(self, other: "CategoryBase"):
        return self.as_int < other.as_int

    def __le__(self, other: "CategoryBase"):
        return self.as_int <= other.as_int

    def __gt__(self, other: "CategoryBase"):
        return self.as_int > other.as_int

    def __ge__(self, other: "CategoryBase"):
        return self.as_int >= other.as_int

    def __eq__(self, other: "CategoryBase"):
        return self.as_int == other.as_int

    def __ne__(self, other: "CategoryBase"):
        return self.as_int != other.as_int

    def __hash__(self):
        return self.as_int

    @staticmethod
    def default_criteria(target_variable: Any,
                         attr_name: str,
                         comparison_value: Union[int, float]) \
                        -> bool:

        return getattr(target_variable, attr_name) <= comparison_value

    @classmethod
    def assign_to(cls, a_parse_tree_node, new_attr_name):
        for enm in cls:
            if enm.criteria_lambda(a_parse_tree_node, enm.value[0]):
                setattr(a_parse_tree_node, new_attr_name, enm)
                return
        else:
            # a_parse_tree_node.leg_length_cat = cls[-1]
            setattr(a_parse_tree_node, new_attr_name, cls[-1])
            return

_stopped_threshold = 10000
_jitter_threshold = 3.7

def _leg_length_identify_anomalies(a_point: EP, anomaly_type: str) -> bool:
    try:
        if not a_point.pt2pt or not a_point.pt2pt._ratio_front_over_back:
            return False
    except AttributeError:
        return False

    ratio = a_point.pt2pt._ratio_front_over_back
    ratio = max(ratio, 1.0 / ratio)
    if anomaly_type == 'stopped':
        if ratio >= _stopped_threshold:
            return True
        return False
    if anomaly_type == 'jitter':
        if ratio >= _jitter_threshold:
            return True
        return False
    return False

class LegLengthCat(CategoryBase):
    """Categorize the length of a leg of a trajectory."""

    anomaly_stopped = (-2, lambda v, this_num:
            _leg_length_identify_anomalies(v, 'stopped'))
    anomaly_jitter = (-1, lambda v, this_num:
            _leg_length_identify_anomalies(v, 'jitter'))

    short = (8.0, lambda v, this_num:
        CategoryBase.default_criteria(v, "horizontal_distance", this_num))

    medium = (16.0, lambda v, this_num:
        CategoryBase.default_criteria(v, "horizontal_distance", this_num))

    long = (_huge_number, lambda v, this_num: True)


class CurvatureCat(CategoryBase):
    """Categorize the curvature of a leg of a trajectory."""
    hard_left = (-12, lambda v, this_num:
        CategoryBase.default_criteria(v, "degree_curve", this_num))

    normal_left = (-4, lambda v, this_num:
        CategoryBase.default_criteria(v, "degree_curve", this_num))

    # gentle_left = (-1, lambda v, this_num:
    #     CategoryBase.default_criteria(v, "degree_curve", this_num))

    # flat = (1, lambda v, this_num:
    flat = (4, lambda v, this_num:
            CategoryBase.default_criteria(v, "degree_curve", this_num))

    # gentle_right = (4, lambda v, this_num:
    #     CategoryBase.default_criteria(v, "degree_curve", this_num))

    normal_right = (12, lambda v, this_num:
        CategoryBase.default_criteria(v, "degree_curve", this_num))

    hard_right = (_huge_number, lambda v, this_num: True)


class DeflectionCat(CategoryBase):
    """Categorize the deflection (change in heading) of a pair of trajectory
    chord segments."""
    sharp_left = (-9.5, lambda v, this_num:
        CategoryBase.default_criteria(v, "deflection_deg", this_num))

    left = (-3, lambda v, this_num:
        CategoryBase.default_criteria(v, "deflection_deg", this_num))

    straight = (3, lambda v, this_num:
        CategoryBase.default_criteria(v, "deflection_deg", this_num))

    right = (9.5, lambda v, this_num:
        CategoryBase.default_criteria(v, "deflection_deg", this_num))

    sharp_right = (360, lambda v, this_num: True)

class Level1Cat(CategoryBase):
    straight_reach = 0,
    s_curve = 1,
    j_hook = 2,
    u_turn = 3,
    grand_j_hook = 4
    race_track = 5
    no_cat = 6


class Level2Cat(CategoryBase):
    left_turn = -1,
    straight = 0,
    right_turn = 1

    @property
    def symbology(self):
        if self == Level2Cat.left_turn:
            return kml_symbology(self.name, color='yellow', width=3)
        elif self == Level2Cat.straight:
            return kml_symbology(self.name, color='white', width=3)
        elif self == Level2Cat.right_turn:
            return kml_symbology(self.name, color='vermillion', width=3)


class CategoryStateException(AttributeError):
    def __init__(self, msg):
        self.message = msg


def level2_categorize(leaf_node: ParseTreeNode.Parse_Tree_Leaf) -> Level2Cat:
    """If the leaf is jitter, return None"""
    l2_cat = None
    leaf: EP = leaf_node.my_point

    # if getattr(leaf, "may_be_jitter", False):
    #     raise CategoryStateException('jitter')

    if leaf.curvature_cat <= CurvatureCat.normal_left:
        l2_cat = Level2Cat.left_turn
    elif leaf.curvature_cat > CurvatureCat.flat:
        l2_cat = Level2Cat.right_turn
    else:
        l2_cat = Level2Cat.straight
    return l2_cat


def _insinuate_new_nodes_into_tree(node_list: ParseTreeNode,
                                   g: nxg.TreeDiGraph,
                                   partitioned_tuple: tuple) -> None:
    """


    All functionality is via side effects. No return value.

    :param node_list: The list of mid-level nodes to insinuate into the graph
    :param g: the graph to be insinuated into
    :param partitioned_tuple: lists of nodes at different levels
    :return: None
    """
    root, lev_1, lev_2, leaves = partitioned_tuple

    node_list[0]._set_start(0)

    if not lev_2:
        for an_L2_node in node_list:
            start, stop = an_L2_node.index_range
            g.add_node(an_L2_node)
            g.add_edge(root, an_L2_node)
            for a_leaf in leaves[start:stop]:
                try:
                    g.remove_edge(root, a_leaf)
                except NetworkXError:
                    pass
                g.add_edge(an_L2_node, a_leaf)

    elif not lev_1:
        for an_L1_node in node_list:
            start, stop = an_L1_node.index_range
            g.add_node(an_L1_node)
            g.add_edge(root, an_L1_node)
            for an_L2_node in lev_2[start:stop]:
                try:
                    g.remove_edge(root, an_L2_node)
                except NetworkXError:
                    pass
                g.add_edge(an_L1_node, an_L2_node)

        # temporary kludge - remove stray edges  -- must fix this eventually
        edges_to_remove = [e for e in g.edges
                           if e[0].depth_level == 0 and e[1].depth_level == 2]
        for e in edges_to_remove:
            g.remove_edge(e[0], e[1])



def _perform_tests(**kwargs):
    if len(kwargs) == 0:
        return
    return
    # nodes: ParseTreeNode.Parse_Tree_Node = kwargs.get('node_list', None)
    # itm: ParseTreeNode.Parse_Tree_Node
    # for itm in nodes:
    #     length = itm.length_chords
    #     total_defl = itm.total_defl_deg_chords
    #     dbg = True

def categorize_level2_to_level1(g: nxg.TreeDiGraph) -> None:
    partitioned_tuple = ParseTreeNode.get_all_by_level(g)
    root, _1, lev_2, _3 = partitioned_tuple

    map_row_length_min = 35.0  # miles
    u_turn_deflection_range = 1.5  # degrees, left or right
    s_curve_mid_straight_max_length = 2.0  # miles

    # find s-curves
    s_curve_list = []
    o_curve_list = []
    for seg_idx in range(len(lev_2)-1):
        seg1: ParseTreeNode.ParseTreeNodeL2 = lev_2[seg_idx]
        seg2: ParseTreeNode.ParseTreeNodeL2 = lev_2[seg_idx+1]
        if seg1.defl_sign * seg2.defl_sign == -1:
            if seg_idx == 77:
                dfl = seg2.total_defl_deg_chords
            a_range = (seg_idx, seg_idx+1)
            s_curve_list.append(a_range)
        elif seg1.defl_sign * seg2.defl_sign == 1:
            lth = seg1.length_chords
            dfl = seg1.total_defl_deg_chords
            a_range = (seg_idx, seg_idx+1)
            o_curve_list.append(a_range)


    # consolidate L1 categories
    l1_node_list = ParseTreeNode.NodeListAtLevel(1)
    for l2_node_idx in range(len(lev_2)-1):
        a_range = (l2_node_idx, l2_node_idx+1)
        new_l1_node = ParseTreeNode.ParseTreeNodeL1(a_range, my_graph=g)
        if a_range in s_curve_list:
            new_l1_node.category = Level1Cat.s_curve
        elif a_range in o_curve_list:
            new_l1_node.category = Level1Cat.race_track
        else:
            new_l1_node.category = Level1Cat.no_cat
        l1_node_list.append(new_l1_node)

    # merge adjacent no_cats into one singles
    for idx in range(len(l1_node_list)-2, 0, -1):
        this_node = l1_node_list[idx]
        next_node = l1_node_list[idx+1]
        if this_node.category == next_node.category:
            this_node[1] = next_node[1]
            l1_node_list.remove(next_node)

    for idx, a_node in enumerate(l1_node_list):
        a_node.index = idx

    _insinuate_new_nodes_into_tree(l1_node_list, g, partitioned_tuple)



def categorize_level3_to_level2(g: nxg.TreeDiGraph) -> None:
    """When you see a bunch of functions with numbers in the function names,
        it is a prediction that you will be refactoring later."""
    partitioned_tuple = ParseTreeNode.get_all_by_level(g)
    root, _1, _2, lev_3 = partitioned_tuple
    # alt_root = g.root_node
    l2_node_list = ParseTreeNode.NodeListAtLevel(2)
    l2_node_list.start_new_with(lev_3[0], 0, owning_graph=g)
    l2_node_list.current.category = level2_categorize(lev_3[1])
    l2_node_list.current.index = node_count = 0
    # l2_node_list.current
    for a_node in lev_3[1:-1]:
        apt = a_node.my_point.my_index, a_node.my_point.pt2pt.distanceAhead

        is_anomaly = True \
            if 'anomaly' in str(a_node.my_point.leg_length_cat) \
            else False

        try:
            prospective_category = level2_categorize(a_node)
            keep_extending = \
                prospective_category == l2_node_list.current.category
        except CategoryStateException as ce:
            keep_extending = True
            # prospective_category is unchanged

        # But,
        if is_anomaly:
            keep_extending = True

        if keep_extending:
            l2_node_list.extend_with(a_node)
        else:
            node_count += 1
            # l2_node_list.current[1] -= 1
            l2_node_list.start_new_with(a_node, owning_graph=g)
            l2_node_list.current.category = prospective_category
            l2_node_list.current.index = node_count

    #region This code region is a kludge until I can get my indexing right.
    for cnt, a_node in enumerate(l2_node_list[:-1]):
        a_node[1] -= 1
        if cnt > 0:
            a_node[0] -= 1
    l2_node_list[-1][0] -= 1
    #endregion

    #region optional post-processing: Turning segments can steal one point
    # from adjacent straight segments when certain conditions obtain.
    deflection_threshold = 2.0
    for node_index in range(1, len(l2_node_list)):
        prev: ParseTreeNode.ParseTreeNodeL2 = l2_node_list[node_index - 1]
        curr: ParseTreeNode.ParseTreeNodeL2 = l2_node_list[node_index]
        curr_first_pt: EP = curr.get_point(0, lev_3)
        pt_prev: EP = prev.get_point(-1, lev_3)
        if Level2Cat.straight == curr.category:
            if pt_prev.defl_sign * curr_first_pt.defl_sign > 0 \
                    and math.fabs(curr_first_pt.deflection_deg) \
                    > deflection_threshold:
                # current gives the point to previous.
                prev[1] += 1
                curr[0] += 1
        elif Level2Cat.straight == prev.category:
            if pt_prev.defl_sign * curr_first_pt.defl_sign > 0 \
                    and math.fabs(pt_prev.deflection_deg) \
                    > deflection_threshold:
                # current gives the point to previous.
                prev[1] -= 1
                curr[0] -= 1

    for node_index in range(len(l2_node_list)-1, 1, -1):
        this_node = l2_node_list[node_index]
        node_point_count = this_node.stop - this_node.start
        if node_point_count < 1:
            del l2_node_list[node_index]
            dbg = True

    #endregion optional post-processing: Turning segments can steal a point

    #region corner case: If a node consists of all anomalies, give it to
    #  the prior node
    del_list = []
    for node_index, a_node in enumerate(l2_node_list):
        node_len = len(a_node.point_list)
        if node_len > 12:
            continue

        anomaly_count = sum(hasattr(n, "leg_length_cat") and
                            n.leg_length_cat.as_int < 0
                            for n in a_node.point_list[1:])
        if node_len == anomaly_count:
            del_list.append(node_index)

    if del_list:
        for idx in reversed(del_list):
            prev_node = l2_node_list[idx-1]
            curr_node = l2_node_list[idx]
            prev_node[1] = curr_node[1] # give curr points to prev.
            del l2_node_list[idx]

    for idx, a_node in enumerate(l2_node_list):
        a_node.index = idx
    #endregion corner case: If a node consists of all anomalies, give it to

    # leaf_successors_of_root_before_insinuation = \
    #     [n for n in g.successors(g.root_node) if n.depth_level == 3]

    _insinuate_new_nodes_into_tree(l2_node_list, g, partitioned_tuple)
    # successors_of_root_after_insinuation = \
    #     [n for n in g.successors(g.root_node) if n.depth_level == 3]

    # _perform_tests(node_list=l2_node_list)
    # dbg = True


def _test_run():
    class _temp_():
        def __init__(self, dist=1.0):
            self.horizontal_distance = dist

    class little_test_class(list):
        def __init__(self, aList):
            for itm in aList:
                self.append(itm)

        @property
        def horizontal_distance(self):
            return 11.0

        @property
        def degree_curve(self):
            return 44.5

    v1 = _temp_(1.0)
    v2 = _temp_(2.0)
    aList = little_test_class([v1, v2])

    print()
    LegLengthCat.assign_to(aList, 'leg_length_cat')
    print('Length Category:', aList.leg_length_cat)

    print()
    CurvatureCat.assign_to(aList, 'curvature_cat')
    print("Curvature Category:", aList.curvature_cat)
    print()

    an_l2cat = Level2Cat.left_turn
    print(an_l2cat.symbology.to_kml())


if __name__ == '__main__':
    try:
        _test_run()
    except KeyboardInterrupt:
        exit(0)


