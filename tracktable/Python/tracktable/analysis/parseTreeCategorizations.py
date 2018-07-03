import enum
import tracktable.analysis.parseTreeNode as ParseTreeNode
from typing import Any, Union
from networkx import DiGraph
from tracktable.analysis.ExtendedPoint import ExtendedPoint as EP
import tracktable.analysis.nx_graph as nxg
from tracktable.analysis.symbology_kml import kml_symbology

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
        dbg = True
        for enm in cls:
            if enm.criteria_lambda(a_parse_tree_node, enm.value[0]):
                setattr(a_parse_tree_node, new_attr_name, enm)
                return
        else:
            # a_parse_tree_node.leg_length_cat = cls[-1]
            setattr(a_parse_tree_node, new_attr_name, cls[-1])
            return


class LegLengthCat(CategoryBase):
    """Categorize the length of a leg of a trajectory."""

    short = (3, lambda v, this_num:
        CategoryBase.default_criteria(v, "horizontal_distance", this_num))

    medium = (11.5, lambda v, this_num:
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
    sharp_left = (-6, lambda v, this_num:
        CategoryBase.default_criteria(v, "deflection_deg", this_num))

    left = (-2, lambda v, this_num:
        CategoryBase.default_criteria(v, "deflection_deg", this_num))

    straight = (2, lambda v, this_num:
        CategoryBase.default_criteria(v, "deflection_deg", this_num))

    right = (6, lambda v, this_num:
        CategoryBase.default_criteria(v, "deflection_deg", this_num))

    sharp_right = (360, lambda v, this_num: True)

class Level1Cat(CategoryBase):
    straight_reach = 0,
    s_curve = 1,
    j_hook = 2,
    u_turn = 3,
    grand_j_hook = 4


class Level2Cat(CategoryBase):
    left_turn = -1,
    straight = 0,
    right_turn = 1

    @property
    def symbology(self):
        if self == Level2Cat.left_turn:
            return kml_symbology(self.name, color='sky blue', width=3)
        elif self == Level2Cat.straight:
            return kml_symbology(self.name, color='white', width=3)
        elif self == Level2Cat.right_turn:
            return kml_symbology(self.name, color='vermillion', width=3)


class CategoryStateException(AttributeError):
    def __init__(self, msg):
        self.message = msg


def level2_categorize(leaf_node: ParseTreeNode.Parse_Tree_Leaf) -> Level2Cat:
    """If the leaf is zigzag, return None"""
    l2_cat = None
    leaf: EP = leaf_node.my_point

    if getattr(leaf, "may_be_zigzag", False):
        raise CategoryStateException('zigzag')

    if leaf.curvature_cat < CurvatureCat.flat:
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
    :param g: the graph to be ininuated into
    :param partitioned_tuple: lists of nodes at different levels
    :return: None
    """
    root, lev_1, lev_2, leaves = partitioned_tuple

    for an_L2_node in node_list:
        start, stop = an_L2_node.index_range
        g.add_node(an_L2_node)
        g.add_edge(root, an_L2_node)
        for a_leaf in leaves[start:stop]:
            g.remove_edge(root, a_leaf)
            g.add_edge(an_L2_node, a_leaf)


    dbg = True

def categorize_level3_to_level2(g: nxg.TreeDiGraph) -> None:
    """When you see a bunch of functions with numbers in the function names,
        it is a prediction that you will be refactoring later."""
    partitioned_tuple = ParseTreeNode.get_all_by_level(g)
    root, _1, _2, lev_3 = partitioned_tuple
    l2_node_list = ParseTreeNode.NodeListAtLevel(2)
    l2_node_list.start_new_with(lev_3[0], 0)
    l2_node_list.current.category = level2_categorize(lev_3[1]) # trouble here if CategoryStateException
    for a_node in lev_3[2:-1]:
        try:
            prospective_category = level2_categorize(a_node)
            keep_extending = \
                prospective_category == l2_node_list.current.category
        except CategoryStateException as ce:
            keep_extending = True
            # prospective_category is unchanged

        if keep_extending:
            l2_node_list.extend_with(a_node)
        else:
            l2_node_list.start_new_with(a_node)
            l2_node_list.current.category = prospective_category

    _insinuate_new_nodes_into_tree(l2_node_list, g, partitioned_tuple)

    dbg = True



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


