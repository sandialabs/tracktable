/*
 * Copyright (c) 2014-2018 National Technology and Engineering
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

#include <tracktable/Core/PointBase.h>
#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointLonLat.h>

#include <boost/archive/text_iarchive.hpp>
#include <boost/archive/text_oarchive.hpp>

#include <iostream>
#include <sstream>


int
test_point_base_serialization()
{
  tracktable::PointBase<2> point, restored_point;
  point[0] = 1;
  point[1] = 2;

  std::ostringstream temp_out;
  boost::archive::text_oarchive archive_out(temp_out);
  archive_out << point;

  std::istringstream temp_in(temp_out.str());
  boost::archive::text_iarchive archive_in(temp_in);
  archive_in >> restored_point;

  if (point != restored_point)
    {
    std::cerr << "ERROR: Serialization/deserialization of "
              << "tracktable::PointBase failed.  Original "
              << "point was "
              << point
              << " and restored point was "
              << restored_point << ".\n";
    return 1;
    }
  else
    {
    return 0;
    }
  
}

int
main(int argc, char *argv[])
{
  int num_errors = 0;

  num_errors += test_point_base_serialization();

  return num_errors;
}
