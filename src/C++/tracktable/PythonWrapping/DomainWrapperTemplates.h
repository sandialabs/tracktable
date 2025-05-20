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

#ifndef __tracktable_DomainWrapperTemplates_h
#define __tracktable_DomainWrapperTemplates_h

#include <boost/geometry/geometries/box.hpp>

#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>

#include <tracktable/Core/PointArithmetic.h>
#include <tracktable/Core/PointTraits.h>
#include <tracktable/Core/PropertyMap.h>
#include <tracktable/PythonWrapping/PythonFileLikeObjectStreams.h>
#include <tracktable/PythonWrapping/GenericSerializablePickleSuite.h>

namespace tracktable { namespace python_wrapping {

template<typename point_type>
boost::shared_ptr<point_type>
make_point_from_sequence(boost::python::object& coordinates)
{
  boost::shared_ptr<point_type> point(new point_type);
  assert(boost::python::len(coordinates) >=0 );
  if (size_t(boost::python::len(coordinates)) <
      tracktable::traits::dimension<point_type>::value)
    {
    throw std::runtime_error("make_point_from_sequence: Boost sequence does not have enough coordinates for point");
    }
  else
    {
    boost::python::object getitem = coordinates.attr("__getitem__");
    for (std::size_t i = 0; i < tracktable::traits::dimension<point_type>::value; ++i)
      {
      (*point)[i] = boost::python::extract<typename point_type::coordinate_type>(getitem(i));
      }
    return point;
    }
}

template<typename point_type>
boost::shared_ptr<point_type>
make_point_2d(double x, double y)
{
  boost::shared_ptr<point_type> point(new point_type);

  point->template set<0>(x);
  point->template set<1>(y);
  return point;
}


template<typename point_type>
boost::shared_ptr<
  point_type
  >
make_point_3d(double x, double y, double z)
{
  boost::shared_ptr<point_type> point(new point_type);

  point->template set<0>(x);
  point->template set<1>(y);
  point->template set<2>(z);
  return point;
}

template<typename point_type, typename box_type>
boost::shared_ptr<box_type>
make_box(point_type const& p1, point_type const& p2)
{
  boost::shared_ptr<box_type> box(new box_type);
  box->min_corner() = p1;
  box->max_corner() = p2;
  return box;
}

// NOTE: I could combine these two functions if I used boost::geometry::assign
// instead of copying the coordinates manually

template<typename box_type>
boost::shared_ptr<box_type>
make_box_2d_from_objects(boost::python::object& min_corner, boost::python::object& max_corner)
{
  using boost::python::extract;
  typedef typename boost::geometry::traits::point_type<box_type>::type point_type;
  typedef typename point_type::coordinate_type coordinate_type;

  boost::shared_ptr<box_type> box(new box_type);
  point_type& box_min_corner(box->min_corner());
  point_type& box_max_corner(box->max_corner());

  box_min_corner[0] = extract<coordinate_type>(min_corner[0]);
  box_min_corner[1] = extract<coordinate_type>(min_corner[1]);
  box_max_corner[0] = extract<coordinate_type>(max_corner[0]);
  box_max_corner[1] = extract<coordinate_type>(max_corner[1]);

  return box;
}

template<typename box_type>
boost::shared_ptr<box_type>
make_box_3d_from_objects(boost::python::object& min_corner, boost::python::object& max_corner)
{
  using boost::python::extract;
  typedef typename boost::geometry::traits::point_type<box_type>::type point_type;
  typedef typename point_type::coordinate_type coordinate_type;

  boost::shared_ptr<box_type> box(new box_type);
  point_type& box_min_corner(box->min_corner());
  point_type& box_max_corner(box->max_corner());

  box_min_corner[0] = extract<coordinate_type>(min_corner[0]);
  box_min_corner[1] = extract<coordinate_type>(min_corner[1]);
  box_min_corner[2] = extract<coordinate_type>(min_corner[2]);
  box_max_corner[0] = extract<coordinate_type>(max_corner[0]);
  box_max_corner[1] = extract<coordinate_type>(max_corner[1]);
  box_max_corner[2] = extract<coordinate_type>(max_corner[2]);
  return box;
}

// These functions give us [] in Python

template<class point_type>
void setitem_coordinate(point_type& pt, int index, double value)
{
  int dimension(boost::geometry::traits::dimension<point_type>::value);

  if (index < 0) index += dimension;
  if (index >= 0 && index < dimension)
    {
    pt[index] = value;
    }
  else
    {
    PyErr_SetString(PyExc_IndexError, "index out of range");
    boost::python::throw_error_already_set();
    }
}

template<class point_type>
double getitem_coordinate(point_type const& pt, int index)
{
  int dimension(boost::geometry::traits::dimension<point_type>::value);

  if (index < 0) index += dimension;
  if (index >= 0 && index < dimension)
    {
    return pt[index];
    }
  else
    {
    PyErr_SetString(PyExc_IndexError, "index out of range");
    boost::python::throw_error_already_set();
    return -1; // it's OK, compiler, I know what I'm doing
    }
}

template<class point_type>
int point_dimension(point_type const& /*pt*/)
{
  return boost::geometry::dimension<point_type>::value;
}

template<class domain_object_type>
std::string point_domain_name(domain_object_type const& /*thing*/)
{
  return tracktable::traits::point_domain_name<domain_object_type>::apply();
}

// Basic wrappers for point types - user-defined constructors will
// be added by the user

class basic_point_methods : public boost::python::def_visitor<basic_point_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      typedef typename ClassT::wrapped_type wrapped_type;
      using namespace boost::python;
      using namespace tracktable::arithmetic;

