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

#ifndef __tracktable_AssembleTrajectoriesIterator_h
#define __tracktable_AssembleTrajectoriesIterator_h

#include <tracktable/Core/Timestamp.h>

#include <list>

#include <boost/unordered_map.hpp>

#include <string>
#include <vector>
#include <list>
#include <typeinfo>
#include <iterator>
#include <cassert>

namespace tracktable {

template<
  typename point_type,
  typename source_iterator_type,
  typename trajectory_type
  >
class AssembleTrajectoriesIterator
{
public:
  AssembleTrajectoriesIterator()
    {
      this->MinimumTrajectoryLength = 0;
      this->SeparationDistance = -1;
      this->SeparationTime = seconds(0);
      this->ValidTrajectoryCount = 0;
      this->InvalidTrajectoryCount = 0;
      this->PointCount = 0;
      this->CleanupInterval = 10000;
    }

  AssembleTrajectoriesIterator(source_iterator_type const& input_begin,
                               source_iterator_type const& input_end,
                               int minimum_length,
                               double separation_distance,
                               Duration const& separation_time,
                               int cleanup_interval)
    : InputBegin(input_begin),
      InputEnd(input_end),
      MinimumTrajectoryLength(minimum_length),
      SeparationDistance(separation_distance),
      SeparationTime(separation_time),
      CleanupInterval(cleanup_interval)
    {
      this->ValidTrajectoryCount = 0;
      this->InvalidTrajectoryCount = 0;
      this->PointCount = 0;

      if (input_begin != input_end)
        {
        this->find_next_complete_trajectory();
        }
    }

  AssembleTrajectoriesIterator(AssembleTrajectoriesIterator const& other)
    : InputBegin(other.InputBegin),
      InputEnd(other.InputEnd),
      MinimumTrajectoryLength(other.MinimumTrajectoryLength),
      SeparationDistance(other.SeparationDistance),
      SeparationTime(other.SeparationTime),
      TrajectoriesInProgress(other.TrajectoriesInProgress),
      ValidTrajectoryCount(other.ValidTrajectoryCount),
      InvalidTrajectoryCount(other.InvalidTrajectoryCount),
      PointCount(other.PointCount),
      CleanupInterval(other.CleanupInterval)
    { }

  ~AssembleTrajectoriesIterator() { }

  AssembleTrajectoriesIterator& operator=(AssembleTrajectoriesIterator const& other)
    {
      this->InputBegin = other.InputBegin;
      this->InputEnd = other.InputEnd;
      this->MinimumTrajectoryLength = other.MinimumTrajectoryLength;
      this->SeparationDistance = other.SeparationDistance;
      this->SeparationTime = other.SeparationTime;
      this->TrajectoriesInProgress = other.TrajectoriesInProgress;
      this->ValidTrajectoryCount = other.ValidTrajectoryCount;
      this->InvalidTrajectoryCount = other.InvalidTrajectoryCount;
      this->PointCount = other.PointCount;
      this->CleanupInterval = other.CleanupInterval;
    }

  // ----------------------------------------------------------------------

  bool operator==(AssembleTrajectoriesIterator const& other) const
    {
      // No, we're not going to compare the entire
      // trajectories-in-progress array.  Since the assembly algorithm
      // is deterministic, it is enough to check whether they are the
      // same size.
      return (
        this->InputBegin == other.InputBegin &&
        this->InputEnd == other.InputEnd &&
        this->MinimumTrajectoryLength == other.MinimumTrajectoryLength &&
        this->SeparationDistance == other.SeparationDistance &&
        this->SeparationTime == other.SeparationTime &&
        this->TrajectoriesInProgress.size() == other.TrajectoriesInProgress.size() &&
        this->FinishedTrajectories.size() == other.FinishedTrajectories.size() &&
        this->CleanupInterval == other.CleanupInterval
        );
    }


  // ----------------------------------------------------------------------

  bool operator!=(AssembleTrajectoriesIterator const& other) const
    {
      return ((*this == other) == false);
    }

  // ----------------------------------------------------------------------

  int valid_trajectory_count() const
    {
      return this->ValidTrajectoryCount;
    }

  // ----------------------------------------------------------------------

  int invalid_trajectory_count() const
    {
      return this->InvalidTrajectoryCount;
    }

  // ----------------------------------------------------------------------

  int point_count() const
    {
      return this->PointCount;
    }

  // ----------------------------------------------------------------------

  trajectory_type operator*()
    {
      assert(this->FinishedTrajectories.empty() == false);
      return this->FinishedTrajectories.front();
    }

  // ----------------------------------------------------------------------

