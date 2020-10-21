# Copyright (c) 2014-2020 National Technology and Engineering Solutions of
# Sandia, LLC. Under the terms of Contract DE-NA0003525 with National Technology
# and Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
# rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# 1. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# CMAKE BUG: #231
unset(Boost_FOUND)
find_package(
  Boost ${BOOST_MINIMUM_VERSION_REQUIRED} REQUIRED
  COMPONENTS ${BOOST_CORE_COMPONENTS_NEEDED} ${BOOST_EXAMPLE_COMPONENTS})

include_directories(${Tracktable_SOURCE_DIR} ${Tracktable_BINARY_DIR} BEFORE)

include_directories(${Boost_INCLUDE_DIR} AFTER)

link_directories(${Boost_LIBRARY_DIRS})

# Factories
add_executable(
  FactoryTest FactoryTestMain.cpp AssemblerFromCommandLine_TEST.cpp CombinedCommandLine_TEST.cpp
              PointReaderFromCommandLine_TEST.cpp)
target_link_libraries(FactoryTest ${Boost_LIBRARIES} TracktableCore TracktableDomain)
add_test(
  NAME C_FactoryTest
  COMMAND FactoryTest
  WORKING_DIRECTORY ${PROJECT_BINARY_DIR})

