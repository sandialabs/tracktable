# Copyright (c) 2017, National Technology & Engineering Solutions of
#   Sandia, LLC (NTESS).
# All rights reserved.
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

# Author: Ben Newton
# Date:   October, 19, 2017

import sys

from tracktable.inout.trajectory import from_dict
from tracktable.inout.trajectory import to_dict
from tracktable.core import Timestamp
import importlib
import unittest

class TestReadWriteDictionary(unittest.TestCase):

    domains = ['terrestrial', 'cartesian2d', 'cartesian3d']

    def gen_dictionary_and_trajectory(self, domainString):
        format = '%Y-%m-%d %H:%M:%S%z'
        domain = importlib.import_module("tracktable.domain."
                                         + domainString.lower())

        # Manually set up a dictionary which contains trajectory info
        dictionary = {
         'domain'               : domainString.lower(),
         'object_id'            : 'AAA001',
         'trajectory_properties':{'percent' : {'type' :'float',
                                               'value':33.333},
                                  'platform': {'type' :'str',
                                               'value':"Boeing 747"},
                                  'start'   : {'type' :'timestamp',
                                               'value':\
                                               "2004-12-07 11:36:00-0000"},
                                  'tailNum' : {'type': 'int',
                                               'value': 3878}},
         'timestamps'           : ['2004-12-07 11:36:18-0000',
                                   '2004-12-07 11:37:56-0000',
                                   '2004-12-07 11:39:18-0000'],
         'point_properties': {'altitude': {'type': 'int',
                                           'values': [2700, 4200, 6700]},
                              'heading' : {'type': 'float',
                                           'values': [108.1, 108.2, 225.3]},
                              'note'    : {'type': 'str',
                                           'values': ["hello", "world", "!"]},
                              'time2'   : {'type': 'timestamp',
                                           'values': \
                                           ["2004-01-01 00:00:01-0000",
                                            "2004-01-01 00:00:02-0000",
                                            "2004-01-01 00:00:03-0000"]}}
        }
        if domain.DIMENSION == 1:
            dictionary.update({'coordinates' : [(26.995),
                                                (27.0447),
                                                (27.1136)]})
        if domain.DIMENSION == 2:
            dictionary.update({'coordinates' : [(26.995, -81.9731),
                                                (27.0447, -81.9844),
                                                (27.1136, -82.0458)]})
        if domain.DIMENSION == 3:
            dictionary.update({'coordinates' : [(26.995, -81.9731, -100.0),
                                                (27.0447, -81.9844, -101.0),
                                                (27.1136, -82.0458, -102.0)]})

        # Manually set up a matching Trajectory object
        p1 = domain.TrajectoryPoint()
        p1[0] = 26.995;
        if domain.DIMENSION > 1:
            p1[1] = -81.9731
        if domain.DIMENSION > 2:
            p1[2] = -100.0
        p1.set_property('altitude', 2700)
        p1.set_property('heading', 108.1)
        p1.set_property('note', "hello")
        p1.set_property('time2',
                        Timestamp.from_string('2004-01-01 00:00:01-0000',
                                              format_string = format))
        p1.object_id = 'AAA001'
        p1.timestamp =Timestamp.from_string('2004-12-07 11:36:18-0000',
                                            format_string=format)

        p2 = domain.TrajectoryPoint()
        p2[0] = 27.0447;
        if domain.DIMENSION > 1:
            p2[1] = -81.9844
        if domain.DIMENSION > 2:
            p2[2] = -101.0
        p2.set_property('altitude', 4200)
        p2.set_property('heading', 108.2)
        p2.set_property('note', "world")
        p2.set_property('time2',
                        Timestamp.from_string('2004-01-01 00:00:02-0000',
                                              format_string = format))
        p2.object_id = 'AAA001'
        p2.timestamp =Timestamp.from_string('2004-12-07 11:37:56-0000',
                                            format_string=format)

        p3 = domain.TrajectoryPoint()
        p3[0] = 27.1136;
        if domain.DIMENSION > 1:
            p3[1] = -82.0458
        if domain.DIMENSION > 2:
            p3[2] = -102.0
        p3.set_property('altitude', 6700)
        p3.set_property('heading', 225.3)
        p3.set_property('note', "!")
        p3.set_property('time2',
                        Timestamp.from_string('2004-01-01 00:00:03-0000',
                                              format_string = format))
        p3.object_id = 'AAA001'
        p3.timestamp =Timestamp.from_string('2004-12-07 11:39:18-0000',
                                            format_string=format)

        trajectory = domain.Trajectory.from_position_list([p1,p2,p3])
        trajectory.set_property('percent', 33.333)
        trajectory.set_property('platform', "Boeing 747")
        trajectory.set_property('start',
                                Timestamp.from_string(
                                    '2004-12-07 11:36:00-0000',
                                    format_string = format))
        trajectory.set_property('tailNum', 3878)

        return dictionary, trajectory

    def tst_trajectory_from_dictionary(self, domain):
        print("Testing the conversion of a dictionary to a trajectory in the "
              +domain+" domain.")
        dict, trajectoryExpected = self.gen_dictionary_and_trajectory(domain)

        trajectory = from_dict(dict)

        self.assertEqual(trajectory, trajectoryExpected,
                         msg="Error: The "+domain+" trajectory generated from"
                         + " dictionary does not match what was expected")

    def tst_dictionary_from_trajectory(self, domain):
        print("Testing the conversion of a trajectory to a dictionary in the "
              + domain + " domain.")
        dictExpected, trajectory = self.gen_dictionary_and_trajectory(domain)

        dictionary = to_dict(trajectory)

        self.assertEqual(dictionary, dictExpected,
                         msg="Error: The " + domain + " dictionary generated"
                         + " from the trajectory does not match what was "
                         + "expected. \nGot     :"+str(dictionary)
                         + "\nExpected:"+str(dictExpected))

    def tst_dictionary_to_trajectory_to_dictionary(self, domain):
        print("Testing the conversion of a dictionary to a trajectory and"
              + " back to a dictionary in the "+domain+" domain.")
        dictionary, unused = self.gen_dictionary_and_trajectory(domain)

        dictionaryFinal = to_dict(from_dict(dictionary))

        self.assertEqual(dictionary, dictionaryFinal,
                         msg="Error: The "+domain+" dictionary generated from"
                         + " the trajectory generated from a dictionary does"
                         + " not match what was expected")

    def tst_trajectory_to_dictionary_to_trajectory(self, domain):
        print("Testing the conversion of a trajectory to a dictionary and"
              + " back to a trajectory in the "+domain+" domain.")
        dictUnused, trajectory = self.gen_dictionary_and_trajectory(domain)

        trajectoryFinal = from_dict(to_dict(trajectory))

        self.assertEqual(trajectory, trajectoryFinal,
                         msg="Error: The "+domain+" trajectory generated from"
                         + " the dictionary generated from a trajectory does"
                         + " not match what was expected")

    def tst_trajectory_from_invalid_coordinates(self, domain):
        print("Testing the conversion of a dictionary with invalid"
              + " coordinates in the " + domain + " domain.")
        dictionary, unused = self.gen_dictionary_and_trajectory(domain)

        #remove last element of coordinate 0
        dictionary['coordinates'][0] = dictionary['coordinates'][0][:-1]
        with self.assertRaises(ValueError) as ctx:
            from_dict(dictionary)
        #optionally, can use this to ensure message is correct
        #self.assertEqual(ctx.exception.message, "..."   )

    def tst_trajectory_from_invalid_point_properties(self, domain):
        print("Testing the conversion of a dictionary with invalid point"
              + " properties in the "+domain+" domain.")
        dictionary, unused = self.gen_dictionary_and_trajectory(domain)

        # test point properties lists don't match length of coordinates by
        # removing last element of the altitude list
        newValues = dictionary['point_properties']['altitude']['values'][:-1]
        dictionary['point_properties']['altitude']['values'] = newValues

        with self.assertRaises(ValueError) as ctx:
            from_dict(dictionary)
        #print(ctx.exception.message)

    def tst_trajectory_from_invalid_timestamps(self, domain):
        print("Testing the conversion of a dictionary with invalid timestamps"
              + " in the "+domain, " domain.")
        dictionary, unused = self.gen_dictionary_and_trajectory(domain)

        # test a timestamp list that doesn't match length of coordinates by
        # removing last timestamp
        dictionaryBad3 = dictionary.copy()
        dictionaryBad3['timestamps'] = dictionaryBad3['timestamps'][:-1]
        with self.assertRaises(ValueError) as ctx:
            from_dict(dictionaryBad3)

    def tst_invalid_domain(self):
        print("Testing invalid domain")
        dictBad, unused = self.gen_dictionary_and_trajectory("terrestrial")
        dictBad['domain'] = "invalid"
        with self.assertRaises(ValueError) as ctx:
            from_dict(dictBad)

    def tst_invalid_object_id(self):
        print("Testing invalid object_id")
        dictBad, unused = self.gen_dictionary_and_trajectory("terrestrial")
        dictBad['object_id'] = 2
        with self.assertRaises(ValueError) as ctx:
            from_dict(dictBad)

    def test_dictionary(self):
        for domain in self.domains:
            self.tst_dictionary_from_trajectory(domain)
            self.tst_trajectory_from_dictionary(domain)
            self.tst_dictionary_to_trajectory_to_dictionary(domain)
            self.tst_trajectory_to_dictionary_to_trajectory(domain)
            self.tst_trajectory_from_invalid_coordinates(domain)
            self.tst_trajectory_from_invalid_point_properties(domain)
            self.tst_trajectory_from_invalid_timestamps(domain)
        self.tst_invalid_domain()
        self.tst_invalid_object_id()

if __name__ == '__main__':
    unittest.main()
