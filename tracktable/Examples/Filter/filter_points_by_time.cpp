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

#include <tracktable/RW/PointReader.h>
#include <tracktable/RW/PointWriter.h>
#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Domain/Terrestrial.h>
#include <boost/iterator/filter_iterator.hpp>

#include <list>

typedef tracktable::domain::terrestrial::trajectory_type trajectory_type;
typedef tracktable::PointReader<trajectory_type::point_type> point_reader_type;
typedef tracktable::PointWriter point_writer_type;
typedef point_reader_type::iterator point_reader_iter;

// Given two timestamps A and B, check a point P to see whether A <=
// P.timestamp <= B.

template<typename pointT>
struct date_between {
  date_between(
    tracktable::Timestamp const& startTime,
    tracktable::Timestamp const& endTime
    )
    : StartTime(startTime)
    , EndTime(endTime)
  { }

  bool operator()(pointT const& point) //const& not copied (reference), not alterable
  {
    return (point.timestamp() >= this->StartTime && point.timestamp() <= this->EndTime);
  }

  tracktable::Timestamp StartTime;
  tracktable::Timestamp EndTime;
};

// ----------------------------------------------------------------------

int main(int argc, char* argv[])
{
  if(argc !=5)
    {
    std::cout << "Usage: " << argv[0] << " input_filename output_filename start_date_time_inclusive end_date_time_inclusive" << std::endl;
    std::cout << "Example: "
              << argv[0] << " in.csv out.csv \"2015-07-09 00:00:00\" \"2015-07-09 23:59:59\"" << std::endl;
    exit(-1);
    }

  point_reader_type point_reader;
  point_writer_type point_writer;

  std::ifstream infile;
  std::ofstream outfile;

  tracktable::Timestamp startTime = tracktable::time_from_string(argv[3]);
  tracktable::Timestamp endTime = tracktable::time_from_string(argv[4]);

  infile.open(argv[1]);
  if (!infile)
    {
    std::cerr << "ERROR: Cannot open file " << argv[1] << " for input.\n";
    exit(1);
    }
  point_reader.set_input(infile);

  outfile.open(argv[2]);
  if (!outfile)
    {
    std::cerr << "ERROR: Cannot open file " << argv[2] << " for output.\n";
    exit(1);
    }
  point_writer.set_output(outfile);

  std::stringstream sstr;
  sstr << " Filtered from " << argv[1] << " to include only updates between "
       << argv[3] << " and " << argv[4] << "." << std::endl;
//  point_writer.add_header_comment(sstr.str());

  date_between<trajectory_type::point_type> MyDateFilter(startTime, endTime);

  std::list<trajectory_type::point_type> in_points(point_reader.begin(), point_reader.end());

  typedef boost::filter_iterator<
    date_between<trajectory_type::point_type>,
    point_reader_type::iterator
    > FilterIteratorT;

//  FilterIteratorT start(MyDateFilter, in_points.begin());
//  FilterIteratorT finish(MyDateFilter, in_points.end());
  FilterIteratorT start(MyDateFilter, point_reader.begin());
  FilterIteratorT finish(MyDateFilter, point_reader.end());

  point_writer.write(start, finish);

#if 0
  point_writer.write(boost::make_filter_iterator<date_between<point_type> >(MyDateFilter, point_reader.begin(),
                                                               point_reader.end()),
                     boost::make_filter_iterator<date_between<point_type> >(MyDateFilter, point_reader.end(),
                                                               point_reader.end())
    );
#else
  point_writer.write(point_reader.begin(), point_reader.end());
#endif

  return 0;

}
