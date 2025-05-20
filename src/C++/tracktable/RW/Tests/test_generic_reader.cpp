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

#include <tracktable/RW/GenericReader.h>
#include <iostream>
#include <sstream>
#include <vector>


namespace {

std::size_t PointWithIdSerialNumber = 1 + (1 << 16) ;

}

// ----------------------------------------------------------------------

class PointWithId
{
public:
  PointWithId()
    : id(-100)
    { }

  PointWithId(int _id)
    : id(_id)
    { }

  PointWithId(PointWithId const& other)
    : id(other.id)
    { }

  virtual ~PointWithId()
    { }

  PointWithId& operator=(PointWithId const& other)
    {
      if (this != &other)
        {
        this->id = other.id;
        }
      return *this;
    }

  bool operator==(PointWithId const& other) const
    {
      return (this->id == other.id);
    }

  bool operator!=(PointWithId const& other) const
    {
      return !(*this == other);
    }

  static PointWithId* generate_new_point()
    {
      std::size_t new_id = ::PointWithIdSerialNumber++;
      std::cout << "generate_new_point: Creating point with ID " << new_id << "\n";
      return new PointWithId(static_cast<int>(new_id));
    }

  int get_id() const { return this->id; }

private:
  int id;
};

std::ostream&
operator<<(std::ostream& out, PointWithId const& p)
{
  std::ostringstream outbuf;
  outbuf << "<PointWithId "
         << p.get_id() << ">";
  out << outbuf.str();
  return out;
}

// ----------------------------------------------------------------------

template<class point_type>
class GenericGenerator : public tracktable::GenericReader<point_type>
{
public:
  GenericGenerator()
    : PointsRemaining(10)
    { }

  GenericGenerator(std::size_t points_remaining)
    : PointsRemaining(points_remaining)
    { }

  GenericGenerator(GenericGenerator const& other)
    : PointsRemaining(other.PointsRemaining)
    { }

protected:
  boost::shared_ptr<point_type> next_item()
    {
      boost::shared_ptr<point_type> result;
      if (this->PointsRemaining > 0)
        {
        result = boost::shared_ptr<point_type>(point_type::generate_new_point());
        -- this->PointsRemaining;
        }
      return result;
    }
private:
  std::size_t PointsRemaining;

};



int main(int /*argc*/, char* /*argv*/[])
{
  std::vector<PointWithId> point_vector;
  GenericGenerator<PointWithId> generator;

  point_vector.assign(generator.begin(), generator.end());
  std::cout << "Point vector contains "
            << point_vector.size() << " points.\n";

  for (std::vector<PointWithId>::iterator iter = point_vector.begin();
       iter != point_vector.end();
       ++iter)
    {
    std::cout << *iter << "\n";
    }

  return 0;
}
