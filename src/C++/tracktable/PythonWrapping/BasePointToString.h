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
 * BasePointToString - Methods usable by Boost.Python to convert
 * a base_point_type (in whatever domain) to a string, both
 * human-readable and Python repr() versions.
 */

#ifndef __tracktable_PythonWrapping_BasePointToString_h
#define __tracktable_PythonWrapping_BasePointToString_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>
#include <sstream>


namespace tracktable { namespace python_wrapping {

/** Methods for str() and repr() for simple points
 *
 * In Python, str(thing) should produce a human-readable
 * representation of 'thing' and repr(thing) should
 * produce a machine-interpretable version.  For base points
 * (those with no information beyond the point's coordinates
 * and coordinate space) we want those to look like this:
 *
 * str(my_point) -> "(1, 2)"
 * repr(my_point) -> "tracktable.domain.terrestrial.BasePoint(1, 2)"
 *
 * The template base_point_to_string class contains machinery to
 * implement both of those.  You do have to initialize it with
 * the Python name you want to use in repr().  See the class
 * base_point_to_string_methods for an example of how to do that
 * and the function install_base_point_wrappers() in
 * tracktable/PythonWrapping/TerrestrialDomainModule.cpp
 * to see how it's called at runtime.
 */

namespace implementation {

template<typename ClassT>
struct base_point_to_string
{
public:
  typedef typename ClassT::wrapped_type wrapped_type;

  static void save_class_name(string_type const& classname)
    {
      _name = classname;
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

template<typename ClassT> std::string base_point_to_string<ClassT>::_name;

} // close namespace implementation inside tracktable::python_wrapping

// ----------------------------------------------------------------------

class base_point_to_string_methods : public boost::python::def_visitor<base_point_to_string_methods>
{
  friend class boost::python::def_visitor_access;

public:
  base_point_to_string_methods(string_type const& classname)
  {
    this->SavedClassName = classname;
  }

  template<class ClassT>
  void visit(ClassT& c) const
    {
      using namespace boost::python;
      implementation::base_point_to_string<ClassT>::save_class_name(this->SavedClassName);
      c
        .def("__str__", &implementation::base_point_to_string<ClassT>::str)
        .def("__repr__", &implementation::base_point_to_string<ClassT>::repr)
        ;
    }

private:
  string_type SavedClassName;
};


} } // close namespace tracktable::python_wrapping

#endif
