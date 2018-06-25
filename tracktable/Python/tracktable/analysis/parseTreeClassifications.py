import enum


class CategoryBase(enum.Enum):
    def __init__(self, num, criteria=None):
        self.num = num
        self.criteria_lambda = criteria

    @classmethod
    def assign_to(cls, a_parse_tree_node, new_attr_name):
        dbg = True
        for enm in cls:
            if enm.criteria_lambda(a_parse_tree_node):
                setattr(a_parse_tree_node, new_attr_name, enm)
                return
        else:
            # a_parse_tree_node.leg_length_cat = cls[-1]
            setattr(a_parse_tree_node, new_attr_name, cls[-1])
            return

class LegLengthCat(CategoryBase):
    single_point = (1, lambda v: len(v) == 1)
    short = (2, lambda v: v.horizontal_distance <= 4.0)
    medium = (3, lambda v: v.horizontal_distance <= 15.0)
    long = (4, lambda v: True)


class CurvatureCat(CategoryBase):
    hard_left = (-3, lambda v: v.degree_curve <= -12.0)
    normal_left = (-2, lambda v: v.degree_curve <= -4.0)
    gentle_left = (-1, lambda v: v.degree_curve <= -1.0)
    straight = (0, lambda v: v.degree_curve <= 1.0)
    gentle_right = (1, lambda v: v.degree_curve <= 4.0)
    normal_right = (2, lambda v: v.degree_curve <= 12.0)
    hard_right = (3, lambda v: True)


def _test_run():
    class _temp_():
        def __init__(self, dist=1.0):
            self.horizontal_distance = dist

    class _whatever(list):
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
    aList = _whatever([v1, v2])

    LegLengthCat.assign_to(aList, 'leg_length_cat')
    print('Test length = ', aList.leg_length_cat)
    print(type(aList.leg_length_cat).__name__,
          aList.leg_length_cat.name,
          type(aList.leg_length_cat.name))

    print()
    CurvatureCat.assign_to(aList, 'curvature_cat')
    print("Curvature Category: ", aList.curvature_cat)


if __name__ == '__main__':
    _test_run()


