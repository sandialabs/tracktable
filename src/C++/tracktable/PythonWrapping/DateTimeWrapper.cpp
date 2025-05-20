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
// Boost.Python code to convert datetime.datetime <-> boost::posix_time::ptime
//
// Since C++ and Python have their own separate date/time classes that
// work perfectly well, we use code to convert transparently between
// them instead of trying to write our own from scratch.
//
// The gotcha, as always, is time zones.  We don't have a great
// solution for this.  For the time being we solve it by convention.
// In C++, you are responsible for keeping all your times in UTC
// (which is a good idea regardless).  In Python, all times will be in
// UTC unless you work to make it otherwise.
//
// Based on code at the following two web pages:
//
// http://code.activestate.com/recipes/576395-convert-datetimedatetime-objects-tofrom-boostpytho/
//
// http://www.boost.org/doc/libs/1_35_0/libs/python/doc/v2/faq.html#custom_string

#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>

#include <tracktable/Core/WarningGuards/PushWarningState.h>
#include <tracktable/Core/WarningGuards/ShadowedDeclaration.h>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/date_time/gregorian/gregorian.hpp>
#include <tracktable/Core/WarningGuards/PopWarningState.h>

// This relies on Python.h
#include <datetime.h>

#include <tracktable/Core/Timestamp.h>

namespace
{
  boost::python::object DEFAULT_TIMEZONE;

  bool already_installed = false;

  long get_usecs(boost::posix_time::time_duration const& d)
  {
    static long resolution = boost::posix_time::time_duration::ticks_per_second();
    long fracsecs = d.fractional_seconds();
    if (resolution > 1000000)
      {
      return fracsecs / ( resolution / 1000000 );
      }
    else
      {
      return fracsecs * (1000000 / resolution);
      }
  }

  /// Utility function: wrap a PyObject* without assuming ownership
  //
  // Normally, a boost::python::object created around a PyObject
  // pointer assumes ownership of the object.  This convenience function
  // creates a borrowed reference that will not lead to the wrapped object's
  // destruction when the wrapper goes out of scope.
  //
  // @param[in] py_object (PyObject*) Object to wrap
  // @return New boost::python::object wrapping Python object

  boost::python::object borrowed_reference(PyObject* py_object)
  {
    return boost::python::object(
      boost::python::handle<>(
        boost::python::borrowed(py_object)));
  }

  /// Localize a timestamp into the default timezone
  //
  // Timestamps may come in from Python with arbitrary time zones
  // attached.  This function creates a new timestamp guaranteed to
  // be in our default timezone.
  //
  // @param[in] timestamp: (PyDateTime_DateTime*) Time stamp from Python
  // @returns New boost::python::object containing an aware datetime
  //     object in our default time zone
  boost::python::object as_default_timezone(PyObject* timestamp)
  {
    using boost::python::object;

    object foreign_timestamp(borrowed_reference(timestamp));
    object fn_astimezone(foreign_timestamp.attr("astimezone"));
    if (fn_astimezone.is_none())
    {
      PyErr_SetString(PyExc_AttributeError,
        "Timestamp to convert has no astimezone attribute");
      boost::python::throw_error_already_set();
    }

    // This will create a new datetime.datetime in our default
    // timezone.
    return fn_astimezone(DEFAULT_TIMEZONE);
  }

