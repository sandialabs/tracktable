import enum


class Classifications_base(enum.Enum):
    @classmethod
    def create(cls):
        raise NotImplementedError('This class must override the create()'
                                  'method')

class leg_length(enum.Enum):
    single_point = (1, lambda v: len(v) == 1)
    short = (2, lambda v: v.horizontal_distance <= 4.0)
    medium = (3, lambda v: v.horizontal_distance <= 15.0)
    long = (4, lambda v: True)

    def __init__(self, num, criteria=None):
        self.num = num
        self.criteria_lambda = criteria

    @classmethod
    def assign_to(cls, a_parse_tree_node):
        for enm in leg_length:
            if enm.criteria_lambda(a_parse_tree_node):
                a_parse_tree_node.leg_length = enm
                return
        else:
            a_parse_tree_node.leg_length = leg_length[-1]
            return



def _test_run():
    print('whatup')

    # for val in leg_length:
    #     print(val.num, val)
    #
    # val = leg_length.single_point
    # print('Name:', leg_length.single_point)
    # print('Value:', leg_length.single_point.value)
    # print('Custom attribute:', leg_length.single_point.criteria_lambda)
    # print('Lambda result:', leg_length.single_point.criteria_lambda([1]))

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

    v1 = _temp_(1.0)
    v2 = _temp_(2.0)
    aList = _whatever([v1, v2])

    leg_length.assign_to(aList)
    dbg = True


if __name__ == '__main__':
    _test_run()


