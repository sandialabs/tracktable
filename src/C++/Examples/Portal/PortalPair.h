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
#ifndef PortalPair_h
#define PortalPair_h

#include "Portal.h"

#include <algorithm>
#include <queue>

using TrajectoryIterT = TrajectoryT::iterator;

/** Used to trak and rank pairs of portal
 * The value of a pair represents how many trajectories travel between the two
 * portals */
class PortalPair {
   public:
    PortalPair(const PortalPtrT &_p1, const PortalPtrT &_p2) {
        if (_p1->trajectories.size() > _p2->trajectories.size()) {
            p1 = _p1;
            p2 = _p2;
        } else {
            p1 = _p2;
            p2 = _p1;
        }
        update_value();
        update_seperation();
    }

    /// Sort based on custom value
    bool operator<(const PortalPair &_other) const {
        return (value * seperation) < (_other.value * _other.seperation);
    }

    /** compute the value of this pair of portals
     * The value is equal to the number of trajectories that seem to start in one portal and end
     * in the other */
    void update_value();
    /** @brief updates the seperation between the two portals
     * No real reason this should ever change with normal use */
    void update_seperation();
    /** @brief Determines the 'innermost' points of a trajectory that connect the two portals
     *
     * @param trajectory Trajectory in question
     * @param first_pt determined first point
     * @param last_pt determined second point
     */
    void get_segment(const TrajectoryPtrT &trajectory, TrajectoryIterT &first_pt, TrajectoryIterT &last_pt) const;
    /** @brief determines if the innermost segment of a trajectory between the two portals constitutes the
     * bulk of the trajectory, this is the criteria for a trajectory being 'from/to' the pair of portals
     *
     * @param _trajectory The trajectory being tested
     * @param _ecc The deviation allowed
     * @return true The trajectory is 'from/to' the portals
     * @return false otherwise
     */
    bool is_within_portal_ellipse(const TrajectoryPtrT &_trajectory, const double &_ecc) const;

   public:
    PortalPtrT p1;                             ///< First Portal
    PortalPtrT p2;                             ///< Second Portal
    size_t value;                              ///< value of portal pair
    double seperation;                         ///< distance between portals
    std::vector<TrajectoryPtrT> contributors;  ///< trajectories that contribute to the value of the pair
};

/** Management object for a set of PortalPairs
 * Based on priority queue which keeps elements sorted
 * allows for management and refinement of pairs and their respective portals
 * @note Highly coupled to PortalPair and Portal
 * @sa PortalPair Portal */
class PairHeap : public std::priority_queue<PortalPair> {
   public:
    /** @brief If possible, subdivides one of the portal in the top ranked pair
     * Returning false implies a 'best' result has bubbled to the top
     *
     * @return true If refinement was done
     * @return false If refinement was unecessary or impossible*/
    bool refine_pairs();
    /** @brief takes a 'refinable' pair and subdivides one them
     * The pair is then destroyed and a new set of pairs between the undivided portal and the newly created
     * children of the divided portal. */
    void refine_top_pair();
    /** @brief MegaPop() removes the top pair from the list and removes any trajectories connecting that pair
     * finally the rest of the heap is rescored*/
    void remove_top_pair();
    /** @brief Does initial intersection of _trajectories and _top
     * Does initial subdivision of _top and assigns trajectories accordingly
     * Creates an initial pair list based on populated divisions
     *
     * @param _trajectories trajectories of interest
     * @param _startingPortal A presumably empty top level portal
     */
    void initialize(std::vector<TrajectoryPtrT> &_trajectories, PortalPtrT &_startingPortal);
    /** @brief goes through the pair heap and corresponding Portal;
     * recursively peeling off the top pair and refining it down to the depth specified
     * in the heap.
     *
     * Every time the top pair has a level equal to the desired depth, it is recorded
     * in a kml file and the corresponding trajectories are removed from all portals
     * in the heirachy
     */
    void find_portals();

   public:
    double minimumSeperation = 10.0;  ///< Minimum Seperation for two portals to be considered a viable pair
    size_t minimumValue = 16u;        ///< Minimum value for a pair to be worth keeping
    size_t xDivisions = 2u;           ///< number of subdivisions to use in the x(longitude) direction
    size_t yDivisions = 2u;           ///< number of subdivisions to use in the y(latitude) direction
    size_t depth = 5u;                ///< maximum depth to subdivide to
    PortalPtrT topPortal;             ///< Pointer to top level portal
};

#endif