  AssembleTrajectoriesIterator& operator++()
    {
      assert(this->FinishedTrajectories.empty() == false);

      this->FinishedTrajectories.pop_front();

      if (this->FinishedTrajectories.empty())
        {
        this->find_next_complete_trajectory();
        }

      return *this;
    }

  // ----------------------------------------------------------------------

  AssembleTrajectoriesIterator operator++(int)
    {
      AssembleTrajectoriesIterator current_state(*this);
      this->operator++();
      return current_state;
    }

private:
  typedef boost::unordered_map<std::string, trajectory_type> string_trajectory_map_type;
  typedef std::list<trajectory_type>     trajectory_list_type;

  source_iterator_type InputBegin;
  source_iterator_type InputEnd;

  std::size_t MinimumTrajectoryLength;
  double SeparationDistance;
  Duration SeparationTime;

  string_trajectory_map_type TrajectoriesInProgress;
  trajectory_list_type       FinishedTrajectories;

  int ValidTrajectoryCount;
  int InvalidTrajectoryCount;
  int PointCount;
  int CleanupInterval;

  // ----------------------------------------------------------------------

  void find_next_complete_trajectory()
    {
      point_type next_point;

      while (this->InputBegin != this->InputEnd)
        {
        ++ this->PointCount;

        next_point = *(this->InputBegin);
        typename string_trajectory_map_type::iterator find_iter = this->TrajectoriesInProgress.find(next_point.object_id());

        if (find_iter == this->TrajectoriesInProgress.end())
          {
          // We are not currently tracking a trajectory with this
          // object ID.  Start a new one.
          trajectory_type new_traj;
          new_traj.push_back(next_point);
          this->TrajectoriesInProgress[next_point.object_id()] = new_traj;
          }
        else
          {
          // We have a partial trajectory for this object ID.
          if (this->point_belongs_to_trajectory(find_iter, next_point))
            {
            (*find_iter).second.push_back(next_point);
            }
          else
            {
            // We're about to start a new trajectory.  Clear out the
            // old one and announce its readiness.
            if ((*find_iter).second.size() >= this->MinimumTrajectoryLength)
              {
              this->FinishedTrajectories.push_back((*find_iter).second);
              this->TrajectoriesInProgress.erase(find_iter);
              ++ this->ValidTrajectoryCount;
              }
            else
              {
              this->TrajectoriesInProgress.erase(find_iter);
              ++ this->InvalidTrajectoryCount;
              }

            // Start the new trajectory.
            trajectory_type new_traj;
            new_traj.push_back(next_point);
            this->TrajectoriesInProgress[next_point.object_id()] = new_traj;
            }
          }

        if (this->CleanupInterval > 0 && this->PointCount % this->CleanupInterval == 0)
          {
          this->cleanup_trajectories_in_progress(next_point.timestamp());
          }

        ++ this->InputBegin;
        if (this->FinishedTrajectories.empty() == false)
          {
          return;
          }
        }

      // Done iterating over all input points.
      if (this->InputBegin == this->InputEnd &&
          this->TrajectoriesInProgress.size() > 0)
        {
        this->cleanup_trajectories_in_progress(next_point.timestamp() + days(10000));
        }
    }


  // ----------------------------------------------------------------------

  void cleanup_trajectories_in_progress(Timestamp const& current_time)
    {
      typename string_trajectory_map_type::iterator traj_iter(this->TrajectoriesInProgress.begin());

      while (traj_iter != this->TrajectoriesInProgress.end())
        {
        Duration time_since_last_point = current_time - (*traj_iter).second.back().timestamp();
        if (time_since_last_point > this->SeparationTime)
          {
          // This trajectory is done and can either be published or
          // discarded.
          if ((*traj_iter).second.size() >= this->MinimumTrajectoryLength)
            {
            this->FinishedTrajectories.push_back((*traj_iter).second);
            ++this->ValidTrajectoryCount;
            }
          else
            {
            ++this->InvalidTrajectoryCount;
            }

          traj_iter = this->TrajectoriesInProgress.erase(traj_iter);
          }
        else
          {
          // This trajectory is still a going concern.  Move along.
          ++ traj_iter;
          }
        }
    }

  // ----------------------------------------------------------------------

  template<typename trajectory_iter_t>
  bool point_belongs_to_trajectory(trajectory_iter_t const& iter,
                                   point_type const& latest_point) const
    {
      if ((*iter).second.size() == 0)
        {
        return true;
        }
      else
        {
        bool within_separation_distance = (distance(latest_point, (*iter).second.back()) < this->SeparationDistance);
        bool within_separation_time = ((latest_point.timestamp() - (*iter).second.back().timestamp()) < this->SeparationTime);

        return (within_separation_distance && within_separation_time);
        }
    }

};

} // close namespace tracktable

#endif
