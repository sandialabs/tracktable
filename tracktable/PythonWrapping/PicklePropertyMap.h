/*
 * Copyright (c) 2014, Sandia Corporation.  All rights
 * reserved.
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


//
// PythonWrapping/PicklePropertyMap.h
//
// Pickle support for tracktable::PropertyValueT and tracktable::PropertyMap.
//

#ifndef __tracktable_PicklePropertyMap_h
#define __tracktable_PicklePropertyMap_h

#include <tracktable/Core/PropertyMap.h>
#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/PythonWrapping/PickleSuites.h>

namespace tracktable { namespace traits {

namespace bp = boost::python;

/// Pickle and unpickle PropertyValueT, a boost::variant
//
// All we really need to do here is ask Boost for the underlying data
// type and emit an appropriate Python object.
template<>
struct pickle_suite< ::tracktable::PropertyValueT > : public boost::python::pickle_suite
{
  /// Use simpler boost::python pickle call
  static boost::python::tuple
  getinitargs(tracktable::PropertyValueT const& value)
    {
      try
        {
        double d_value = boost::get<double>(value);
        return bp::make_tuple(d_value);
        }
      catch (boost::bad_get e)
        {
        try
          {
          std::string s_value = boost::get<std::string>(value);
          return bp::make_tuple(s_value);
          }
        catch (boost::bad_get e)
          {
          try
            {
            tracktable::Timestamp t_value = boost::get<tracktable::Timestamp>(value);
            return bp::make_tuple(t_value);
            }
          catch (boost::bad_get e)
            {
            std::cerr << "ERROR: pickle_property_variant: Couldn't downcast the variant to a double, a string or a timestamp\n";
            return bp::make_tuple(0);
            }
          }
        }
    }
};

/// Pickle and unpickle PropertyMap
//
// Since this is more complex than a POD type -- it behaves as a
// mutable Python object in its own right -- we need to iterate over
// its entries ourselves and pickle them, then reverse the process
// during unpickling.  This is not that difficult once we've figured
// it out but it took a lot of wading through the Boost.Python
// documentation to get to the right place.
template<>
struct pickle_suite< ::tracktable::PropertyMap > : public boost::python::pickle_suite
{
  /// Convenience alias
  //
  // We'll use this later on to make it clear what we're extracting and why.
  typedef ::tracktable::PropertyMap native_object_t;

  /// Handle the property map's __dict__
  //
  // Since this object is exposed in Python, users can set any
  // properties they want on it without consulting us.  Those get
  // stored in the object's __dict__ attribute.  By saving that here
  // we can preserve it even though those properties may not be
  // accessible directly from C++.
  static boost::python::tuple
  getstate(boost::python::object py_obj)
    {
      const native_object_t& native_obj = boost::python::extract<native_object_t>(py_obj)();
      return boost::python::make_tuple( pickle_suite<native_object_t>::getnativestate(native_obj),
                                        py_obj.attr("__dict__") );
    }

  /// Handle the property map's __dict__
  //
  // Since this object is exposed in Python, users can set any
  // properties they want on it without consulting us.  Those get
  // stored in the object's __dict__ attribute.  By restoring that
  // here we give them back to Python whether or not we can use them.
  static void
  setstate(boost::python::object py_obj, boost::python::tuple state)
    {
      native_object_t& native_obj = boost::python::extract<native_object_t&>(py_obj)();
      pickle_suite<native_object_t>::setnativestate(native_obj,
                                                    boost::python::extract<boost::python::tuple>(state[0])());
      boost::python::dict d = boost::python::extract<boost::python::dict>(py_obj.attr("__dict__"));
      d.update(state[1]);
    }

  /// Iterate over and pickle the entries in the map
  //
  // Since we already have a pickle/unpickle suite for PropertyValueT
  // itself, pickling the contents of the propetry map becomes a
  // simple walk over its contents.
  static boost::python::tuple
  getnativestate(tracktable::PropertyMap const& pmap)
    {
      boost::python::list property_values;
      for (tracktable::PropertyMap::const_iterator iter = pmap.begin();
           iter != pmap.end();
           ++iter)
        {
        std::string property_name = (*iter).first;
        tracktable::PropertyValueT value = (*iter).second;
        property_values.append(bp::make_tuple(property_name, value));
        }
      return boost::python::make_tuple(property_values);
    }

  /// Populate a property map from pickled values
  //
  // When we unpickle property values we get back boost::variant
  // objects.  The simplest way to discover what they are and thus
  // insert them back into the property map is to ask Boost:
  //
  // Is this thing a double? If so, set the property as a double.
  // If not, is it a timestamp? If so, set the property as a timestamp.
  // If not, is it a string? If so, set the property as a string.
  // If not, raise an exception and complain bitterly.
  static void
  setnativestate(tracktable::PropertyMap& new_pmap, boost::python::tuple state)
    {
      bp::list saved_values = bp::extract<bp::list>(state[0])();

      // Restore the entries in the property map
      for (int i = 0; i < bp::len(saved_values); ++i)
        {
        std::string name = bp::extract<std::string>(saved_values[i][0])();

        bp::extract<double> get_double(saved_values[i][1]);
        bp::extract<tracktable::Timestamp> get_timestamp(saved_values[i][1]);
        bp::extract<std::string> get_string(saved_values[i][1]);


        if (get_double.check())
          {
          tracktable::set_property(new_pmap, name, get_double());
          }
        else if (get_timestamp.check())
          {
          tracktable::set_property(new_pmap, name, get_timestamp());
          }
        else if (get_string.check())
          {
          tracktable::set_property(new_pmap, name, get_string());
          }
        else
          {
          PyErr_SetObject(PyExc_ValueError,
                          ("Unpickling PropertyMap: Couldn't downcast object %s into a PropertyValueT" % state[i][1]).ptr());
          bp::throw_error_already_set();
          }
        }
    }

  /// Tell Python that we will handle the object's __dict__ ourselves.
  static bool getstate_manages_dict() { return true; }

};

} } // exit namespace tracktable::traits

#endif
