/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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

#include <tracktable/Core/PointTypes.h>
#include <iostream>

template<class point_type>
bool test_point_type(point_type const& left, point_type const& right)
{
  std::cout << traits::dimension<point_type>::value << "-D points: "
            << left << ", " << right << "\n";

  std::cout << "Point magnitude: "
            << tracktable::magnitude(left)
            << ", "
            << tracktable::magnitude(right)
            << "\n";

  std::cout << "Point sum, difference, product, quotient, inner product:\n";
  std::cout << "   Sum: "
            << left + right << "\n";
  std::cout << "   Difference: "
            << left - right << "\n";
  std::cout << "   Elementwise product: "
            << left * right << "\n";
  std::cout << "   Elementwise quotient: "
            << left / right << "\n";
  std::cout << "   Inner product: "
            << tracktable::dot_product(left, right) << "\n";

  std::cout << "Scalar multiplication and division (by 10):\n";
  std::cout << "   Multiplication: "
            << left * 10 << ", " << right * 10 << "\n";
  std::cout << "   Division: "
            << left / 10 << ", " << right / 10 << "\n";

  std::cout << "In-place operators:\n";
  point_type new_point(left);
  new_point += right;

  std::cout << "   Addition: ";
  std::cout << new_point << "\n";

  new_point = left;
  new_point -= right;
  std::cout << "   Subtraction: " << new_point << "\n";

  new_point = left;
  new_point *= right;
  std::cout << "   Pointwise multiplication: " << new_point << "\n";

  new_point = left;
  new_point /= right;
  std::cout << "   Pointwise division: " << new_point << "\n";

  new_point = left;
  new_point *= 10;
  std::cout << "   Scalar multiplication: " << new_point << "\n";

  new_point = left;
  new_point /= 10;
  std::cout << "   Scalar division: " << new_point << "\n";

  return true;
}

bool test_point_types()
{
  typedef tracktable::Point<2> point2;
  typedef tracktable::Point<10> point10;

  double xcoords[2] = { 2, 3 };
  point2 x(xcoords);

  point2 y(x);
  y *= 10;

  point10 a(coords1);
  point10 b(coords2);

  for (int i = 0; i < 10; ++i)
    {
    a[i] = i+1;
    b[i] = i*i+1;
    }

  test_point_type(x, y);
  test_point_type(a, b);
  return true;
}

int main(int argc, char* argv[])
{
  test_point_types();
  return 0;
}

