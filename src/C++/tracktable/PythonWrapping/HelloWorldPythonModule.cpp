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


// Tracktable Trajectory Library
//
// Boost.Python code for a trivial Hello World module
//
// Created by Danny Rintoul and Andy Wilson.

#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>

char const* greet()
{
	return "Hello world from Tracktable!";
}

class SimpleTestClass
{
public:
   SimpleTestClass() { this->Value = 0; }
   ~SimpleTestClass() { };

   void setValue(int value) { this->Value = value; }
   int getValue() const { return this->Value; }

   int Value;
};

BOOST_PYTHON_MODULE(_tracktable_hello)
{
	using namespace boost::python;
	def("greet", greet);

    class_<SimpleTestClass>("SimpleTestClass")
        .def(init<>())
// This line causes a segfault on module import
//        .add_property("value", &SimpleTestClass::getValue, &SimpleTestClass::setValue)
//        .def_readwrite("value", &SimpleTestClass::Value)
        .add_property("value", &SimpleTestClass::getValue)
        ;

}
