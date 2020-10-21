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


#ifndef __tracktable_AssembleTrajectories_h
#define __tracktable_AssembleTrajectories_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Analysis/detail/AssembleTrajectoriesIterator.h>

namespace tracktable {

/** Assemble time-sorted points into trajectories
 *
 * We often receive input data as sequences of points sorted by
 * timestamp. In order to manipulate these data sets as trajectories
 * instead of as isolated points we must perform some sort of
 * connect-the-dots operation to group them together. This class
 * implements that operation.
 *
 * Suppose for the sake of argument that our input is sorted first by
 * object ID and second by increasing timestamp. Now consider the
 * block of points corresponding to a single object ID. We divide
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
 * We implement AssembleTrajectories as an iterator. It consumes an
 * input stream of points sorted by timestamp (*not* by object ID) and
 * produces complete trajectories. Internally, it keeps track of all
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

  /** Instantiate AssembleTrajectories using the default assembly configuration.
   *
   * @copydoc AssembleTrajectories::set_default_configuration()
   */
  AssembleTrajectories()
    {
      this->set_default_configuration();
    }

 /** Instantiate AssembleTrajectories from a range of elements and default configuration.
   *
   * If you have a container of points you can use this constructor to
   * create and populate the tree in one swell foop instead of adding
   * elements one at a time.
   *
   * @copydoc AssembleTrajectories::set_default_configuration()
   *
   * @param [in] range_begin  Iterator pointing to beginning of input points
   * @param [in] range_end    Iterator pointing past end of input points
   */
  AssembleTrajectories(PointIteratorT rangeBegin, PointIteratorT rangeEnd)
    {
      this->set_default_configuration();
      this->set_input(rangeBegin, rangeEnd);
    }

 /** Copy Constructor, create AssembleTrajectories with trajectory data from another trajectory.
   *
   * @param [in] other  AssembleTrajectories instance
   */
  AssembleTrajectories(AssembleTrajectories const& other)
    {
      this->SeparationDistance = other.SeparationDistance;
      this->SeparationTime = other.SeparationTime;
      this->PointBegin = other.PointBegin;
      this->PointEnd = other.PointEnd;
    }

  /// Destructor
  virtual ~AssembleTrajectories() { }

  /** Assign a AssembleTrajectories to the value of another.
   *
   * @param [in] other AssembleTrajectories to assign value of
   * @return AssembleTrajectories with the new assigned value
   */
  AssembleTrajectories& operator=(AssembleTrajectories const& other)
    {
      this->SeparationDistance = other.SeparationDistance;
      this->SeparationTime = other.SeparationTime;
      this->PointBegin = other.PointBegin;
      this->PointEnd = other.PointEnd;
      return *this;
    }

  /** Check whether one AssembleTrajectories is equal to another by comparing the properties.
   *
   * Two items are equal if all of their properties are equal.
   *
   * @param [in] other AssembleTrajectories for comparison
   * @return Boolean indicating equivalency
   */
  bool operator==(AssembleTrajectories const& other) const
    {
      return (this->SeparationDistance == other.SeparationDistance &&
              this->SeparationTime == other.SeparationTime &&
              this->PointBegin == other.PointBegin &&
              this->PointEnd == other.PointEnd);
    }

  /** Check whether two AssembleTrajectories are unequal.
   *
   * @param [in] other AssembleTrajectories for comparison
   * @return Boolean indicating equivalency
   */
  bool operator!=(AssembleTrajectories const& other) const
    {
      return ((*this == other) == false);
    }

  /** Return an iterator to the first parsed point.
   *
   * @note that any changes you make to the parser configuration will
   * invalidate existing iterators.
   *
   * @return Iterator to first parsed point
   */
  iterator begin()
    {
      return iterator(this->PointBegin, this->PointEnd,
                      boost::numeric_cast<int>(this->MinimumTrajectoryLength),
                      this->SeparationDistance,
                      this->SeparationTime,
                      this->CleanupInterval);
    }

 /** Return an iterator to detect when parsing has ended.
   *
   * This iterator is guaranteed to not point at any valid
   * TrajectoryPoint. The only time when `begin() == end()` will be
   * when all points have been parsed from the input stream.
   *
   * @return Iterator past end of point sequence
   */
  iterator end()
    {
      return iterator(this->PointEnd, this->PointEnd,
                      boost::numeric_cast<int>(this->MinimumTrajectoryLength),
                      this->SeparationDistance,
                      this->SeparationTime,
                      this->CleanupInterval);
    }

  /** Set the start and end points of the trajectory
   *
   * @param [in] forefront Start point
   * @param [in] rearguard End point
   */
  void set_input(PointIteratorT const& forefront,
                 PointIteratorT const& rearguard)
    {
      this->PointBegin = forefront;
      this->PointEnd = rearguard;
    }

  /** Set the time between each point in the trajectory
   *
   * @param [in] d Time duration between each point in the trajectory
   */
  void set_separation_time(Duration const& d)
    {
      this->SeparationTime = d;
    }

  /** Set the distance between each point in the trajectory
   *
   * @param [in] d Distance between each point in the trajectory
   */
  void set_separation_distance(double d)
    {
      this->SeparationDistance = d;
    }

  /** Set the minimum length a trajectory can be
   *
   * @param [in] len Length of the trajectory
   */
  void set_minimum_trajectory_length(std::size_t len)
    {
      this->MinimumTrajectoryLength = len;
    }

  /** Set the interval that the trajectory points will be cleaned up
   *
   * @param [in] points_between_cleanup Number of points to clean up
   */
  void set_cleanup_interval(int points_between_cleanup)
    {
      this->CleanupInterval = points_between_cleanup;
    }

  /**
   * @return The separation time of the trajectory points
   */
  Duration separation_time() const
    {
      return this->SeparationTime;
    }

  /**
   * @return The separation distance of the trajectory points
   */
  double separation_distance() const
    {
      return this->SeparationDistance;
    }

  /**
   * @return The minimum length a trajectory can be
   */
  std::size_t minimum_trajectory_length() const
    {
      return this->MinimumTrajectoryLength;
    }

  int cleanup_interval() const
    {
      return this->CleanupInterval;
    }

protected:
  /** Set the default values for a trajectory
   *
   *
   * Default configuration is:
   *    - SeparationDistance = 100
   *    - SeparationTime = Duration(minutes(30))
   *    - MinimumTrajectoryLength = 2
   *    - CleanupInterval = 10000
   */
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
