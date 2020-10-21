#ifndef AssemblerFromComandLine_h
#define AssemblerFromComandLine_h
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
#include "CommandLineFactory.h"

#include <tracktable/Analysis/AssembleTrajectories.h>
#include <tracktable/Core/Timestamp.h>
#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/IO/PointReader.h>

namespace tracktable {

template <typename TrajectoryT>
class AssemblerFromCommandLine : public CommandLineFactory {
  using PointT = typename TrajectoryT::point_type;
  using PointReaderT = tracktable::PointReader<PointT>;
  using PointReaderIteratorT = typename PointReaderT::iterator;
  using AssemblerT = tracktable::AssembleTrajectories<TrajectoryT, PointReaderIteratorT>;

 protected:
  using ThisType = AssemblerFromCommandLine<TrajectoryT>;
  using BaseType = CommandLineFactory;

  struct AssemblerSettings : public CommandLineSettings {
    double SeparationDistance;
    std::size_t SeparationSeconds;
    std::size_t MinimumNumPoints;
    std::size_t CleanupInterval;
  };

 private:
  void initializeSettings() override {}
  void processVariables() override {}

 public:
  using BaseType::addOptions;
  void addOptions(bpo::options_description& _options) override {
    auto settings = std::static_pointer_cast<AssemblerSettings>(settingsPtr);
    // clang-format off
    bpo::options_description assemblerOptions("Assembler");
    assemblerOptions.add_options()
    ("separation-distance",
      bpo::value<double>(&settings->SeparationDistance)->default_value(100),
     "Set maximum separation distance for trajectory points")
    ("separation-seconds",
      bpo::value<std::size_t>(&settings->SeparationSeconds)->default_value(1200),
     "Set maximum separation time (in seconds) for trajectory points")
    ("min-points",
      bpo::value<std::size_t>(&settings->MinimumNumPoints)->default_value(10),
     "Trajectories shorter than this will be discarded")
    ("clean-up-interval",
      bpo::value<std::size_t>(&settings->CleanupInterval)->default_value(10000),
     "Number of points between cleanup")
    ;
    _options.add(assemblerOptions);
    // clang-format on
  }
  AssemblerFromCommandLine() : CommandLineFactory() {
    settingsPtr = std::make_shared<AssemblerSettings>();
    addOptions(commandLineOptions);
    positionalCommandLineOptions = nullptr;
  }

  std::shared_ptr<AssemblerT> createAssembler(std::shared_ptr<PointReaderT> _pointReader) {
    if (nullptr == parsedVariables) {
      throw std::runtime_error("Create Called With No Variable Map");
    }
    processVariables();
    auto settings = std::static_pointer_cast<AssemblerSettings>(settingsPtr);
    auto assembler = std::make_shared<AssemblerT>(_pointReader->begin(), _pointReader->end());
    assembler->set_separation_distance(settings->SeparationDistance);
    assembler->set_separation_time(tracktable::seconds(settings->SeparationSeconds));
    assembler->set_minimum_trajectory_length(settings->MinimumNumPoints);
    assembler->set_cleanup_interval(settings->CleanupInterval);
    return assembler;
  }
};

}  // namespace tracktable

#endif  // AssemblerFromComandLine_h