/*
 * Copyright (c) 2014-2023 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

// Python documentation string for tracktable.domain.<domain>.Trajectory

namespace tracktable {
namespace python_wrapping {
namespace docstrings {

const char* GenericTrajectoryDocString =
    "This class is the heart of most of what Tracktable does.  It \n"
    "implements an ordered sequence of TrajectoryPoint objects, each of \n"
    "which has an ID, coordinates and a timestamp.  Those compose a \n"
    "trajectory. Object can be serialized for given type/property map.\n"
    "\n"
    "Attributes: \n"
    "   properties (dict): Property values of the trajectory\n"
    "   duration (float): The duration of the trajectory\n"
    "   domain (str): Domian that the point is in\n"
    "   trajectory_id (str): The ID of the trajectory\n"
    "   object_id (str): The ID of the point\n"
    "\n"
    "Methods: \n"
    "   set_property (str name, property value): Set the give property value\n"
    "   has_property (str name): Check whether a property is present \n"
    "   property (str name): Retrieve a named property\n"
    "   from_position_list (list points): Create a list of trajectories from a list of iterables\n"
    "   insert (int indea, point value): Insert a single element into the trajectory at an arbitrary index\n"
    "   clone (): Make this trajectory a clone of another \n"
    ;

}}}