      c
        .def(init<>())
        .def("__init__", make_constructor(make_point_from_sequence<wrapped_type>))
        .def("__getitem__", getitem_coordinate<wrapped_type>)
        .def("__setitem__", setitem_coordinate<wrapped_type>)
        .def("__len__", point_dimension<wrapped_type>)
        .def("__add__", add<wrapped_type>)
        .def("__iadd__", add_in_place<wrapped_type>)
        .def("__sub__", subtract<wrapped_type>)
        .def("__isub__", subtract_in_place<wrapped_type>)
        .def("__mul__", multiply<wrapped_type>)
        .def("__imul__", multiply_in_place<wrapped_type>)
        .def("__div__", divide<wrapped_type>)
        .def("__idiv__", divide_in_place<wrapped_type>)
        .def("__mul__", multiply_scalar<wrapped_type, double>)
        .def("__rmul__", multiply_scalar<wrapped_type, double>)
        .def("__imul__", multiply_scalar_in_place<wrapped_type, double>)
        .def("__div__", divide_scalar<wrapped_type, double>)
        .def("__rdiv__", divide_scalar<wrapped_type, double>)
        .def("__idiv__", divide_scalar_in_place<wrapped_type, double>)
        .def("zero", zero<wrapped_type>)
        .def_pickle(GenericSerializablePickleSuite<wrapped_type>())
        .add_property("domain", point_domain_name<wrapped_type>)
        .staticmethod("zero")
        .def(self == self)
        .def(self != self)
        ;

    }
};

// ----------------------------------------------------------------------

template<typename ClassT>
struct typed_object_to_string
{
public:
  typedef typename ClassT::wrapped_type wrapped_type;

  static void save_name_for_later(ClassT const& c)
    {
      _name = boost::python::extract<std::string>(c.attr("__name__"));
    }

  static std::string str(wrapped_type const& thing)
    {
      std::ostringstream outbuf;
      outbuf << thing;
      return outbuf.str();
    }

  static std::string repr(wrapped_type const& thing)
    {
      std::ostringstream outbuf;
      outbuf << _name << str(thing);
      return outbuf.str();
    }

private:
  static std::string _name;
};

template<typename ClassT> std::string typed_object_to_string<ClassT>::_name;


// ----------------------------------------------------------------------

template<typename ClassT>
struct point_to_string
{
public:
  static void save_name_for_later(ClassT const& c)
    {
      _name = boost::python::extract<std::string>(c.attr("__name__"));
    }

