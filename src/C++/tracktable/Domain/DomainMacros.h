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
 * These macros make it simple for us to say to the compiler "Treat
 * MyPointClass just like ThisOtherPointClass when you want to do math
 * on it."
 */

#ifndef __tracktable_DomainMacros_h
#define __tracktable_DomainMacros_h

#include <tracktable/Core/PointTraits.h>

#define TRACKTABLE_DELEGATE( NEW_CLASS, DELEGATE_CLASS, TRAIT ) \
  template<>                                                    \
  struct TRAIT < NEW_CLASS > : TRAIT < DELEGATE_CLASS > { };

#define TRACKTABLE_DELEGATE_COORDINATE_ACCESS( NEW_POINT, DELEGATE_POINT ) \
  template<size_t dim>                                                  \
struct access< NEW_POINT, dim > : access< DELEGATE_POINT, dim > { };


#define TRACKTABLE_DELEGATE_BOOST_POINT_TRAITS( NEW_POINT, DELEGATE_POINT ) \
  namespace boost { namespace geometry { namespace traits {             \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, tag )                 \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, coordinate_type )     \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, dimension )           \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, coordinate_system )   \
  TRACKTABLE_DELEGATE_COORDINATE_ACCESS( NEW_POINT, DELEGATE_POINT )    \
  } } }


#define TRACKTABLE_DELEGATE_TRAJECTORY_ALGORITHMS( NEW_CLASS, DELEGATE ) \
  namespace tracktable { namespace algorithms {                         \
  TRACKTABLE_DELEGATE( NEW_CLASS, DELEGATE, subset_during_interval )    \
  TRACKTABLE_DELEGATE( NEW_CLASS, DELEGATE, point_at_fraction )         \
  TRACKTABLE_DELEGATE( NEW_CLASS, DELEGATE, point_at_time )             \
  } }


#define TRACKTABLE_DELEGATE_POINT_ALGORITHMS( NEW_POINT, DELEGATE_POINT ) \
  namespace tracktable { namespace algorithms {                           \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, distance )              \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, bearing )               \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, interpolate )           \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, signed_turn_angle )     \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, unsigned_turn_angle )   \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, convex_hull_perimeter ) \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, convex_hull_area )      \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, convex_hull_centroid )  \
  } }

#define TRACKTABLE_DELEGATE_BASE_POINT_TRAITS( NEW_POINT, DELEGATE_POINT ) \
  namespace tracktable { namespace traits {                             \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, tag )                 \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, has_properties )      \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, dimension )           \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, undecorated_point )   \
  } }

#define TRACKTABLE_DELEGATE_TRAJECTORY_POINT_TRAITS( NEW_POINT, DELEGATE_POINT ) \
  namespace tracktable { namespace traits {                             \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, tag )                 \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, dimension )           \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, has_object_id )       \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, has_properties )      \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, has_timestamp )       \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, object_id )           \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, timestamp )           \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, undecorated_point )   \
  TRACKTABLE_DELEGATE( NEW_POINT, DELEGATE_POINT, point_domain_name )   \
  } }

#define TRACKTABLE_DELEGATE_DOMAIN_TRAIT(DOMAIN_NS, DOMAIN_TAG)        \
  namespace tracktable { namespace traits {                             \
      template<> struct domain<DOMAIN_NS::base_point_type>  { typedef DOMAIN_TAG type; }; \
      template<> struct domain<DOMAIN_NS::trajectory_point_type> : domain<DOMAIN_NS::base_point_type> {}; \
      template<> struct domain<DOMAIN_NS::trajectory_type> : domain<DOMAIN_NS::trajectory_point_type> {}; \
      template<> struct domain<DOMAIN_NS::linestring_type> : domain<DOMAIN_NS::base_point_type> {}; \
  } }

#define TRACKTABLE_DELEGATE_POINT_DOMAIN_NAME_TRAIT(DOMAIN_NS) \
  namespace tracktable { namespace traits {                                 \
    template<> struct point_domain_name<DOMAIN_NS::box_type> : point_domain_name<DOMAIN_NS::base_point_type> {};       \
  } }



#endif
