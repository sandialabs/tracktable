/*
 * Copyright (c) 2014-2019 National Technology and Engineering
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

/***
 *** GenericSerializablePickleSuite: Delegate Python pickling to
 *** boost::serialization
 ***
 *** Both Python's pickle module and Boost's serialization library aim
 *** to do the same thing: save and restore an object to a byte
 *** stream.  Rather than implement serialization twice for each
 *** object type, we will use this class to delegate Python pickle
 *** support to the underlying Boost serialization support.
 ***
 ***/


#ifndef __tracktable_GenericSerializablePickleSuite_h
#define __tracktable_GenericSerializablePickleSuite_h

#include <boost/python.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/binary_iarchive.hpp>

#include <sstream>

namespace tracktable { namespace python_wrapping {

template<class native_object_t>
class GenericSerializablePickleSuite : public boost::python::pickle_suite
{
public:
  
  static boost::python::tuple getstate(native_object_t const& object_to_pickle)
  {
    std::ostringstream outbuf;
    boost::archive::binary_oarchive archive(outbuf);

    archive << object_to_pickle;
    return boost::python::make_tuple(boost::python::str(outbuf.str()));
  }                                        
  
  static void setstate(native_object_t& object_to_restore, boost::python::tuple state)
  {
    using boost::python::tuple;
    using boost::python::str;
    
    str state_as_python_str((boost::python::extract<str>(state)));
    std::string state_as_string((boost::python::extract<std::string>(state_as_python_str)));
    std::istringstream inbuf(state_as_string);
    boost::archive::binary_iarchive archive(inbuf);
    
    
    archive >> object_to_restore;
  }
};

} } // namespace tracktable::python_wrapping

#endif
