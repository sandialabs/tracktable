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
# Date:   November, 29, 2017

#Example: python3 asdiToJson.py /ascldap/users/bdnewto/research/edamame/data/asdi/asdi_july_2013.tsv out2.json
#Example python3 asdiToJson.py /ascldap/users/bdnewto/research/edamame/data/asdi/asdi_july_2013.tsv /data/edamame/july_2013.json


from tracktable.source.trajectory import AssembleTrajectoryFromPoints
from tracktable.domain import all_domains as ALL_DOMAINS
from tracktable.examples import example_point_reader
from tracktable.io.trajectory import to_json, to_json_file

import importlib
import datetime
import argparse

def remove_nulls(traj):
    for i in range(len(traj)):
        for (name, value) in traj[i].properties.items():
            if value == None:
                del traj[i].properties[name]

def make_trajectory_properties(traj):
    for (name, value) in traj[0].properties.items():
        all_same=True
        for i in range(len(traj)):
            if name not in traj[i].properties or \
            traj[i].properties[name] != traj[0].properties[name]:  #could avoid 0 to optimize
                all_same=False
                break
        if(all_same):
            traj.set_property(name, traj[0].properties[name]) #make it a trajectory property
            for i in range(len(traj)):
                del traj[i].properties[name] #remove point properties

#add later!!!!
#if only value once make trajectory property # todo may be able to combine with above?
#def make_trajectory_properties_single_value(traj):
#    counts = {}
#
#
#    for (name, value) in traj[0].properties.items():
#        only_once = True
#        seen_once=False
#        for i in range(len(traj)):
#            if name in traj[i].properties:
#                if seen_once: #seen again
#                    only_once = False
#                    break
#                else:
#                    seen_once = True
#        if(only_once):
#            traj.set_property(name, traj[0].properties[name]) #make it a trajectory property
#            for i in range(len(traj)):
#                del traj[i].properties[name] #remove point properties


parser = argparse.ArgumentParser(description='Convert ASDI .tsv file to JSON.')
parser.add_argument('asdi_file', type=argparse.FileType('r'))
parser.add_argument('json_file', type=argparse.FileType('w'))
args = parser.parse_args()

infile = args.asdi_file #open("/ascldap/users/bdnewto/research/edamame/data/asdi/asdi_july_2013.tsv", 'rb')

domain = "terrestrial"
if domain.lower() not in ALL_DOMAINS:
    raise KeyError("Domain '{}' is not in list of installed domains ({}).".format(domain, ', '.join(ALL_DOMAINS)))
else:
    domain_to_import = 'tracktable.domain.{}'.format(domain.lower())
    domain_module = importlib.import_module(domain_to_import)

reader = domain_module.TrajectoryPointReader()
reader.input = infile
#reader.set_warnings_enabled(False) #not recognized
#reader.set_timestamp_format()# try todo

#reader.set_null_value("") # doesn't work
reader.field_delimiter = "\t"
reader.object_id_column = 0
reader.timestamp_column = 1
reader.coordinates[0] = 2
reader.coordinates[1] = 3
reader.set_integer_field_column("speed", 4)
reader.set_integer_field_column("heading", 5)
reader.set_integer_field_column("altitude", 6)
reader.set_string_field_column("ads_callsign", 7)
reader.set_string_field_column("iata_callsign", 8)
reader.set_string_field_column("squawk", 9) #is this ever not empty?
reader.set_string_field_column("status", 10)
reader.set_string_field_column("aircraft_category", 11)
reader.set_string_field_column("aircraft_construction_number", 12)
reader.set_string_field_column("registration", 13)
reader.set_string_field_column("aircraft_type", 14)
reader.set_string_field_column("aircraft_type_full", 15)
reader.set_string_field_column("airframe_mode_s_id", 16)
reader.set_string_field_column("operator_category", 17)
reader.set_string_field_column("airline", 18)
reader.set_string_field_column("airline_iata", 19)
reader.set_string_field_column("airline_icao", 20)
reader.set_time_field_column("scheduled_arrival_time", 21)
reader.set_time_field_column("scheduled_departure_time", 22)
reader.set_time_field_column("actual_arrival_time", 23)
reader.set_time_field_column("actual_departure_time", 24)
reader.set_string_field_column("origin", 25)
reader.set_string_field_column("origin_full", 26)
reader.set_string_field_column("origin_iata", 27)
reader.set_real_field_column("origin_longitude", 28)
reader.set_real_field_column("origin_latitude", 29)
reader.set_string_field_column("destination", 30)
reader.set_string_field_column("destination_full", 31)
reader.set_string_field_column("destination_iata", 32)
reader.set_real_field_column("destination_longitude", 33)
reader.set_real_field_column("destination_latitude", 34)
reader.set_real_field_column("distance_from_origin", 35)
reader.set_real_field_column("distance_to_destination", 36)
reader.set_real_field_column("distance_from_origin_to_destination", 37)
reader.set_real_field_column("percent_complete", 38)
reader.set_string_field_column("is_general_aviation", 39)
reader.set_string_field_column("is_general_aviation", 40)
reader.set_string_field_column("route", 41)
reader.set_string_field_column("route_faa", 42)
reader.set_string_field_column("route_full", 43)
reader.set_string_field_column("route_iata", 44)
reader.set_string_field_column("sending_center_id", 45)
reader.set_string_field_column("sending_center_id_full", 46)
reader.set_string_field_column("waypoints", 47)

trajectory_assembler = AssembleTrajectoryFromPoints()
trajectory_assembler.input = reader
trajectory_assembler.separation_time = datetime.timedelta(minutes=10) #assumed max separation time? correct?
trajectory_assembler.separation_distance = 100  #what are the units
trajectory_assembler_minimum_length = 20 #samples

assembleAll = True
numberToAssemble = 5
numberAssembled = 0

args.json_file.write("[\n")

for traj in trajectory_assembler.trajectories():
    remove_nulls(traj)
    make_trajectory_properties(traj)
    #make_trajectory_properties_single_value(traj)
    if numberAssembled != 0:
        args.json_file.write(",\n") #coma newline before each except first
    args.json_file.write(to_json(traj))

    numberAssembled+=1
    if not assembleAll:
        if numberAssembled >= numberToAssemble:
            break;
args.json_file.write("\n]")

#all_trajectories = list(trajectory_assembler.trajectories())
#print(len(all_trajectories[0]))

#to_json(all_trajectories[0], "output.json")
