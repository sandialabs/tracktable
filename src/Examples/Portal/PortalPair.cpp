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
#include "PortalPair.h"

#include <tracktable/RW/KmlOut.h>

#include <boost/geometry/algorithms/intersects.hpp>

void PortalPair::update_value() {
    value = 0;
    contributors.clear();
    std::set_intersection(p1->trajectories.begin(), p1->trajectories.end(), p2->trajectories.begin(),
                          p2->trajectories.end(), std::back_inserter(contributors));

    contributors.erase(
        std::remove_if(contributors.begin(), contributors.end(),
                       [&](const TrajectoryPtrT _t) {
                           if (is_within_portal_ellipse(_t, 1.01)) {
                               ++value;  // cheating by incrementing value from within the lambda
                               return true;
                           }
                           return false;
                       }),
        contributors.end());
}

void PortalPair::update_seperation() { seperation = boost::geometry::distance(*p1, *p2); }

bool PortalPair::is_within_portal_ellipse(const TrajectoryPtrT &_trajectory, const double &_ecc) const {
    TrajectoryT::iterator first_pt, last_pt;
    get_segment(_trajectory, first_pt, last_pt);
    TrajectoryT segment(first_pt, last_pt);

    return (!segment.empty() &&
            (tracktable::length(segment) < _ecc * tracktable::distance(segment.front(), segment.back())));
}

void PortalPair::get_segment(const TrajectoryPtrT &trajectory, TrajectoryIterT &first_pt,
                             TrajectoryIterT &last_pt) const {
    // We know that the trajectory intersects both portals because it is in both portals list and they got
    // added to the list because they intersect
    unsigned int prev = 0;  // Has intersected neither
    TrajectoryIterT cur_box1, cur_box2;

    if (trajectory->size() < 2)
        std::cout << "Warning, trajectory->size() = " << trajectory->size() << std::endl;
    // If the path zigzags in and out of portals, it will remember the two innermost intersections
    for (auto pt = trajectory->begin(); (pt + 1) != trajectory->end(); ++pt) {
        auto segment = boost::geometry::model::segment<PointT>(*pt, *(pt + 1));
        if (boost::geometry::intersects(segment, *p1)) {
            cur_box1 = pt;           // if we were leaving, this was the last point inside the box
            if (prev == 2) {         // means we are entering instead of leaving
                ++cur_box1;          // enter means the other point was the last one inside the box
                last_pt = cur_box1;  // entering the box means the segment is ending here
                first_pt = cur_box2;
            }
            prev = 1;
        }
        if (boost::geometry::intersects(segment, *p2)) {
            cur_box2 = pt;
            if (prev == 1) {  // last intersection was with portal 1
                ++cur_box2;
                first_pt = cur_box1;
                last_pt = cur_box2;
            }
            prev = 2;
        }
    }
    if (0 == prev) {
        std::cout << "Something is very wrong!" << std::endl;
    }
}

bool PairHeap::refine_pairs() {
    if (empty()) return false;
    if (((top().p1->level >= depth) && (top().p2->level >= depth))) {
        if (top().seperation > this->minimumSeperation) {
            return false;
        }
        remove_top_pair();  // Consider removing a pair that is too close as a 'refinement'
    } else {
        refine_top_pair();
    }
    return true;
}

void PairHeap::refine_top_pair() {
    // Decompose the first portal by default (it's the largest), or
    // do the second if the first is already at desired depth
    auto shrink = top().p1;
    auto keep = top().p2;
    if (shrink->level >= depth) {
        assert(top().p2->level < depth);  // check done before call should not allow
        std::swap(shrink, keep);
    }
    pop();

    // If we haven't already created the children in the decomposition, do so
    /* TODO: Is it possible to have it already divided? if it is, should the pairing below be done? should we
     * have popped? */
    if (shrink->children.empty()) {
        shrink->divide(xDivisions, yDivisions);
    }

    // Now reassign the pairs, we do not enforce minimum seperation at this time
    for (auto first = shrink->children.begin(); first != shrink->children.end(); ++first) {
        PortalPair p(*first, keep);
        if (p.value >= minimumValue) {
            push(p);
        }
        for (auto second = std::next(first); second != shrink->children.end(); ++second) {
            PortalPair p2(*first, *second);
            if (p2.value >= minimumValue) {
                push(p2);
            }
        }
    }
}

void PairHeap::remove_top_pair() {
    // remove the contributors to the top pairs value
    topPortal->remove_trajectories(top().contributors);
    // remove the top
    pop();

    // Rescore and filter the heap NOTE: 'c' comes from the base class
    c.erase(std::remove_if(c.begin(), c.end(),
                           [&](PortalPair &_p) {
                               _p.update_value();
                               return _p.value < minimumValue;
                           }),
            c.end());
    // resort the heap and store it like 'priority_queue' prefers.
    std::make_heap(c.begin(), c.end());
}

void PairHeap::initialize(std::vector<TrajectoryPtrT> &_trajectories, PortalPtrT &_startingPortal) {
    topPortal = _startingPortal;
    // Initialize the simulation by making one big portal out of the _startingPortal
    // and then decomposing it.

    for (auto &t : _trajectories) {
        if (boost::geometry::intersects(*t, *topPortal)) {
            topPortal->add_trajectory(t);
        }
    }

    // Note: we are assuming _startingPortal is the USA and has an aspect ratio
    // of 12 by 5.  Using a different aliquot than that in the command below
    // will result in non-square portals.  Not that there is anything wrong
    // with that.

    topPortal->divide(12, 5);

    // Now initialize pair list with all of the children...
    // We do not enforce a separation at this time as it potentials blocks future children with a valid
    // separation
    for (auto first = topPortal->children.begin(); first != topPortal->children.end(); ++first) {
        for (auto second = std::next(first); second != topPortal->children.end(); ++second) {
            PortalPair p(*first, *second);
            if (p.value > minimumValue /* && p.seperation > minimumSeperation*/) {
                push(p);
            }
        }
    }
}

void writeKmlPortalPair(const PortalPair &pp, const std::string &file_name);

void PairHeap::find_portals() {
    static int i = 0;
    while (!empty()) {
        while (refine_pairs())
            ;
        if (!empty()) {
            std::stringstream filename;
            filename << "flights" << i << ".kml";
            writeKmlPortalPair(top(), filename.str());
            remove_top_pair();
            ++i;
        }
    }
}

using tracktable::kml;
void writeKmlPortalPair(const PortalPair &pp, const std::string &file_name) {
    std::ofstream out(file_name.c_str());
    out.precision(15);
    out << kml::header;
    kml::width(3);
    kml::write(out, pp.contributors);

    out << kml::style("Portal", "FF0000FF", 1.0);
    out << kml::startpm();
    out << kml::startmulti();
    out << kml::box(pp.p1->min_corner(), pp.p1->max_corner());
    out << kml::box(pp.p2->min_corner(), pp.p2->max_corner());
    out << kml::stopmulti();
    out << kml::stoppm();
    out << kml::footer;
}