  static std::string str(typename ClassT::wrapped_type const& thing)
    {
      std::ostringstream outbuf;
      outbuf << thing.to_string();
      return outbuf.str();
    }

  static std::string repr(typename ClassT::wrapped_type const& thing)
    {
      std::ostringstream outbuf;
      outbuf << _name << "(" << &thing << ")"; // str(thing);
      return outbuf.str();
    }

private:
  static std::string _name;
};

template<typename ClassT> std::string point_to_string<ClassT>::_name;

// ----------------------------------------------------------------------


class to_string_methods : public boost::python::def_visitor<to_string_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      using namespace boost::python;

      typed_object_to_string<ClassT>::save_name_for_later(c);
      c
        .def("__str__", &typed_object_to_string<ClassT>::str)
        .def("__repr__", &typed_object_to_string<ClassT>::repr)
        ;
    }
};


// ----------------------------------------------------------------------


template<typename ClassT>
class bbox_to_string
{
public:
  static void save_name_for_later(ClassT const& c)
    {
      _name = boost::python::extract<std::string>(c.attr("__name__"));
    }

  static std::string str(typename ClassT::wrapped_type const& thing)
    {
      std::ostringstream outbuf;
      outbuf << "BoundingBox(" << thing.min_corner()
             << " - "
             << thing.max_corner()
             << ")";
      return outbuf.str();
    }

  static std::string repr(typename ClassT::wrapped_type const& thing)
    {
      std::ostringstream outbuf;
      outbuf << _name << "(" << &thing << ")"; // str(thing);
      return outbuf.str();
    }

private:
  static std::string _name;
};

template<typename ClassT> std::string bbox_to_string<ClassT>::_name;


// ---------------------------------------------------------------------
//
class bbox_to_string_methods : public boost::python::def_visitor<bbox_to_string_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      using namespace boost::python;

      bbox_to_string<ClassT>::save_name_for_later(c);
      c
        .def("__str__", &bbox_to_string<ClassT>::str)
        .def("__repr__", &bbox_to_string<ClassT>::repr)
        ;
    }
};

// ----------------------------------------------------------------------


class point_to_string_methods : public boost::python::def_visitor<point_to_string_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      using namespace boost::python;

      point_to_string<ClassT>::save_name_for_later(c);
      c
        .def("__str__", &point_to_string<ClassT>::str)
        .def("__repr__", &point_to_string<ClassT>::repr)
        ;
    }
};

// ----------------------------------------------------------------------

class bounding_box_methods : public boost::python::def_visitor<bounding_box_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
  {
    typedef typename ClassT::wrapped_type wrapped_type;
    typedef typename boost::geometry::traits::point_type<wrapped_type>::type point_type;
    using namespace boost::python;

    point_type& (wrapped_type::*min_corner)() = &wrapped_type::min_corner;
    point_type& (wrapped_type::*max_corner)() = &wrapped_type::max_corner;
    c
    .def(bbox_to_string_methods())
    .add_property("min_corner", make_function(min_corner, return_internal_reference<>()))
    .add_property("max_corner", make_function(max_corner, return_internal_reference<>()))
    .add_property("domain", point_domain_name<wrapped_type>)
    ;
  }
};

// ----------------------------------------------------------------------

// This is meant to be used *along with* basic_point_methods, not
// *instead of*.
class trajectory_point_methods : public boost::python::def_visitor<trajectory_point_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      typedef typename ClassT::wrapped_type wrapped_type;
      using namespace boost::python;

      c
        .add_property("object_id", &wrapped_type::object_id, &wrapped_type::set_object_id)
        .add_property("timestamp", &wrapped_type::timestamp, &wrapped_type::set_timestamp)
        .add_property("current_length", &wrapped_type::current_length)
        .def(self == self)
        .def(self != self)
        ;
    }
};

class trajectory_methods : public boost::python::def_visitor<trajectory_methods>
{
	friend class boost::python::def_visitor_access;

