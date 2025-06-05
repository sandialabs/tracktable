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

#ifndef PredictData_h
#define PredictData_h

#include <tracktable/Analysis/GuardedBoostGeometryRTreeHeader.h>
#include <tracktable/Domain/Terrestrial.h>

#include <boost/geometry/geometries/adapted/std_array.hpp>

#include <array>
#include <memory>

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
// TODO: Make TrajectoryT a template param

class PredictData {
   public:
    // Have to use boost array instead of standard because rtree can't handle std::array
    using FeatureT = std::array<double, 10>;
    FeatureT feature;
    size_t Id;
    std::shared_ptr<TrajectoryT> index;

    PredictData() = delete;
    PredictData(FeatureT const& _f, size_t id, std::shared_ptr<TrajectoryT> idx)
        : feature(_f), Id(id), index(idx) {}
    ~PredictData() = default;

    PredictData(PredictData const& _other) {
        feature = _other.feature;
        Id = _other.Id;
        index = _other.index;
    }

    PredictData& operator=(PredictData const& _other) {
        feature = _other.feature;
        Id = _other.Id;
        index = _other.index;
        return *this;
    }
};

BOOST_GEOMETRY_REGISTER_STD_ARRAY_CS(cs::cartesian)

namespace boost {
namespace geometry {
namespace index {

template <>
struct indexable<PredictData*> {
    using result_type = PredictData::FeatureT const&;  // required by boost
    result_type& operator()(PredictData* const& v) const { return v->feature; }
};

}  // namespace index
}  // namespace geometry
}  // namespace boost
using PredictRtreeT = boost::geometry::index::rtree<PredictData*, boost::geometry::index::quadratic<16>>;

#endif