  /// Convert a boost::posix::ptime to a Python datetime.datetime
  //
  // \note The only non-obvious thing going on here is that we bypass
  //       the convenience macros in PyDateTimeAPI to call a
  //       constructor function that takes a pointer to a timezone
  //       struct.
  //
  // \note One can quite reasonably make the argument that almost
  //       nothing about the Python<->C API is obvious.
  //
  struct ptime_to_python_datetime
  {
    static PyObject* convert(boost::posix_time::ptime const& pt)
      {
        boost::gregorian::date date = pt.date();
        boost::posix_time::time_duration td = pt.time_of_day();

        if (::DEFAULT_TIMEZONE.ptr() == Py_None)
          {
          // We don't have a default timezone.  How did this happen?
          PyObject* datetime = PyDateTime_FromDateAndTime(
            static_cast<int>(date.year()),
            static_cast<int>(date.month()),
            static_cast<int>(date.day()),
            td.hours(),
            td.minutes(),
            td.seconds(),
            get_usecs(td));

          return datetime;
          }
        else
          {
          // In order to create 'aware' datetime objects (i.e. those
          // with a non-null tzinfo member) we have to call the Python
          // constructor directly instead of using the convenience
          // macro.  Fortunately this is not a big deal.

          PyObject* datetime = PyDateTimeAPI->DateTime_FromDateAndTime(
            static_cast<int>(date.year()),
            static_cast<int>(date.month()),
            static_cast<int>(date.day()),
            td.hours(),
            td.minutes(),
            td.seconds(),
            get_usecs(td),
            ::DEFAULT_TIMEZONE.ptr(),
            PyDateTimeAPI->DateTimeType);

          return datetime;
          }
      }
  };

  /// Convert from a Python datetime to a boost::posix::ptime
  //
  // This is a lot more straightforward since we don't need
  // to deal with Python reference counting.  We use
  // convenience macros to extract the components of a timestamp
  // and stuff them into a boost::posix_time::ptime.
  //
  // \note The 'convertible' function is used by the Python C
  //       API to decide whether or not a converter can be
  //       applied to a given object.
  struct ptime_from_python_datetime
  {
    ptime_from_python_datetime()
      {
        boost::python::converter::registry::push_back(
          &convertible,
          &construct,
          boost::python::type_id< boost::posix_time::ptime > ());
      }

    static void* convertible(PyObject* obj_ptr)
      {
        if (!PyDateTime_Check(obj_ptr))
          {
          return 0;
          }
        else
          {
          return obj_ptr;
          }
      }

    // XXX Does this function actually need to be here?
    static void construct(PyObject* obj_ptr,
                          boost::python::converter::rvalue_from_python_stage1_data* data)
      {
        boost::python::object localized_pydate(as_default_timezone(obj_ptr));

        PyDateTime_DateTime const* raw_localized_pydate =
          reinterpret_cast<PyDateTime_DateTime const*>(
            localized_pydate.ptr());

        // Create date object
        boost::gregorian::date
          _date(PyDateTime_GET_YEAR(raw_localized_pydate),
                PyDateTime_GET_MONTH(raw_localized_pydate),
                PyDateTime_GET_DAY(raw_localized_pydate));

        // Create time duration object
        boost::posix_time::time_duration
          _duration(PyDateTime_DATE_GET_HOUR(raw_localized_pydate),
                    PyDateTime_DATE_GET_MINUTE(raw_localized_pydate),
                    PyDateTime_DATE_GET_SECOND(raw_localized_pydate),
                    0);
        // Set the usecs
        _duration += boost::posix_time::microseconds(
          PyDateTime_DATE_GET_MICROSECOND(raw_localized_pydate));

        // Create POSIX time object
        void* storage =
          ((boost::python::converter::rvalue_from_python_storage<boost::posix_time::ptime>*)data)->storage.bytes;
        new (storage) boost::posix_time::ptime(_date, _duration);
        data->convertible = storage;
      }
  };


  // Below this point we have classes that perform much the same
  // function as the converters for datetime.datetime and
  // boost::posix_time::ptime but with datetime.timedelta and
  // boost::posix_time::time_duration instead.

  /// Convert time_duration to datetime.timedelta
  struct tduration_to_python_delta
  {
    static PyObject* convert(boost::posix_time::time_duration d)
      {
        long days = d.hours() / 24;
        if (days < 0)
          {
          --days;
          }
        long seconds = d.total_seconds() - days*(24*3600);
        long usecs = get_usecs(d);
        if (days < 0)
          {
          usecs = 1000000 - 1 - usecs;
          }
        return PyDelta_FromDSU(days, seconds, usecs);
      }
  };

