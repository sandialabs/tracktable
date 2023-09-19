# Copyright (c) 2014-2023 National Technology and Engineering Solutions of
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


# So far this is a header-only library.  The lack of any library files being
# built is not an error.

include_directories(
  ${Tracktable_SOURCE_DIR}
  ${Boost_INCLUDE_DIR}
)

if (BUILD_TESTING)
  add_subdirectory(Tests)
endif (BUILD_TESTING)

set( DataGenerators_HEADERS
  PointGenerator.h
)

# This adds this folder to Visual Studio on Windows so that files
# are visible without creating a build command.
add_custom_target( TracktableDataGenerators
    SOURCES
    ${DataGenerators_HEADERS}
    )

# And this puts those files in their own folder in Visual Studio.
source_group( "Header Files"
    ${DataGenerators_HEADERS}
    )

# This adds the files in DataGenerators_HEADERS to the list of files
# that will be copied during 'make install'.
install(
  FILES ${DataGenerators_HEADERS}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${TRACKTABLE_INCLUDEDIR}/DataGenerators
)
