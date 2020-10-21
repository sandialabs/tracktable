#ifndef CommandLineFactory_h
#define CommandLineFactory_h
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
#include <tracktable/Core/TracktableCommon.h>

#include <boost/program_options.hpp>

#include <memory>

namespace tracktable {

struct CommandLineSettings {
  using string_type = tracktable::string_type;
  string_type InputFilename;
};

namespace bpo = boost::program_options;

class CommandLineFactory {
 public:
  CommandLineFactory() {
    commandLineOptions = std::make_shared<bpo::options_description>("Available Options");
    positionalCommandLineOptions = std::make_shared<bpo::positional_options_description>();
    commandLineOptions->add_options()("help", "Produce help message");
  }

  void parseCommandLine(int _argc, char* _argv[]) {
    if (nullptr == parsedVariables) {
      parsedVariables = std::make_shared<bpo::variables_map>();
    }
    initializeSettings();
    if (nullptr != positionalCommandLineOptions) {
      bpo::store(bpo::command_line_parser(_argc, _argv)
                     .options(*commandLineOptions)
                     .positional(*positionalCommandLineOptions)
                     .run(),
                 *parsedVariables);
    } else {
      bpo::store(bpo::command_line_parser(_argc, _argv).options(*commandLineOptions).run(), *parsedVariables);
    }
    bpo::notify(*parsedVariables);
    if (0 < parsedVariables->count("help")) {
      std::cerr << (*commandLineOptions) << std::endl;
    }
    processVariables();
  }

 private:
  virtual void initializeSettings() = 0;
  virtual void processVariables() = 0;

 public:
  void addOptions(std::shared_ptr<bpo::options_description>& _options) { addOptions(*_options); }
  virtual void addOptions(bpo::options_description& _options) = 0;

  std::shared_ptr<bpo::options_description> getCommandLineOptions() { return commandLineOptions; }
  void setCommandLineOptions(std::shared_ptr<bpo::options_description> _options) {
    commandLineOptions = _options;
  }

  std::shared_ptr<bpo::positional_options_description> getPositionalCommandLineOptions() {
    return positionalCommandLineOptions;
  }
  void setPositionalCommandLineOptions(std::shared_ptr<bpo::positional_options_description> _options) {
    positionalCommandLineOptions = _options;
  }

  std::shared_ptr<bpo::variables_map> getVariables() { return parsedVariables; }
  void setVariables(std::shared_ptr<bpo::variables_map> _variables) { parsedVariables = _variables; }

 protected:
  std::shared_ptr<bpo::options_description> commandLineOptions = nullptr;
  std::shared_ptr<bpo::positional_options_description> positionalCommandLineOptions = nullptr;
  std::shared_ptr<bpo::variables_map> parsedVariables = nullptr;
  std::shared_ptr<CommandLineSettings> settingsPtr = nullptr;
};

}//namespace tracktable
#endif  // CommandLineFactory_h