	template<class ClassT>
	void visit(ClassT& c) const
	{
		typedef typename ClassT::wrapped_type wrapped_type;
        typedef typename wrapped_type::point_type point_type;
		using namespace boost::python;
        //deal with the fact that insert is already overloaded
        void (wrapped_type::*insert)(int, point_type const&) = &wrapped_type::insert;
		c
                  .add_property("duration", &wrapped_type::duration)
                  .add_property("domain", point_domain_name<wrapped_type>)
                  .add_property("trajectory_id", &wrapped_type::trajectory_id)
                  .add_property("object_id", &wrapped_type::object_id)
                  .def("insert", insert)
                  .def("clone", &wrapped_type::clone, return_value_policy<return_by_value>())
                  .def(self == self)
                  .def(self != self)
                  .def_pickle(GenericSerializablePickleSuite<wrapped_type>())
                  ;
	}
};

// Methods we use to access property maps from Python
class property_access_suite : public boost::python::def_visitor<property_access_suite>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      typedef typename ClassT::wrapped_type wrapped_type;
      using namespace boost::python;

      // This gobbledygook is how we get pointers to overloaded member
      // functions.  In this case we are taking the three overloads
      // for set_property and assigning them to variables named
      // set_property_double, set_property_string and
      // set_property_timestamp.
      void (wrapped_type::*set_property_variant)(std::string const&, tracktable::PropertyValueT const&) = &wrapped_type::set_property;
      tracktable::PropertyMap& (wrapped_type::*__properties)() = &wrapped_type::__non_const_properties;
      c
        .def("set_property", set_property_variant)
        .def("has_property", &wrapped_type::has_property)
        .def("property", &wrapped_type::property_without_checking)
        .add_property("properties", make_function(__properties, return_internal_reference<>() ))
        ;
    }
}; // end of property_access_suite


// Common methods for point readers
class cartesian2d_point_reader_methods : public boost::python::def_visitor<cartesian2d_point_reader_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      typedef typename ClassT::wrapped_type reader_type;
      using namespace boost::python;

      c
        .add_property("x_column", &reader_type::x_column, &reader_type::set_x_column)
        .add_property("y_column", &reader_type::y_column, &reader_type::set_y_column)
        ;
    }
};

class cartesian3d_point_reader_methods : public boost::python::def_visitor<cartesian3d_point_reader_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      typedef typename ClassT::wrapped_type reader_type;
      using namespace boost::python;

      c
        .add_property("x_column", &reader_type::x_column, &reader_type::set_x_column)
        .add_property("y_column", &reader_type::y_column, &reader_type::set_y_column)
        .add_property("z_column", &reader_type::z_column, &reader_type::set_z_column)
        ;
    }
};

class terrestrial_point_reader_methods : public boost::python::def_visitor<terrestrial_point_reader_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      typedef typename ClassT::wrapped_type reader_type;
      using namespace boost::python;

      c
        .add_property("longitude_column", &reader_type::longitude_column, &reader_type::set_longitude_column)
        .add_property("latitude_column", &reader_type::latitude_column, &reader_type::set_latitude_column)
        ;
    }
};

template<typename box_type>
std::string
box_to_string(box_type& box)
{
  std::ostringstream outbuf;
  outbuf << "(" << box.min_corner() << " - " << box.max_corner() << ")";
  return outbuf.str();
}

// ----------------------------------------------------------------------

template<typename trajectory_type>
trajectory_type*
trajectory_from_position_list(boost::python::list const& position_list)
{
  using namespace boost::python;
  typedef typename trajectory_type::point_type point_type;

  trajectory_type* trajectory = new trajectory_type;

  stl_input_iterator<object> iter(position_list), end;

  for (; iter != end; ++iter)
    {
    point_type next_point((extract<point_type>(*iter)));
    trajectory->push_back(next_point);
    }
  return trajectory;
}

// ----------------------------------------------------------------------

