# Copyright (c) 2014-2023 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
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
# Date:   October, 24, 2017

import sys
import os
import unittest
import importlib

from tracktable.rw.read_write_json import trajectory_from_json
from tracktable.rw.read_write_json import json_from_trajectory
from tracktable.rw.read_write_json import json_file_from_trajectory
from tracktable.rw.read_write_json import trajectory_from_json_file

import tracktable.domain.terrestrial

from tracktable.core import Timestamp

class TestReadWriteDictionary(unittest.TestCase):
    def gen_json_and_trajectory(self):
        domain = tracktable.domain.terrestrial
        json = "{\"coordinates\": [[26.995, -81.9731], [27.0447, -81.9844], [27.1136, -82.0458]], \"domain\": \"terrestrial\", \"object_id\": \"AAA001\", \"point_properties\": {\"altitude\": {\"type\": \"float\", \"values\": [2700.0, 4200.0, 6700.0]}, \"heading\": {\"type\": \"float\", \"values\": [108.1, 108.2, 225.3]}, \"note\": {\"type\": \"str\", \"values\": [\"hello\", \"world\", \"!\"]}, \"time2\": {\"type\": \"datetime\", \"values\": [\"2004-01-01 00:00:01\", \"2004-01-01 00:00:02\", \"2004-01-01 00:00:03\"]}}, \"timestamps\": [\"2004-12-07 11:36:18\", \"2004-12-07 11:37:56\", \"2004-12-07 11:39:18\"], \"trajectory_properties\": {\"percent\": {\"type\": \"float\", \"value\": 33.333}, \"platform\": {\"type\": \"str\", \"value\": \"Boeing 747\"}, \"start\": {\"type\": \"datetime\", \"value\": \"2004-12-07 11:36:00\"}, \"tailNum\": {\"type\": \"str\", \"value\": \"3878\"}}}"

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
        p1.set_property('time2', Timestamp.from_string('2004-01-01 00:00:01'))
        p1.object_id = 'AAA001'
        p1.timestamp = Timestamp.from_string('2004-12-07 11:36:18', format_string='%Y-%m-%d %H:%M:%S')

        p2 = domain.TrajectoryPoint()
        p2[0] = 27.0447;
        if domain.DIMENSION > 1:
            p2[1] = -81.9844
        if domain.DIMENSION > 2:
            p2[2] = -101.0
        p2.set_property('altitude', 4200)
        p2.set_property('heading', 108.2)
        p2.set_property('note', "world")
        p2.set_property('time2', Timestamp.from_string('2004-01-01 00:00:02'))
        p2.object_id = 'AAA001'
        p2.timestamp = Timestamp.from_string('2004-12-07 11:37:56', format_string='%Y-%m-%d %H:%M:%S')

        p3 = domain.TrajectoryPoint()
        p3[0] = 27.1136;
        if domain.DIMENSION > 1:
            p3[1] = -82.0458
        if domain.DIMENSION > 2:
            p3[2] = -102.0
        p3.set_property('altitude', 6700)
        p3.set_property('heading', 225.3)
        p3.set_property('note', "!")
        p3.set_property('time2', Timestamp.from_string('2004-01-01 00:00:03'))
        p3.object_id = 'AAA001'
        p3.timestamp = Timestamp.from_string('2004-12-07 11:39:18', format_string='%Y-%m-%d %H:%M:%S')

        trajectory = domain.Trajectory.from_position_list([p1,p2,p3])
        trajectory.set_property('percent', 33.333)
        trajectory.set_property('platform', "Boeing 747")
        trajectory.set_property('start', Timestamp.from_string('2004-12-07 11:36:00'))
        trajectory.set_property('tailNum', '3878')

        return json, trajectory

    def tst_trajectory_from_json(self):
        print("Testing the conversion of a json string to a trajectory.")
        json, trajectoryExpected = self.gen_json_and_trajectory()
        trajectory = trajectory_from_json(json)

        self.assertEqual(trajectory, trajectoryExpected,
                         msg="Error: The trajectory generated from json does not match what"
                         "was expected")

    def tst_json_from_trajectory(self):
        print("Testing the conversion of a trajectory to a json string.")
        jsonExpected, trajectory = self.gen_json_and_trajectory()
        json = json_from_trajectory(trajectory)

        self.assertEqual(json, jsonExpected,
                         msg="Error: The json generated from the trajectory does not match "
                         "what was expected. \nGot     :"+str(json)+"\nExpected:"+str(jsonExpected))

    def tst_trajectory_from_json_file_from_trajectory(self):
        print("Testing the writing of a trajectory to a json file and reading it back in.")
        unused, trajectoryExpected = self.gen_json_and_trajectory()
        json_file_from_trajectory(trajectoryExpected, "_test-output.json")
        trajectory = trajectory_from_json_file("_test-output.json")
        os.remove("_test-output.json")

        self.assertEqual(trajectory, trajectoryExpected,
                         msg="Error: The trajectory read in from the file does not match the original trajectory written to the file")
    def test_json(self):
        self.maxDiff = 10240
        self.tst_trajectory_from_json()
        self.tst_json_from_trajectory()
        self.tst_trajectory_from_json_file_from_trajectory()

if __name__ == '__main__':
    unittest.main()


