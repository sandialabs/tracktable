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
# Date:   October, 24, 2017

import sys
import os
import inout
import unittest
import importlib

from tracktable.inout.trajectory import from_json
from tracktable.inout.trajectory import to_json
from tracktable.inout.trajectory import to_json_file
from tracktable.inout.trajectory import from_json_file
from tracktable.inout.trajectory import from_json_file_multi
#from tracktable.inout.trajectory import from_json_file_iter

import tracktable.inout.trajectory as trajectory

import tracktable.domain.terrestrial

from tracktable.core import Timestamp

class TestReadWriteDictionary(unittest.TestCase):
    def two_trajectories_json(self):
        return """[
{"coordinates": [[163.883, 51.75], [163.65, 51.65]], "domain": "terrestrial", "object_id": "JAL65", "point_properties": {"heading": {"type": "int", "values": [null, 235]}}, "timestamps": ["2013-07-01 05:55:03-0000", "2013-07-01 05:56:44-0000"], "trajectory_properties": {"ads_callsign": {"type": "str", "value": "JAL65"}, "altitude": {"type": "int", "value": 40000}, "destination": {"type": "str", "value": "RJAA"}, "iata_callsign": {"type": "str", "value": "JAL65"}, "origin": {"type": "str", "value": "KSAN"}, "route_faa": {"type": "str", "value": "SAN.PEBLE4.SLI.J169.LAX..GMN..EHF.J65.RBL.J1.OED.J501.HQM.J501.TOU..FINGS..JOWEN..LOHNE..ARCAL..6000N/16000W..NOLTI.R220.NANAC.Y810.KETAR.Y811.MELON..RJAA/0806"}, "status": {"type": "str", "value": "A"}}},
{"coordinates": [[179.683, 52.7333], [179.9, 52.8], [-179.833, 52.9]], "domain": "terrestrial", "object_id": "ANA12", "point_properties": {"altitude": {"type": "int", "values": [0, 0, 31000]}, "heading": {"type": "int", "values": [61, 63, 58]}, "speed": {"type": "int", "values": [590, 570, 570]}}, "timestamps": ["2013-07-01 05:54:26-0000", "2013-07-01 05:55:26-0000", "2013-07-01 05:56:20-0000"], "trajectory_properties": {"ads_callsign": {"type": "str", "value": "ANA12"}, "destination": {"type": "str", "value": "KORD"}, "iata_callsign": {"type": "str", "value": "ANA12"}, "origin": {"type": "str", "value": "RJAA"}, "route_faa": {"type": "str", "value": "JAA..CUPID.Y808.ALLEN.Y812.SCORE.R591.ADNAP.OTR5.KALNA.G344.CRYPT.G344.CUDDA..ODK..5720N/14000W..BKA..LVD..YQU.J515.YWG.J89.DLH.J538.DLL..MSN.V9.JVL.V97.BULLZ.BULLZ5.KORD/1105"}, "status": {"type": "str", "value": "A"}}}
]
"""

    def gen_json_and_trajectory(self):
        format = '%Y-%m-%d %H:%M:%S%z'
        domain = tracktable.domain.terrestrial
        json = ('{\"coordinates\": [[26.995, -81.9731], [27.0447, -81.9844], '
                '[27.1136, -82.0458]], \"domain\": \"terrestrial\", '
                '\"object_id\": \"AAA001\", \"point_properties\": '
                '{\"altitude\": {\"type\": \"int\", \"values\": '
                '[2700, 4200, 6700]}, \"heading\": {\"type\": \"float\",'
                ' \"values\": [108.1, 108.2, 225.3]}, \"note\": {\"type\":'
                ' \"str\", \"values\": [\"hello\", \"world\", \"!\"]},'
                ' \"time2\": {\"type\": \"timestamp\", \"values\":'
                ' [\"2004-01-01 00:00:01-0000\", \"2004-01-01 00:00:02-0000\",'
                ' \"2004-01-01 00:00:03-0000\"]}}, \"timestamps\":'
                ' [\"2004-12-07 11:36:18-0000\", \"2004-12-07 11:37:56-0000\",'
                ' \"2004-12-07 11:39:18-0000\"], \"trajectory_properties\":'
                ' {\"percent\": {\"type\": \"float\", \"value\": 33.333},'
                ' \"platform\": {\"type\": \"str\", \"value\":'
                ' \"Boeing 747\"}, \"start\": {\"type\": \"timestamp\",'
                ' \"value\": \"2004-12-07 11:36:00-0000\"}, \"tailNum\":'
                ' {\"type\": \"int\", \"value\": 3878}}}')

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
                                              format_string =format))
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
                                              format_string =format))
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
                                              format_string =format))
        p3.object_id = 'AAA001'
        p3.timestamp =Timestamp.from_string('2004-12-07 11:39:18-0000',
                                            format_string=format)

        trajectory = domain.Trajectory.from_position_list([p1,p2,p3])
        trajectory.set_property('percent', 33.333)
        trajectory.set_property('platform', "Boeing 747")
        trajectory.set_property('start',
                                Timestamp.from_string(
                                    '2004-12-07 11:36:00-0000',
                                    format_string =format))
        trajectory.set_property('tailNum', 3878)

        return json, trajectory

    def tst_trajectory_from_json(self):
        print("Testing the conversion of a json string to a trajectory.")
        json, trajectoryExpected = self.gen_json_and_trajectory()
        trajectory = from_json(json)

        self.assertEqual(trajectory, trajectoryExpected,
                         msg="Error: The trajectory generated from json does"
                         + " not match what was expected")

    def tst_json_from_trajectory(self):
        print("Testing the conversion of a trajectory to a json string.")
        jsonExpected, trajectory = self.gen_json_and_trajectory()
        json = to_json(trajectory)

        self.assertEqual(json, jsonExpected,
                         msg="Error: The json generated from the trajectory"
                         + " does not match what was expected. \nGot     :"
                         + str(json)+"\nExpected:"+str(jsonExpected))

    def tst_trajectory_from_json_file_from_trajectory(self):
        print("Testing the writing of a trajectory to a json file and reading"
              + " it back in.")
        unused, trajectoryExpected = self.gen_json_and_trajectory()
        to_json_file(trajectoryExpected, "_test-output.json")
        trajectory = from_json_file("_test-output.json")
        os.remove("_test-output.json")

        self.assertEqual(trajectory, trajectoryExpected,
                         msg="Error: The trajectory read in from the file"
                         + " does not match the original trajectory written"
                         + " to the file")

    def tst_multi_trajectories_from_json_file(self):
        print("Testing reading multiple trajectories from a json file")
        trajs = []
        with inout.StringIO() as f:
            f.write(self.two_trajectories_json())
            f.seek(0)
            for traj in trajectory.from_json_file_iter(f):
                trajs.append(traj)
        out = trajectory.to_json_multi(trajs)
        self.assertEqual(out, self.two_trajectories_json())

    def test_json(self):
        self.tst_trajectory_from_json()
        self.tst_json_from_trajectory()
        self.tst_trajectory_from_json_file_from_trajectory()
        self.tst_multi_trajectories_from_json_file()

if __name__ == '__main__':
    unittest.main()

