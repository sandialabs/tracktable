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
#ifndef Portal_h
#define Portal_h

#include <tracktable/Domain/Terrestrial.h>

#include <boost/geometry/geometries/box.hpp>
#include <boost/geometry/geometries/register/box.hpp>

#include <list>
#include <memory>
#include <set>

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = typename TrajectoryT::point_type;
using BoxT = boost::geometry::model::box<PointT>;
using TrajectoryPtrT = std::shared_ptr<TrajectoryT>;

/**
 * @brief A portal is simply a box defined by two points
 * A portal has a set of trajectories that intersect it and the potentail to have a set of 'children' which
 * are fully contained subdivisions
 */
class Portal : public BoxT {
   public:
    Portal() = delete;
    Portal(const BoxT &b) : BoxT(b){};

    /// Sort Portals basic on how many trajectories they contain
    bool operator<(const Portal &p) const { return (trajectories.size() < p.trajectories.size()); }
    /** @brief Divides portal into x*y children portals and assign trajectories accordingly
     * @param _xDivision number of divisions in the x(longitude) direction
     * @param _yDivisions number of divisions in the y(latitude) direction */
    void divide(size_t _xDivision, size_t _yDivisions);
    /** @brief Adds a list of trajectories to the portal
     * @param _addList */
    void add_trajectories(std::vector<TrajectoryPtrT> &_addList);
    /** @brief Will assign the trajectory to this portal (does not check intersection) then adds the
     * trajectory to all children (based on intersection)
     * @note if the trajectory does not intersect the top level, it will still be added while not existing
     * in any of the children (impact unknown)
     * @param _t The trajectory to add */
    void add_trajectory(const TrajectoryPtrT &_t);
    /** @brief Removes a list of trajectories from the portal
     * @param _removeList */
    void remove_trajectories(const std::vector<TrajectoryPtrT> &_removeList);
    /** @brief Removes a specific trajectory from portal and all children
     * @param _t trajectory to remove */
    void remove_trajectory(const TrajectoryPtrT &_t);

   public:
    size_t level;                                  ///< The level this portal is at
    std::set<TrajectoryPtrT> trajectories;         ///< Trajectories that intersect this portal
    std::list<std::shared_ptr<Portal> > children;  ///< Children portals (if any)
};

/// How we pass portal references around
using PortalPtrT = std::shared_ptr<Portal>;
/// Overide default sorting for PortalPtrT
bool operator<(const PortalPtrT &p1, const PortalPtrT &p2);

BOOST_GEOMETRY_REGISTER_BOX(Portal, PointT, min_corner(), max_corner());

#endif  // portal_h