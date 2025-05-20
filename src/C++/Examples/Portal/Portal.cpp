#include "Portal.h"

#include <boost/geometry/arithmetic/arithmetic.hpp>

void Portal::divide(size_t _xDivisions, size_t _yDivisions) {
    /** notes about boost geomtry arithmetic;
     * the first point is piecwise modified by the second point
     * to preserve the original point it is necessary to make copies first
     */
    auto delta = this->max_corner();
    boost::geometry::subtract_point(delta, this->min_corner());
    boost::geometry::divide_point(delta,PointT(_xDivisions,_yDivisions));

    for (auto i = 0u; i < _xDivisions; ++i) {
        for (auto j = 0u; j < _yDivisions; ++j) {
            auto ll = this->min_corner();
            auto d = delta;
            boost::geometry::multiply_point(d,PointT(i,j));
            boost::geometry::add_point(ll,d);

            auto ur = ll;
            boost::geometry::add_point(ur,delta);

            auto p = std::make_shared<Portal>(BoxT(ll, ur));
            p->level = this->level + 1;
            // Now, go through all of the trajectories associated with the parent portal
            // and assign them to the child by testing intersection.
            for (auto &t : this->trajectories) {
                if (boost::geometry::intersects(*t, *p)) {
                    p->trajectories.insert(t);
                }
            }
            // only keep the child if it's non empty
            if (!p->trajectories.empty()) {
                this->children.push_back(p);
            }
        }
    }
}

void Portal::add_trajectories(std::vector<TrajectoryPtrT> &_addList) {
    for (auto &t : _addList) {
        add_trajectory(t);
    }
}
void Portal::add_trajectory(const TrajectoryPtrT &_t) {
    trajectories.insert(_t);
    for (auto &c : children) {
        if (boost::geometry::intersects(*_t, *c)) {
            c->add_trajectory(_t);
        }
    }
}

void Portal::remove_trajectories(const std::vector<TrajectoryPtrT> &_removeList) {
    for (auto &t : _removeList) {
        remove_trajectory( t);
    }
}

void Portal::remove_trajectory(const TrajectoryPtrT &_t) {
    if (0 == trajectories.erase(_t)) {
        return; //if it doesn't intersect the parent, it doesn't intersect any of the children
    }
    for (auto &c : children) {
        c->remove_trajectory(_t);
    }
}

bool operator<(const PortalPtrT &p1, const PortalPtrT &p2) {
    return p1->trajectories.size() < p2->trajectories.size();
}
