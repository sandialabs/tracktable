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


#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

namespace tracktable { namespace python_wrapping {


    // Forward declaration
       template <class Container, bool NoProxy, class DerivedPolicies>
       class trajectory_indexing_suite;

       namespace detail
       {
          template <class Container, bool NoProxy>
          class final_trajectory_derived_policies
             : public trajectory_indexing_suite<
	           Container,
                   NoProxy,
                   final_trajectory_derived_policies<Container, NoProxy>
	           >
	   {};
       }

	template <class Container, bool NoProxy = false, class DerivedPolicies = detail::final_trajectory_derived_policies<Container, NoProxy>>
	class trajectory_indexing_suite
	  : public boost::python::vector_indexing_suite<Container, NoProxy, DerivedPolicies>
        {
        public:

	   typedef typename Container::size_type index_type;

  	   static boost::python::object
           get_slice(Container& container, index_type from, index_type to)
 	   {
		if (from > to)
		  return boost::python::object(Container());
		return boost::python::object(Container(container.begin()+from, container.begin()+to, container));
	   }
	};

}
}

