/*
 * Copyright (c) 2014-2017 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 */

// 
// rtree
//
// Our rtree implementation
//
// Created by Danny Rintoul.
//

#ifndef __rtree
#define __rtree
#include "Common.h"
#include <utility>
#include <boost/geometry.hpp>
#include <boost/array.hpp>
#include <boost/geometry/geometries/point.hpp>
#include <boost/geometry/geometries/register/point.hpp>
#include <boost/geometry/geometries/adapted/boost_array.hpp>
#include <boost/geometry/index/rtree.hpp>

// Here is the "by hand" thing that needs to be set for each run
// It describes the structure of your point.  There is probably a better
// way to do this.

BOOST_GEOMETRY_REGISTER_BOOST_ARRAY_CS(cs::cartesian)

typedef my_data* value;
typedef std::vector<value>::iterator data_itr;
typedef boost::geometry::index::quadratic<16> parameters;
typedef boost::geometry::model::box<Feature> box;

template <typename Container>
class my_indexable
{
//  typedef typename Container::iterator iterator;
  typedef typename Container::value_type* ptr;
  typedef typename Container::const_reference cref;
  Container const& container;

public:
  typedef cref result_type;
  explicit my_indexable(Container const& c) : container(c) {}
//  result_type operator()(iterator itr) const { return *itr; }
  result_type operator()(ptr p) const { return *p; }
};
typedef my_indexable< std::vector<my_data> > indexable_getter;

namespace boost { namespace geometry { namespace index {

template <>
struct indexable<value>
{
    typedef value value_type;
    typedef Feature const& result_type;
    result_type operator()(value_type const& v) const { return v->Point; }
};

}}}
typedef boost::geometry::index::rtree<value, parameters > my_rtree;

#endif