  /// Convert datetime.timedelta to boost::posix_time::time_duration
  struct tduration_from_python_delta
  {
    tduration_from_python_delta()
      {
        boost::python::converter::registry::push_back(
          &convertible,
          &construct,
          boost::python::type_id<boost::posix_time::time_duration>()
          );
      }

    static void* convertible(PyObject* obj_ptr)
      {
        if (!PyDelta_Check(obj_ptr))
          {
          return 0;
          }
        else
          {
          return obj_ptr;
          }
      }

    static void construct(
      PyObject* obj_ptr,
      boost::python::converter::rvalue_from_python_stage1_data* data
      )
      {
        PyDateTime_Delta const* pydelta = reinterpret_cast<PyDateTime_Delta*>(obj_ptr);
        long days = pydelta->days;
        bool is_negative = (days < 0);
        if (is_negative)
          {
          days = -days;
          }

        // Create time duration object
        boost::posix_time::time_duration
          duration = boost::posix_time::hours(24)*days
          + boost::posix_time::seconds(pydelta->seconds)
          + boost::posix_time::microseconds(pydelta->microseconds);
        if (is_negative)
          {
          duration = duration.invert_sign();
          }

        void* storage =
          (( boost::python::converter::rvalue_from_python_storage<boost::posix_time::time_duration> *)data)->storage.bytes;
        new (storage) boost::posix_time::time_duration(duration);
        data->convertible = storage;
      }
  };

}

/// Make sure DEFAULT_TIMEZONE gets dereferenced at shutdown time
//
// Because of the order in which libraries get unloaded when the
// Python interpreter shuts down, we can get into a situation where
// ::DEFAULT_TIMEZONE is invalid but the interpreter still thinks the
// pointer is live.  This struct prevents that by zeroing out the
// pointer (thus releasing the reference held by the interpreter) when
// it goes out of scope.
struct DefaultTimezoneGuard
{
public:
  DefaultTimezoneGuard() { }
  ~DefaultTimezoneGuard() { ::DEFAULT_TIMEZONE = boost::python::object(); }
};


/// Register converters with the Python interpreter
//
// This function must be called in order for the Python interpreter to
// know how to convert datetime and ptime back and forth.
void install_datetime_converters()
{
  if (::already_installed == false)
    {
    ::already_installed = true;

    if (PyDateTimeAPI == 0)
      {
      PyDateTime_IMPORT;
      }

    ::ptime_from_python_datetime();

    boost::python::to_python_converter<
      const boost::posix_time::ptime,
      ::ptime_to_python_datetime
      >();

    ::tduration_from_python_delta();

    boost::python::to_python_converter<
      const boost::posix_time::time_duration,
      ::tduration_to_python_delta
      >();

    boost::shared_ptr<DefaultTimezoneGuard> guard(new DefaultTimezoneGuard);

    boost::python::class_<DefaultTimezoneGuard, boost::shared_ptr<DefaultTimezoneGuard>, boost::noncopyable>("DefaultTimezoneGuard", boost::python::no_init);

    boost::python::scope().attr("__tzguard") = guard;
    }
}

// ----------------------------------------------------------------------

/// Set a default timezone to use during conversion
//
// In the Python side of the house we maintain the notion of a default
// timezone for new timestamp objects.  We keep a pointer to it here
// so that when we convert a ptime to a datetime we can imbue it with
// that timezone.
void
set_default_timezone(boost::python::object tz)
{
  using namespace boost::python;
  ::DEFAULT_TIMEZONE = tz;
}

// ----------------------------------------------------------------------

/// Register functions related to timestamps
//
// So far we only have the one function.
void
install_timestamp_functions()
{
  using namespace boost::python;

  def("set_default_timezone", set_default_timezone);
}
