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

from tracktable.io.read_write_dictionary import trajectory_from_dictionary
from tracktable.io.read_write_dictionary import dictionary_from_trajectory
from tracktable.core import Timestamp
import importlib
import unittest

class TestReadWriteDictionary(unittest.TestCase):

    domains = ['terrestrial', 'cartesian2d', 'cartesian3d']

    def gen_dictionary_and_trajectory(self, domainString):
        domain = importlib.import_module("tracktable.domain."+domainString.lower())

        # Manually set up a dictionary which contains trajectory info
        dictionary = {'domain'        : domainString.lower(),
                      'trajectoryPropNames' : ['platform', 'start'],
                      'trajectoryProp0'     : 747,
                      'trajectoryProp1'     : "2004-12-07 11:36:00",
                      'propertyNames' : ['altitude', 'heading', 'note', 'speed'],
                      'object_id'     : 'AAA001',
                      'timestamps'    : ['2004-12-07 11:36:18',#-0000',
                                         '2004-12-07 11:37:56',#-0000',
                                         '2004-12-07 11:39:18'],#-0000'],
                      'property0'     : [2700, 4200, 6700],
                      'property1'     : [108, 108, 225],
                      'property2'     : ["hello", "world", "!"],
                      'property3'     : [0, -27, -22]}
        if domain.DIMENSION == 1:
            dictionary.update({'coordinates' : [(26.995), (27.0447), (27.1136)]})
        if domain.DIMENSION == 2:
            dictionary.update({'coordinates' : [(26.995, -81.9731), (27.0447, -81.9844), (27.1136, -82.0458)]})
        if domain.DIMENSION == 3:
            dictionary.update({'coordinates' : [(26.995, -81.9731, -100.0), (27.0447, -81.9844, -101.0), (27.1136, -82.0458, -102.0)]})

        # Manually set up a matching Trajectory object
        p1 = domain.TrajectoryPoint()
        p1[0] = 26.995;
        if domain.DIMENSION > 1:
            p1[1] = -81.9731
        if domain.DIMENSION > 2:
            p1[2] = -100.0
        p1.set_property('altitude', 2700)
        p1.set_property('heading', 108)
        p1.set_property('note', "hello")
        p1.set_property('speed', 0)
        p1.object_id = 'AAA001'
        p1.timestamp = Timestamp.from_string('2004-12-07 11:36:18', format_string='%Y-%m-%d %H:%M:%S')

        p2 = domain.TrajectoryPoint()
        p2[0] = 27.0447;
        if domain.DIMENSION > 1:
            p2[1] = -81.9844
        if domain.DIMENSION > 2:
            p2[2] = -101.0
        p2.set_property('altitude', 4200)
        p2.set_property('heading', 108)
        p2.set_property('note', "world")
        p2.set_property('speed', -27)
        p2.object_id = 'AAA001'
        p2.timestamp = Timestamp.from_string('2004-12-07 11:37:56', format_string='%Y-%m-%d %H:%M:%S')

        p3 = domain.TrajectoryPoint()
        p3[0] = 27.1136;
        if domain.DIMENSION > 1:
            p3[1] = -82.0458
        if domain.DIMENSION > 2:
            p3[2] = -102.0
        p3.set_property('altitude', 6700)
        p3.set_property('heading', 225)
        p3.set_property('note', "!")
        p3.set_property('speed', -22)
        p3.object_id = 'AAA001'
        p3.timestamp = Timestamp.from_string('2004-12-07 11:39:18', format_string='%Y-%m-%d %H:%M:%S')

        trajectory = domain.Trajectory.from_position_list([p1,p2,p3])
        trajectory.set_property('platform', 747)
        trajectory.set_property('start', "2004-12-07 11:36:00")
        #trajectory.set_property('start', Timestamp.from_string('2004-12-07 11:36:00'))

        return dictionary, trajectory

    def tst_trajectory_from_dictionary(self, domain):
        print "Testing the conversion of a dictionary to a trajectory in the", domain, "domain."
        dictionary, trajectoryExpected = self.gen_dictionary_and_trajectory(domain)

        trajectory = trajectory_from_dictionary(dictionary)

        self.assertEqual(trajectory, trajectoryExpected,
                         msg="Error: The "+domain+" trajectory generated from dictionary does not match what"
                         "was expected")

    def tst_dictionary_from_trajectory(self, domain):
        print "Testing the conversion of a trajectory to a dictionary in the", domain, "domain."
        dictionaryExpected, trajectory = self.gen_dictionary_and_trajectory(domain)

        dictionary = dictionary_from_trajectory(trajectory)

        self.assertEqual(dictionary, dictionaryExpected,
                         msg="Error: The "+domain+" dictionary generated from the trajectory does not match "
                         "what was expected. \nGot     :"+str(dictionary)+"\nExpected:"+str(dictionaryExpected))

    def tst_dictionary_to_trajectory_to_dictionary(self, domain):
        print "Testing the conversion of a dictionary to a trajectory and back to a dictionary in the", domain,
        "domain."
        dictionary, unused = self.gen_dictionary_and_trajectory(domain)

        dictionaryFinal = dictionary_from_trajectory(trajectory_from_dictionary(dictionary))

        self.assertEqual(dictionary, dictionaryFinal,
                         msg="Error: The "+domain+" dictionary generated from the trajectory generated from a "
                         "dictionary does not match what was expected")

    def tst_trajectory_to_dictionary_to_trajectory(self, domain):
        print "Testing the conversion of a trajectory to a dictionary and back to a trajectory in the", domain,
        "domain."
        dictionaryUnused, trajectory = self.gen_dictionary_and_trajectory(domain)

        trajectoryFinal = trajectory_from_dictionary(dictionary_from_trajectory(trajectory))

        self.assertEqual(trajectory, trajectoryFinal,
                         msg="Error: The "+domain+" trajectory generated from the dictionary generated from a "
                         "trajectory does not match what was expected")

    def tst_trajectory_from_invalid_dictionary(self, domain):
        print "Testing the conversion of an invalid dictionary to a trajectory in the", domain, "domain."
        dictionary, unused = self.gen_dictionary_and_trajectory(domain)

        dictionary['coordinates'][0] = dictionary['coordinates'][0][:-1] #remove last element of coordinate 0
        with self.assertRaises(ValueError) as ctx:
            trajectory_from_dictionary(dictionary)
        #self.assertEqual(ctx.exception.message, "..."   )#can use this to ensure message is correct

    def test_dictionary(self):
        for domain in self.domains:
            self.tst_dictionary_from_trajectory(domain)
            self.tst_trajectory_from_dictionary(domain)
            self.tst_dictionary_to_trajectory_to_dictionary(domain)
            self.tst_trajectory_to_dictionary_to_trajectory(domain)
            self.tst_trajectory_from_invalid_dictionary(domain)

if __name__ == '__main__':
    unittest.main()
