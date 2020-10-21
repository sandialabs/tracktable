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

// Python documentation string for tracktable.domain.<domain>.TrajectoryPointReader

namespace tracktable {
namespace python_wrapping {
namespace docstrings {

const char* GenericTrajectoryPointReaderDocString =
    "Class for reading trajectory points from a file. \n"
    "\n"
    "This reader wraps the following pipeline: \n"
    "   - Read lines from a text file \n"
    "   - Skip any lines that begin with a designated comment character \n"
    "   - Tokenize each line using specified delimiters  \n"
    "   - Create a point (user-specified type) from each tokenized line \n"
    "   - Return the resulting points via a iteratable \n"
    "\n"
    "Attributes:\n"
    "   comment_character (str): Designated character for commented lines (Default: '#') \n"
    "   field_delimiter (str): Designated character for delimiting fields (Default: whitespace) \n"
    "   null_value (str): Value indicating null value \n"
    "   coordinates (<domain>Point): Long-lat point for the given domain \n"
    "   input (str): File to read \n"
    "   object_id_column (str): The column that will be used for object IDs \n"
    "   timestamp_column (str): The column that will be used for timestamps \n"
    "   timestamp_format (str): The format of the timestamp \n"
    "Cartesian2D specific attributes: \n"
    "       * x_column (int): The column that will be the X coordinate \n"
    "       * y_column (int): The column that will be the Y coordinate \n"
    "Cartesian3D specific attributes: \n"
    "       * x_column (int): The column that will be the X coordinate \n"
    "       * y_column (int): The column that will be the Y coordinate \n"
    "       * z_column (int): The column that will be the Z coordinate \n"
    "Terrestrial specific attributes: \n"
    "       * longitude_column (int): The column that will be the longitude coordinate \n"
    "       * latitude_column (int): The column that will be the latitude coordinate \n"
    "\n"
    "Methods: \n"
    "   has_coordinate_column (int coordinate): Returns bool indicating if the coordinate has a corrdinate column\n"
    "   clear_coordinate_assignments (): Clears all of the corrdinate assignments\n"
    "   set_real_field_column (string field, int column): Set the field column value of the point\n"
    "   real_field_column (str field): Retrieve the column assignment for a real-valued field\n"
    "   set_string_field_column (str field, int column): Set the string column value of the point\n"
    "   string_field_column (str field): Retrieve the column assignment for a string field\n"
    "   set_time_field_column (str field, int column): Set the time column value of the point\n"
    "   time_field_column (str field): Retrieve the column assignment for a time field\n"
    ;

}}}


