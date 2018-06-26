import enum
from typing import Any, Union

_huge_number = 1000000

class CategoryBase(enum.Enum):
    """Base class for all parse tree categorizations."""
    def __init__(self, num, criteria=None):
        self.num = num
        self.criteria_lambda = criteria

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

    gentle_left = (-1, lambda v, this_num:
        CategoryBase.default_criteria(v, "degree_curve", this_num))

    flat = (1, lambda v, this_num:
        CategoryBase.default_criteria(v, "degree_curve", this_num))

    gentle_right = (4, lambda v, this_num:
        CategoryBase.default_criteria(v, "degree_curve", this_num))

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


if __name__ == '__main__':
    try:
        _test_run()
    except KeyboardInterrupt:
        exit(0)


