/* Copyright (c) 2014-2023 National Technology and Engineering
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
#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Core/PointBase.h>
#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/ThirdParty/TracktableCatch2.h>

#include <cmath>
#include <memory>

// a user defined literal that is handy for readability in GENERATE
constexpr std::size_t operator"" _z(unsigned long long n) { return n; }

using namespace tracktable::arithmetic;

// clang-format off
#define POINTLIST                                        \
  tracktable::domain::cartesian3d::base_point_type,      \
  tracktable::domain::terrestrial::base_point_type,      \
  tracktable::domain::cartesian3d::trajectory_point_type,\
  tracktable::domain::terrestrial::trajectory_point_type
// clang-format on

// TEMPLATE_TEST_CASE allows us to run the same tests on different types.
// Note that POINTLIST is defined above ans is just a list of typenames
//  A good strategy with all things 'template' is to develop it with a specific
//  type and then switch to template after done. This will allow editors and
//  tools to work with better as the type won't be 'unknown'.
TEMPLATE_TEST_CASE("Degenerate", "[Degenerate][Point]", POINTLIST) {
  // TestType contains the current type from the list
  using PointT = TestType;
  GIVEN("A unit vector") {
    auto p = zero<PointT>();
    p[0] = 1.0;
    WHEN("You divide by a zero scalar") {
      auto result = divide_scalar(p, 0);
      THEN("All elements are not finite") {
        // You can use for loops and even functions in combination with most clauses
        for (auto u = 0u; u < PointT::size(); ++u) {
          CHECK(!std::isfinite(result[u]));
        }
      }
    }
    // The difference between GIVEN and AND_GIVEN is simply alignment in some reporters
    AND_GIVEN("A Zero Point") {
      auto z = zero<PointT>();
      WHEN("You divide by zero point") {
        auto result = divide(p, z);
        THEN("All elements are not finite") {
          for (auto u = 0u; u < PointT::size(); ++u) {
            CHECK(!std::isfinite(result[u]));
          }
        }
      }
    }
  }
  GIVEN("A Zero Point") {
    auto z = zero<PointT>();
    WHEN("You normalize") {
      auto result = normalize(z);
      THEN("result is not finite") {
        for (auto u = 0u; u < PointT::size(); ++u) {
          CHECK(!std::isfinite(result[u]));
        }
      }
    }
  }
}

// SCENARIO("Norms") {
TEMPLATE_TEST_CASE("Norms", "[Normal][Point]", POINTLIST) {
  // This effectively tests norm_square, and dot
  using PointT = TestType;
  auto u1 = GENERATE(range(0_z, PointT::size()));
  auto p = zero<PointT>();
  GIVEN("A point with element " << u1 << " being 1") {
    p[u1] = 1.0;
    WHEN("You take the norm") {
      auto n = norm(p);
      THEN("You get 1") { CHECK(1.0 == n); }
    }
    // Generate ref allows for capture by reference
    auto u2 = GENERATE_REF(filter([&u1](size_t u) { return u != u1; }, range(0_z, PointT::size())));
    AND_GIVEN("element " << u2 << "being 1") {
      p[u2] = 1.0;
      WHEN("You take the norm") {
        auto n = norm(p);
        THEN("You get sqrt(2)") { CHECK(std::sqrt(2) == n); }
      }
    }
  }
  GIVEN("A point with element " << u1 << " being 2") {
    p[u1] = 2.0;
    WHEN("You take the norm") {
      auto n = norm(p);
      THEN("You get 2") { CHECK(2.0 == n); }
    }
  }
}

// SCENARIO("Basic Operations") {
TEMPLATE_TEST_CASE("Basic Operations", "[Addition][Multiplication][Division][Subtraction][Point][Scalar]",
                   POINTLIST) {
  using PointT = TestType;
  GIVEN("A Point") {
    // The following will generate variety of points
    // GENERATE creates a section by default that last until the statement is out of scope
    //   For conservation of white space, it is not indented
    //   but not that subsequent GENERATE blocks are equivalent to nested loops
    //   because it creates a 'section' everything contained creates a new test
    PointT p = zero<PointT>();
    auto x = GENERATE(range(-100.0, 100.0, 50.0));
    auto y = GENERATE(range(-200.0, 200.0, 100.0));
    auto z = GENERATE(range(-300.0, 300.0, 150.0));
    if (PointT::size() > 0) p[0] = x;
    if (PointT::size() > 1) p[1] = y;
    if (PointT::size() > 2) p[2] = z;
    auto notzero = false;
    for (auto u = 0u; u < PointT::size(); ++u)
      if (0 != p[u]) notzero = true;
    // The if works with the clauses to allow us to conditionally run test
    if (notzero) {
      WHEN("At least one element is not 0") {  // Paradigm reversal
        WHEN("You normalize it") {
          auto result = normalize(p);
          THEN("The magnitude is 1") { CHECK(Approx(1.0) == norm(result)); }
        }
      }
    }
    WHEN("You subtract it from itself") {
      auto result = subtract(p, p);
      THEN("The magnitude is 0") { CHECK(Approx(0.0) == norm(result)); }
    }
    WHEN("You add it to itself") {
      auto result = add(p, p);
      THEN("The magnitude (norm) doubles") { CHECK((2 * norm(p)) == (norm(result))); }
    }
    WHEN("You multiply by itself") {
      auto result = multiply(p, p);
      THEN("each element squares") {
        // We use a loop instead of GENERATE here because we are only doing one test.
        // A Generate would recreate the whole stack for each iteration
        for (auto u = 0u; u < PointT::size(); ++u) {
          CHECK(result[u] == (p[u] * p[u]));
        }
      }
    }
    auto zero = false;
    for (auto u = 0u; u < PointT::size(); ++u)
      if (0 == p[u]) zero = true;
    // The if works with the clauses to allow us to conditionally run test
    if (!zero) {
      WHEN("No element is 0") {  // This is a reversal of the standard paradigm because of conditional
                                 // execution
        AND_WHEN("You divide by itself") {
          auto result = divide(p, p);
          THEN("each element is 1") {
            for (auto u = 0u; u < PointT::size(); ++u) {
              CHECK(result[u] == 1);
            }
          }
        }
      }
    }
    AND_GIVEN("A scalar") {
      auto s = GENERATE(range(-10, 10));
      s /= 5;
      WHEN("You multiply by a scalar)") {
        auto result = multiply_scalar(p, s);
        THEN("each element is multiplied") {
          for (auto u = 0u; u < PointT::size(); ++u) {
            CHECK(result[u] == (p[u] * s));
          }
        }
      }
      if (s != 0.0) {
        WHEN("that scalar is not 0") {  // another reversal due to conditional execution
          AND_WHEN("You divide by a scalar)") {
            auto result = divide_scalar(p, s);
            THEN("each element is divided") {
              for (auto u = 0u; u < PointT::size(); ++u) {
                CHECK(result[u] == (p[u] / s));
              }
            }
          }
        }
      }
    }
  }
}

// SCENARIO("Cross Product") {
TEMPLATE_TEST_CASE("Cross Product", "[Point][Cross]", POINTLIST) {
  using PointT = TestType;
  GIVEN("2 unit vectors") {
    // Use Generate to cycle through all 3 sets
    auto u1 = GENERATE(range(0_z, PointT::size()));

    // We use 'zero' to create points because they don't initialize to 0 otherwise
    // TODO: Look into why they don't initialize to 0 (is it catch2 or tracktable)
    auto p1 = zero<PointT>();
    p1[u1] = 1.0;
    auto u2 = (u1 + 1) % PointT::size();
    auto p2 = zero<PointT>();
    p2[u2] = 1.0;

    if (PointT::size() == 3) {
      WHEN("Point is 3 Dimensional") {  // Reversal due to conditional
        // somewhat hacky way to get the 'other' coord;
        auto u3 =
            GENERATE_REF(filter([&](size_t u) { return u != u1 && u != u2; }, range(0_z, PointT::size())));
        WHEN("You take the cross product " << p1 << "X" << p2) {
          auto result = cross_product(p1, p2);
          THEN("The result is a unit vector in the missing dimension") {
            CHECK(0.0 == result[u1]);
            CHECK(0.0 == result[u2]);
            CHECK(1.0 == result[u3]);
          }
        }
        WHEN("You take the cross product the other way" << p2 << "X" << p1) {
          auto result = cross_product(p2, p1);
          THEN("The result is a negative unit vector in the missing dimension") {
            CHECK(0.0 == result[u1]);
            CHECK(0.0 == result[u2]);
            CHECK(-1.0 == result[u3]);
          }
        }
      }
    }
    // TODO: Implement 2D checks
  }
}