class basic_point_reader_methods : public boost::python::def_visitor<basic_point_reader_methods>

 {
   friend class boost::python::def_visitor_access;

   template<class ClassT>
   void visit(ClassT& c) const
     {
       typedef typename ClassT::wrapped_type reader_type;
       using namespace boost::python;

       c
         .def(init<>())
         .def(init<object>())
         .add_property("comment_character", &reader_type::comment_character, &reader_type::set_comment_character)
         .add_property("field_delimiter", &reader_type::field_delimiter, &reader_type::set_field_delimiter)
         .add_property("null_value", &reader_type::null_value, &reader_type::set_null_value)
         .def("has_coordinate_column", &reader_type::has_coordinate_column)
         .def("clear_coordinate_assignments", &reader_type::clear_coordinate_assignments)
         .add_property("coordinates", make_function(&reader_type::__coordinate_assignments, return_internal_reference<>()), &reader_type::__set_coordinate_assignments)
         .add_property("input", &reader_type::input_as_python_object, &reader_type::set_input_from_python_object)
         .def("__iter__", iterator<reader_type, return_value_policy<copy_const_reference> >())
         ;
    }
};


// Common methods for point readers
class trajectory_point_reader_methods : public boost::python::def_visitor<trajectory_point_reader_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      typedef typename ClassT::wrapped_type reader_type;
      using namespace boost::python;

      c
	.add_property("object_id_column", &reader_type::object_id_column, &reader_type::set_object_id_column)
	.add_property("timestamp_column", &reader_type::timestamp_column, &reader_type::set_timestamp_column)
        .add_property("timestamp_format", &reader_type::timestamp_format, &reader_type::set_timestamp_format)
        .def("set_real_field_column", &reader_type::set_real_field_column)
        .def("real_field_column", &reader_type::real_field_column)
        .def("set_string_field_column", &reader_type::set_string_field_column)
        .def("string_field_column", &reader_type::string_field_column)
        .def("set_time_field_column", &reader_type::set_time_field_column)
        .def("time_field_column", &reader_type::time_field_column)
 	;
    }
};


class trajectory_reader_methods : public boost::python::def_visitor<trajectory_reader_methods>

 {
   friend class boost::python::def_visitor_access;

   template<class ClassT>
   void visit(ClassT& c) const
     {
       typedef typename ClassT::wrapped_type reader_type;
       using namespace boost::python;

       c
         .def(init<>())
         .def(init<object>())
         .add_property("comment_character", &reader_type::comment_character, &reader_type::set_comment_character)
         .add_property("field_delimiter", &reader_type::field_delimiter, &reader_type::set_field_delimiter)
         .add_property("null_value", &reader_type::null_value, &reader_type::set_null_value)
         .add_property("input", &reader_type::input_as_python_object, &reader_type::set_input_from_python_object)
         .add_property("warnings_enabled", &reader_type::warnings_enabled, &reader_type::set_warnings_enabled)
         .def("__iter__", iterator<reader_type, return_value_policy<copy_const_reference> >())
         ;
    }
};

class common_writer_methods : public boost::python::def_visitor<common_writer_methods>
{
  friend class boost::python::def_visitor_access;

  template<class ClassT>
  void visit(ClassT& c) const
    {
      typedef typename ClassT::wrapped_type writer_type;
      using namespace boost::python;

      c
        .def(init<>())
        .def(init<object&>())
        .add_property("output",
                  &writer_type::output_as_python_object,
                  &writer_type::set_output_from_python_object)
        .add_property("field_delimiter",
                  &writer_type::field_delimiter,
                  &writer_type::set_field_delimiter)
        .add_property("null_value",
                      &writer_type::null_value,
                      &writer_type::set_null_value)
        .add_property("record_delimiter",
                      &writer_type::record_delimiter,
                      &writer_type::set_record_delimiter)
        .add_property("coordinate_precision",
                      &writer_type::coordinate_precision,
                      &writer_type::set_coordinate_precision)
        .add_property("quote_character",
                      &writer_type::quote_character,
                      &writer_type::set_quote_character)
        .def("write", &writer_type::write_python_sequence)
        ;
    }
};


} } // exit namespace tracktable::python_wrapping


#endif
