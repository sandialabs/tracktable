NOTE: As of release 1.7.2, this document is inaccurate.  We're
currently using CTest, not PyTest.  We have plans to convert our
Python tests over to CTest and use an adapter to have CMake run
them.

Developer Testing Guide

This document serves as a guide to Tracktable developers for running tests, developing new tests, and maintaining legacy tests.

Legacy Tests

Tracktable tests have never been developed in a formal way.
However, there has been considerable effort made to ensure that features, as they are developed, are tested in at least an ad hoc fashion.
This has resulted in a variety of approaches that vary based on the individual developers own style.
The legacy tests may not be easily understandable to new developers that need to update tests or debug issues.
For this reason, new tests should be written using the formal frameworks defined in this document when updating tests or feature functionality.
Since the legacy tests are not created at the unit level but at a system level, it is not expected for the new tests do anything different at this time.
Tests are integrated into our cmake environment via the add_test method in the CMakeLists.txt files in each test directory.
This approach allows us to run tests individually and to capture individual results when run as a suite of tests in cmake/ctest.

New Tests

The Tracktable codebase is written in both Python and C++.
This requires seperate test frameworks for each language but the general approach to testing will be similar.
As part of implementing a new feature, the developer shall create a system level test that at least contain checks for common corner cases.
Ideally, feature requests are accompanied by Behavior Driven Design (BDD) (described below) style scenarios that will easily translate into test cases.
In order to integrate tests into our cmake environment without disturbing our legacy tests use the add_python_test and add_catch2_test methods, respectively, when developing new tests with the proper test frameworks.
These methods were created to allow for legacy test reporting functionality to remain unchanged while also creating new coverage and testing reports.
The formal test frameworks also allow for test discovery which we are not currently utlizing at the file system level so we can maintain more precise control of how our tests are run.
When the legacy tests have all been rewritten, this approach can be reassesed.

Python

Our test framework for our Python code is the pytest package.
The current implementation of our python tests based on pytest require the following packages.

coverage
pytest
pytest-cov
pytest-html
pytest-bdd

It would be silly to recreate a pytest tutorial within this document so it will only make note of relevant features and point the developer in the direction of more official documentation.

Resources
https://docs.pytest.org/en/6.2.x/getting-started.html
https://docs.pytest.org/en/6.2.x/fixture.html#fixtures
https://docs.pytest.org/en/6.2.x/parametrize.html#parametrize
https://github.com/pytest-dev/pytest-bdd
src/Python/tracktable/core/tests/test_distance.py
src/Python/tracktable/core/tests/test_compute_bounding_box.py
src//Python/tracktable/core/tests/test_convex_hull_area.py


Test Naming Conventions

PyTest test discovery looks for python files and methods named "test_*" or "*_test". While we are not currently using test discovery in a way that would utilize the file names, it is higly suggested that test files still begin with the "test_" prefix in order to support the functionality in the future.
It is required that the methods intended to be run as a test will start with the "test_" prefix.
Most legacy test already follow this naming convention.

Fixtures

Fixtures are the methods by which PyTest defines common setup and cleanup for tests.
The methods are defined using a Python decorator that is declared on the line before a method declaration.
It is highly reccomended that fixtures and classes be utilized when it makes sense to do so.
These features allows for concise test methods with a high degree of readability.

C++

Our test framework for our C++ code is Catch2 v2.
Our custom header for using Catch2 in our environment is tracktable/ThirdParty/TracktableCatch2.h
Including this header will give full access to the Catch2 macros that make up the test framework.

As with the python tests it would be redundant to recreate a tutorial here when there already exists a fantastic version on the official github page.
https://github.com/catchorg/Catch2/blob/devel/docs/tutorial.md
https://github.com/catchorg/Catch2/blob/devel/docs/tutorial.md#bdd-style
https://github.com/catchorg/Catch2/blob/devel/docs/test-cases-and-sections.md
tracktable\Core\Tests\test_distance.cpp
tracktable\Analysis\Tests\test_great_circle_fit.cpp

Why aren't we using v3?

Catch2 v3 is still under ative development and documentation is still incomplete.
When and if it becomes time to upgrade, tests written for v2 will still be compatible.

Test Naming Convention

In an attempt to maintain consistency between the C++ and Python portions of the code, Catch2 test names should follow the same conventions as outlined above.

Parameterized Tests

Given the highly paramterized nature of the Tracktable code, I want to point out the built-in templates that Catch2 has available for its tests.
TEMPLATE_TEST_CASE and TEMPLATE_TEST_CASE_METHOD are the macros that you will want to use when creating parameterized tests.
The latter is for use when using a fixture.
test_distance.cpp provides some examples of their use.

Behavior Driven Design (BDD)

The BDD style of test specification looks to leverage natural language for more easily understanding test structure and intent.
This style uses syntax like "In Scenario A, and Given X, When Y, Then Z".
The main difference between PyTest and Catch2, is that Catch2 makes extensive use of macros to enable this, where PyTest uses decorators.
In either case test structure will be very similar.
Where possible, when features are requested, it would be beneficial to the developer to gain as much understanding of the requirements of said feature in a BDD style specification.

Code Coverage

Coverage information is not generated by default.
The CMake option, COVERAGE_REPORT, should be enabled to generate an HTML coverage report for the Python code.
Currently it is not expected to reach full coverage but this is something that we will strive to address over time.
We also have made the decision not to capture coverage when testing in the MS Visual Studio environment.
Other platforms are generally compatible with gcov and Visual Studio is the exception that we would rather not make a special case for.

Test Output

Test result and coverage reports are stored in the ${Tracktable_BINARY_DIR}/TestOutput/ directory