/*
 * Copyright (c) 2014-2020 National Technology and Engineering
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

// Python documentation string for tracktable.domain.<domain>.TrajectoryPoint

namespace tracktable {
namespace python_wrapping {
namespace docstrings {

const char* GenericTrajectoryPointDocString =
    "This class will add trajectory properties (a timestamp, an object\n"
    "ID and storage for named properties) to any point class.\n"
    "\n"
    "Accesors and operators are wrapped under: \n"
    "   * __init__: Create new point \n"
    "   * __getitem__: Access the point values \n"
    "   * __setitem__: Set the point values \n"
    "   * __len__: Get point dimension \n"
    "   * __add__: Add \n"
    "   * __iadd__: Add in place \n"
    "   * __sub__: Subtract \n"
    "   * __isub__: Subtract in place \n"
    "   * __mul__: Multiply \n"
    "   * __imul__: Multiply in place \n"
    "   * __div__: Divide \n"
    "   * __idiv__: Divide in place \n"
    "   * __mul__: Multiply scalar \n"
    "   * __rmul__: Multiply scalar \n"
    "   * __imul__: Multiply scalar in place \n"
    "   * __div__: Divide scalar \n"
    "   * __rdiv__: Divide scalar in place \n"
    "   * __idiv__: Divide scalar in place \n"
    "\n"
    "To string operations are wrapped under the standard to-string methods:\n"
    "   * __str__\n"
    "   * __repr__\n"
    "\n"
    "Attributes: \n"
    "   point (<domain>Point): A tuple representing the long-lat points of the given domain\n"
    "   properties (dict): Property values of the point\n"
    "   object_id (str): The ID of the point\n"
    "   timestamp (str): Timestamp for the point\n"
    "   current_length (int): length of trajectory\n"
    "   domain (str): Domian that the point is in\n"
    "\n"
    "Methods: \n"
    "   set_property (str name, property value): Set the give property value\n"
    "   has_property (str name): Check whether a property is present \n"
    "   property (str name): Retrieve a named property\n"
    ;

}}}


