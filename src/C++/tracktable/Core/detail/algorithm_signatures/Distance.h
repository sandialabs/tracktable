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

/*
 * BasePointDefaults - Top-level trait structs for things that can be
 * computed for any point type.
 */

#ifndef __tracktable_core_algorithms_detail_DistanceSignature_h
#define __tracktable_core_algorithms_detail_DistanceSignature_h

#include <tracktable/Core/detail/trait_signatures/Domain.h>

#include <boost/mpl/assert.hpp>
#include <boost/type_traits/is_same.hpp>
#include <cmath>

//#include <tracktable/Core/detail/trait_signatures/CoordinateSystem.h>

namespace tracktable { namespace algorithms {

template<typename DomainType>
struct distance
{
  BOOST_MPL_ASSERT_MSG(
    (sizeof(DomainType) == 0)
    , TRACKTABLE_DISTANCE_NOT_DEFINED_FOR_DOMAIN
    , (types<DomainType>)
  );
};


} } // namespace tracktable::algorithms

/*
 * Now we have functions that wrap the algorithms structs so that we can
 * call them easily instead of worrying about instantiation.
 */

namespace tracktable {

  template<class Geometry1, class Geometry2>
  double distance(Geometry1 const& from, Geometry2 const& to)
  {
    typedef typename tracktable::traits::domain<Geometry1>::type domain1;
    typedef typename tracktable::traits::domain<Geometry2>::type domain2;

    BOOST_MPL_ASSERT_MSG(
      (boost::is_same<domain1, domain2>::value),
      TRACKTABLE_DISTANCE_CANNOT_BE_COMPUTED_ACROSS_DIFFERENT_DOMAINS,
      (types<domain1,domain2>)
    );

    return algorithms::distance<domain1>::apply(from, to);
  }

} // namespace tracktable

#endif
