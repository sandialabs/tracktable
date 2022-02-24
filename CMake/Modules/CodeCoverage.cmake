include(CMakeParseArguments)

# Sets up build targets for code coverage
#
# Arguments
#   EXCLUDES - List of additional expressions to exclude from code coverage. See lcov documentation for syntax
#
# Usage:
#       cmake -DCMAKE_CXX_COMPILER=g++ -DCMAKE_C_COMPILER=gcc -DCMAKE_BUILD_TYPE=Coverage ..
#       make -j
#
#       # Code coverage for just unit tests
#       make cov_unit
#
#       It is also possible to manually run commands, then check the coverage
#       make cov_init
#       # Run your tests manually here
#       make cov_capture
#
#       # To generate an html report (after running your tests)
#       make cov_genhtml
#
function(SETUP_CODE_COVERAGE)
    set(multiValueArgs EXCLUDES)

    cmake_parse_arguments(CODE_COVERAGE "" "" "${multiValueArgs}" ${ARGN})

    # Set up build targets for code coverage
    if(${CMAKE_CXX_COMPILER_ID} STREQUAL "GNU")
        set(SHARED_OPTIONS "-g -O0 -fprofile-arcs -ftest-coverage -fno-inline")
        set(SHARED_OPTIONS "${SHARED_OPTIONS} -fno-elide-constructors") # Stops compiler from optimizing out temporary objects that confuse gcov

        set(CMAKE_CXX_FLAGS_COVERAGE ${SHARED_OPTIONS} CACHE STRING
            "Flags used for C++ compiler for coverage" FORCE)
        set(CMAKE_C_FLAGS_COVERAGE ${SHARED_OPTIONS} CACHE STRING
            "Flags used for C compiler for coverage" FORCE)
        set(CMAKE_EXE_LINKER_FLAGS_COVERAGE "-fprofile-arcs -ftest-coverage" CACHE STRING
            "Flags used for linking binaries during coverage builds" FORCE)
        set(CMAKE_SHARED_LINKER_FLAGS_COVERAGE "" CACHE STRING
            "Flags used for linking shared libraries during coverage builds" FORCE)
        mark_as_advanced(
            CMAKE_CXX_FLAGS_COVERAGE
            CMAKE_C_FLAGS_COVERAGE
            CMAKE_EXE_LINKER_FLAGS_COVERAGE
            CMAKE_SHARED_LINKER_FLAGS_COVERAGE)

        find_program(LCOV_PATH lcov)
        find_program(GCOV_PATH gcov)
        find_program(GENHTML_PATH genhtml)

        if(LCOV_PATH AND GCOV_PATH)
            set(LCOV_BRANCH_COVERAGE ${LCOV_PATH} --rc lcov_branch_coverage=1)

            add_custom_target(cov_init
                COMMAND ${LCOV_BRANCH_COVERAGE} --capture --initial --directory ${CMAKE_SOURCE_DIR} --output-file coverage_base.info --no-external
            )

            add_custom_target(cov_unit
                COMMAND ${CMAKE_BUILD_TOOL} cov_init
                COMMAND ${CMAKE_BUILD_TOOL} test # Might be a better way to make sure things get built and run
                COMMAND ${CMAKE_BUILD_TOOL} cov_capture
            )

            add_custom_target(cov_capture
                COMMAND ${LCOV_BRANCH_COVERAGE} --capture --directory ${CMAKE_SOURCE_DIR} --output-file coverage_test.info --no-external
                COMMAND ${LCOV_BRANCH_COVERAGE} --add-tracefile coverage_base.info --add-tracefile coverage_test.info --output coverage_total.info
                COMMAND ${LCOV_BRANCH_COVERAGE} --remove coverage_total.info
                    '/usr/*'                         # Exclude stuff from /usr/
                    ${CODE_COVERAGE_EXCLUDES}
                    --output-file coverage_filtered.info
                COMMAND ${LCOV_BRANCH_COVERAGE} --list coverage_test.info --no-external
            )

            if (GENHTML_PATH)
                # Generate local html code coverage report
                add_custom_target(cov_genhtml
                    COMMAND ${GENHTML_PATH} --quiet coverage_filtered.info -output-directory coverage
                    COMMENT "Code coverage report saved to ${CMAKE_BINARY_DIR}/coverage/index.html"
                )
            else()
                message(WARNING "***** WARNING: genhtml was not found! *****")
            endif()

        else()
            message(WARNING "***** WARNING: lcov or gcov was not found! *****")
        endif()
    endif()
endfunction(SETUP_CODE_COVERAGE)
