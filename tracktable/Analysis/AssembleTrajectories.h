/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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


#ifndef __tracktable_AssembleTrajectories_h
#define __tracktable_AssembleTrajectories_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Analysis/detail/AssembleTrajectoriesIterator.h>

namespace tracktable {

/** Assemble time-sorted points into trajectories
 *
 * We often receive input data as sequences of points sorted by
 * timestamp.  In order to manipulate these data sets as trajectories
 * instead of as isolated points we must perform some sort of
 * connect-the-dots operation to group them together.  This class
 * implements that operation.
 *
 * Suppose for the sake of argument that our input is sorted first by
 * object ID and second by increasing timestamp.  Now consider the
 * block of points corresponding to a single object ID.  We divide
 * that into one or more trajectories as follows:
 *
 * - If too much time (as specified by the separation_time parameter)
 *   has elapsed between one point and the next, one trajectory has
 *   ended and another begins.
 *
 * - If too much distance (as specifide by the separation_distance
 *   parameter) lies between one point and the next, one trajectory has
 *   ended and another begins.
 *
 * We implement AssembleTrajectories as an iterator.  It consumes an
 * input stream of points sorted by timestamp (*not* by object ID) and
 * produces complete trajectories.  Internally, it keeps track of all
 * the object IDs seen recently and applies the process above to
 * identify and emit complete trajectories.
 *
 * We can also set a third parameter (minimum_trajectory_length) that
 * silently rejects trajectories that do not contain enough points to
 * be interesting.
 */


template<typename TrajectoryT, typename PointIteratorT>
class AssembleTrajectories
{
public:
  typedef TrajectoryT trajectory_type;
  typedef typename trajectory_type::point_type point_type;
  typedef AssembleTrajectoriesIterator<point_type, PointIteratorT, trajectory_type> iterator;

  AssembleTrajectories()
    {
      this->set_default_configuration();
    }

  AssembleTrajectories(PointIteratorT rangeBegin, PointIteratorT rangeEnd)
    {
      this->set_default_configuration();
      this->set_input(rangeBegin, rangeEnd);
    }

  AssembleTrajectories(AssembleTrajectories const& other)
    {
      this->SeparationDistance = other.SeparationDistance;
      this->SeparationTime = other.SeparationTime;
      this->PointBegin = other.PointBegin;
      this->PointEnd = other.PointEnd;
    }

  AssembleTrajectories& operator=(AssembleTrajectories const& other)
    {
      this->SeparationDistance = other.SeparationDistance;
      this->SeparationTime = other.SeparationTime;
      this->PointBegin = other.PointBegin;
      this->PointEnd = other.PointEnd;
      return *this;
    }

  virtual ~AssembleTrajectories() { }

  bool operator==(AssembleTrajectories const& other) const
    {
      return (this->SeparationDistance == other.SeparationDistance &&
              this->SeparationTime == other.SeparationTime &&
              this->PointBegin == other.PointBegin &&
              this->PointEnd == other.PointEnd);
    }

  bool operator!=(AssembleTrajectories const& other) const
    {
      return ((*this == other) == false);
    }

  iterator begin()
    {
      return iterator(this->PointBegin, this->PointEnd,
                      boost::numeric_cast<int>(this->MinimumTrajectoryLength),
                      this->SeparationDistance,
                      this->SeparationTime,
                      this->CleanupInterval);
    }

  iterator end()
    {
      return iterator(this->PointEnd, this->PointEnd,
                      boost::numeric_cast<int>(this->MinimumTrajectoryLength),
                      this->SeparationDistance,
                      this->SeparationTime,
                      this->CleanupInterval);
    }

  void set_input(PointIteratorT const& forefront,
                 PointIteratorT const& rearguard)
    {
      this->PointBegin = forefront;
      this->PointEnd = rearguard;
    }

  void set_separation_time(Duration const& d)
    {
      this->SeparationTime = d;
    }

  void set_separation_distance(double d)
    {
      this->SeparationDistance = d;
    }

  void set_minimum_trajectory_length(std::size_t len)
    {
      this->MinimumTrajectoryLength = len;
    }

  void set_cleanup_interval(int points_between_cleanup)
    {
      this->CleanupInterval = points_between_cleanup;
    }

  Duration separation_time() const
    {
      return this->SeparationTime;
    }

  double separation_distance() const
    {
      return this->SeparationDistance;
    }

  std::size_t minimum_trajectory_length() const
    {
      return this->MinimumTrajectoryLength;
    }

protected:
  virtual void set_default_configuration()
    {
      this->SeparationDistance = 100;
      this->SeparationTime = Duration(minutes(30));
      this->MinimumTrajectoryLength = 2;
      this->CleanupInterval = 10000;
    }

private:
  PointIteratorT PointBegin;
  PointIteratorT PointEnd;
  Duration SeparationTime;
  double SeparationDistance;
  std::size_t MinimumTrajectoryLength;
  int CleanupInterval;
};

} // close namespace tracktable

#endif
