##########################################################################
# THIS IS PROBABLY THE ONLY SECTION WHERE THINGS CHANGE
##########################################################################
# Begin project variables
#-------------------------------------------------------------------------

# Give your project a cool name because this will also be used for the executable name
set(PROJECT_NAME coolprogram)

# Start this at 0.0.1 for a new project
set(PROJECT_VERSION 0.0.1)

# These are your .cpp files for the executable
set(PROGRAM_SOURCES
        cool_main.cpp
	)

# This allows for an alternate compiler
set(CMAKE_CXX_COMPILER gcc)

# Do you have extra random linker flags? Put them here.
add_link_options()

# The same with any extra compiler flags
add_compile_options(-Wall -Wno-unknown-pragmas -O2 -DBOOST_ALL_DYN_LINK)

# This is where pkgconfig automagically adds your project dependencies,
# and dependencies of dependencies, and dependencies of dependencies of
# dependencies including all their cflags and ldflags and other flags.
#
# TLDR: Magic happens
set(PKGCONFIG_TRACKTABLE tracktable-1.2)

# Example below with OpenGL, Glib, Sqlite3 and GNU Scientific Library added
# Look in /usr/lib64/pkgconfig for more development packages with pkgconfig support
#set(PKGCHECK_EXTRA_MODULES gl glib sqlite3 gsl)

set(BOOST_COMPONENTS_NEEDED program_options date_time timer regex log)

#-------------------------------------------------------------------------
# End project variables
##########################################################################

# Housekeeping
cmake_minimum_required(VERSION 3.12)
include(GNUInstallDirs)

# Declare the project, languages and version
project(${PROJECT_NAME} LANGUAGES C CXX VERSION ${PROJECT_VERSION})

# pkgconfig stuff
find_package(PkgConfig REQUIRED)
pkg_check_modules(PKGCONFIG REQUIRED ${PKGCONFIG_TRACKTABLE} ${PKGCHECK_EXTRA_MODULES})

# This makes sure we're looking at the same boost that tracktable was built with
pkg_get_variable(BOOST_LIBRARYDIR ${PKGCONFIG_TRACKTABLE} boost_library_dir )
pkg_get_variable(BOOST_INCLUDEDIR ${PKGCONFIG_TRACKTABLE} boost_include_dir )
pkg_get_variable(CMAKE_CXX_STANDARD ${PKGCONFIG_TRACKTABLE} cxx_standard )
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Boost CONFIG REQUIRED COMPONENTS ${BOOST_COMPONENTS_NEEDED} )

# Declare the executable, its sources and compiling/linking flags
# If you want more than one executable in the project you should be able to just copy/paste the
# add_executable(), target_link_libraries(), target_include_directories() and target_compile_options()
# lines. Then replace ${PROJECT_NAME} with your second executable's name.
add_executable(${PROJECT_NAME} ${PROGRAM_SOURCES})
target_link_libraries(${PROJECT_NAME} PUBLIC ${PKGCONFIG_LDFLAGS} ${PKGCONFIG_LDFLAGS_OTHER} ${Boost_LIBRARIES} -lstdc++)
target_include_directories(${PROJECT_NAME} PUBLIC ${PKGCONFIG_INCLUDE_DIRS} ${Boost_INCLUDE_DIRS})
target_compile_options(${PROJECT_NAME} PUBLIC ${PKGCONFIG_CFLAGS_OTHER})

