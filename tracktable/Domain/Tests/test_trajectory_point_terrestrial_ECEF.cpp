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

// This tells Windows that we want all the #defines from cmath
#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>

#include <iostream>
#include <sstream>

#include <tracktable/Core/PointCartesian.h>
#include <tracktable/Core/PointLonLat.h>

#include <tracktable/Core/TrajectoryPoint.h>

#include <tracktable/Domain/Terrestrial.h>
#include <tracktable/Domain/Cartesian3D.h>

typedef tracktable::domain::terrestrial::TerrestrialPoint TerrestrialPoint;
typedef tracktable::domain::terrestrial::TerrestrialTrajectoryPoint TerrestrialTrajectoryPoint;
typedef tracktable::domain::cartesian3d::CartesianPoint3D CartesianPoint3D;

//----------------------------------------------------

int verify_result(CartesianPoint3D actual, CartesianPoint3D expected, const char* description, double tolerance_fraction=1e-4)
{
    std::ostringstream errbuf;

    if ((fabs(actual[0] - expected[0]) > tolerance_fraction) ||
     (fabs(actual[1] - expected[1]) > tolerance_fraction) ||
     (fabs(actual[2] - expected[2]) > tolerance_fraction))
/*
    if ((!tracktable::almost_equal(actual[0], expected[0], tolerance_fraction))
     || (!tracktable::almost_equal(actual[1], expected[1], tolerance_fraction))
     || (!tracktable::almost_equal(actual[2], expected[2], tolerance_fraction)))
*/
    {
        std::cout << "ERROR: "
                  << description << " ECEF "
                  << "expected to be " << expected << " "
                  << "but actual ECEF is " << actual << "."
                  << fabs(actual[0] - expected[0]) << "\t"
                  << fabs(actual[1] - expected[1]) << "\t"
                  << fabs(actual[2] - expected[2]) << "\t"
                  << std::endl;
        return 1;
    }

    return 0;
}

TerrestrialTrajectoryPoint create_terrestrial_point(double lat, double lon, std::string const& id=std::string())
{
    TerrestrialTrajectoryPoint point;
    point.set_longitude(lon);
    point.set_latitude(lat);
    point.set_object_id(id);

    return point;
}

// ----------------------------------------------------------------------



int run_test()
{
    using namespace tracktable;

    int error_count = 0;

    std::cout << "Testing ECEF function" << std::endl;

    TerrestrialTrajectoryPoint lonlatzero = create_terrestrial_point(0.0, 0.0);
    TerrestrialTrajectoryPoint equatorpoint = create_terrestrial_point(0.0, 90.0);
    TerrestrialTrajectoryPoint northpole = create_terrestrial_point(90.0, 0.0);
    TerrestrialTrajectoryPoint northpole2 = create_terrestrial_point(90.0, -135.0);
    northpole2.set_property("altitude",100);
    TerrestrialTrajectoryPoint albuquerque = create_terrestrial_point(35.0844, -106.6504);

    CartesianPoint3D actual, expected;
    actual = lonlatzero.ECEF();
    expected[0] = 6378.137;
    expected[1] = 0.0;
    expected[2] = 0.0;
    error_count += verify_result(actual, expected, "LonLatZero");

    actual = equatorpoint.ECEF();
    expected[0] = 0.0;
    expected[1] = 6378.137;
    expected[2] = 0.0;
    error_count += verify_result(actual, expected, "EquatorPoint");

    actual = northpole.ECEF();
    expected[0] = 0.0;
    expected[1] = 0.0;
    expected[2] = 6356.75231;
    error_count += verify_result(actual, expected, "NorthPole",1e-4);

    actual = northpole2.ECEF("altitude");
    expected[0] = 0.0;
    expected[1] = 0.0;
    expected[2] = 6456.75231;
    error_count += verify_result(actual, expected, "NorthPole2",1e-4);

    actual = albuquerque.ECEF();
    expected[0] = -1497.14022;
    expected[1] = -5005.96887;
    expected[2] = 3645.53304;
    error_count += verify_result(actual, expected, "Albuquerque");

    std::cout << "Testing exception throw" << std::endl;
    bool thrown = false;
    try {
        albuquerque.ECEF_from_feet();

    } catch(tracktable::domain::terrestrial::PropertyDoesNotExist &e) {
        thrown = true;
    }
    if (!thrown) {
      std::cout << "Failed to throw exception when attribute not present" << std::endl;
      ++error_count;
    }
    try {
      albuquerque.ECEF("altitude");
    } catch (tracktable::domain::terrestrial::PropertyDoesNotExist &e) {
      thrown = true;
    }
    if (!thrown) {
      std::cout << "Failed to throw exception when attribute not present" << std::endl;
      ++error_count;
    }
    std::cout << "Testing ECEF_from_meters" << std::endl;
    albuquerque.set_property("altitude", 1000);
    actual = albuquerque.ECEF_from_meters();
    expected[0] = -1497.375;
    expected[1] = -5006.753;
    expected[2] = 3646.108;
    error_count += verify_result(actual, expected, "AlbuquerqueMetters",1e-2);
    std::cout << "Testing ECEF_from_feet" << std::endl;
    albuquerque.set_property("height", 1000);
    actual = albuquerque.ECEF_from_feet("height");
    expected[0] = -1497.212;
    expected[1] = -5006.208;
    expected[2] = 3645.708;
    error_count += verify_result(actual, expected, "AlbuquerqueFeet", 1e-2);
    return error_count;
}

int main(int, char **)
{
    return run_test();
}

