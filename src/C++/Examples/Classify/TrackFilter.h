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

#ifndef TrackFilter_h
#define TrackFilter_h

#include <tracktable/Domain/Terrestrial.h>

#include <boost/program_options.hpp>

#include <limits>

using TrajectoryT = tracktable::domain::terrestrial::trajectory_type;
using PointT = typename TrajectoryT::point_type;
// TODO: Template these

/** @brief Utility interface that provides framework for filtering tracks
 * In it's simplest form the only advantage it provides is each of maintenance
 * of the erase loops.
 *
 * The real advantage comes when the command line automation is added in
 * the MinMaxTrackFilter implementation
 * @sa MinMaxTrackFilter
 */
class TrackFilter {
   public:
    TrackFilter(const std::string& _name) : name(_name) {}
    void operator()(std::vector<TrajectoryT>& _tracks) { filterTracks(_tracks); }

    void filterTracks(std::vector<TrajectoryT>& _tracks) {
        // use lambda to wrap non-static function
        _tracks.erase(std::remove_if(_tracks.begin(), _tracks.end(),
                                     [&](const TrajectoryT& _t) { return this->shouldNotKeepTrack(_t); }),
                      _tracks.end());
    }
    void inverseFilterTracks(std::vector<TrajectoryT>& _tracks) {
        _tracks.erase(std::remove_if(_tracks.begin(), _tracks.end(),
                                     [&](const TrajectoryT& _t) { return this->shouldKeepTrack(_t); }),
                      _tracks.end());
    }

    const std::string& getName() const { return name; }

   protected:
    /** This is filter criteria */
    virtual bool shouldKeepTrack(const TrajectoryT& _t) = 0;
    bool shouldNotKeepTrack(const TrajectoryT& _t) { return !shouldKeepTrack(_t); }


   protected:
    std::string name;
};

namespace bpo = boost::program_options;

/** @brief Provides a basic min max filter and facilitates command line options to set the parameters
 *
 * The following filters on length, adding command line options "--min-length" & "--max-length"
 * @code
 * boost::program_options::options_description commandLineOptions;
 * MinMaxTrackFilter<double> lengthFilter("length",tracktable::length<TrajectoryT>);
 * lengthFilter.addOptions(commandLineOptions;)
 * //parse and notify
 * lengthFilter(trajectories);
 * @endcode
 *
 * @tparam MeasurementT The type of value we are expecting from the measurement function
 */
template <typename MeasurementT>
class MinMaxTrackFilter : public TrackFilter {
   protected:
    using ThisType = MinMaxTrackFilter<MeasurementT>;
    using BaseType = TrackFilter;

   public:
    /**
     * @brief Construct a new Min Max Track Filter object
     *
     * @param _name Used to create command line arguments for min/max
     * @param _measureFunc Function that returns a value to be compared against min/max
     *
     * @note Can us inverseFilterTracks to exclude the range
     */
    MinMaxTrackFilter(const std::string& _name, MeasurementT (*_measureFunc)(const TrajectoryT&))
        : BaseType(_name), measureFunc(_measureFunc) {}
    bool shouldKeepTrack(const TrajectoryT& _t) {
        auto r = measureFunc(_t);
        return max >= r && r >= min;
    }
    void addOptions(bpo::options_description& _desc) {
        auto minString = "min-" + name;
        auto maxString = "max-" + name;
        bpo::options_description filterOptions(name);
        // clang-format off
        filterOptions.add_options()
            (minString.c_str(), bpo::value<MeasurementT>(&min),
             ("minimum value for " + name).c_str())
            (maxString.c_str(), bpo::value<MeasurementT>(&max),
             ("maximum value for " + name).c_str())
        ;
        // clang-format on
        _desc.add(filterOptions);
    }

    MeasurementT getMin() const { return min; }
    void setMin(MeasurementT _v) { min = _v; }
    MeasurementT getMax() const { return max; }
    void setMax(MeasurementT _v) { max = _v; }

   private:
    MeasurementT min = std::numeric_limits<MeasurementT>::min();
    MeasurementT max = std::numeric_limits<MeasurementT>::max();
    MeasurementT (*measureFunc)(const TrajectoryT&) = nullptr;
};

#endif  // TrackFilter_h