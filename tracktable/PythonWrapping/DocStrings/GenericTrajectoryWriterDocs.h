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

// Python documentation string for tracktable.domain.<domain>.TrajectoryWriter

namespace tracktable {
namespace python_wrapping {
namespace docstrings {

const char* GenericTrajectoryWriterDocString =
    "Write trajectories of any type as delimited text \n"
    "\n"
    "This class writes subclasses of tracktable::Trajectory (including \n"
    "the domain classes) to a stream as delimited text.  It will write \n"
    "one trajectory per line.  The resulting file will contain enough \n"
    "header information to reconstruct the trajectory exactly as long as \n"
    "the user asks for the correct class. \n"
    "\n"
    "Attributes: \n"
    "   write_header (bool): Flag to write a header. The header string describes the contents of a point: coordinate"
    "       system, properties (if any), number of coordinates.  By default it will be written at the beginning of a sequence of points.\n "
    "   output (object): Python object to write to\n"
    "   field_delimiter (str): Designated character for delimiting fields (Default: whitespace) \n"
    "   null_value (str): Value indicating null value \n"
    "   record_delimiter (str): The record separator (end-of-line string). This string will be written after each point.\n"
    "   coordinate_precision (float): The decimal precision for writing coordinates\n"
    "   quote_character (str): The quote character. This character *may* be used to enclose a field containing lots\n"
    "       of characters that would otherwise need to be escaped.\n"
    "\n"
    "Methods: \n"
    "   write (iter trajectory_start, trajectory_ end): Write many trajectories\n"
    ;

}}}


