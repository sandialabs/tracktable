/*
 * Copyright (c) 2014-2018 National Technology and Engineering
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


#ifndef __tracktable_Trajectory_h
#define __tracktable_Trajectory_h

#include <tracktable/Core/TracktableCommon.h>
#include <tracktable/Core/PropertyMap.h>
#include <tracktable/Core/Timestamp.h>

#include <tracktable/Core/detail/algorithm_signatures/EndToEndDistance.h>
#include <tracktable/Core/detail/algorithm_signatures/Length.h>
#include <tracktable/Core/detail/algorithm_signatures/PointAtFraction.h>
#include <tracktable/Core/detail/algorithm_signatures/PointAtTime.h>
#include <tracktable/Core/detail/algorithm_signatures/TimeAtFraction.h>
#include <tracktable/Core/detail/algorithm_signatures/SubsetDuringInterval.h>

#include <tracktable/Core/detail/implementations/PointAtFraction.h>
#include <tracktable/Core/detail/implementations/PointAtTime.h>
#include <tracktable/Core/detail/implementations/TimeAtFraction.h>
#include <tracktable/Core/detail/implementations/SubsetDuringInterval.h>
#include <tracktable/Core/detail/trait_signatures/HasProperties.h>

#include <tracktable/Core/GuardedBoostGeometryHeaders.h>
#include <boost/geometry/geometries/register/linestring.hpp>

#include <boost/serialization/string.hpp>
#include <boost/serialization/map.hpp>
#include <boost/serialization/vector.hpp>
#include <boost/serialization/variant.hpp>

#include <cassert>
#include <ostream>
#include <vector>
#include <typeinfo>

namespace tracktable {

/**
 * \class Trajectory
 *
 * \brief Ordered sequence of points
 *
 * This class is the heart of most of what Tracktable does.  It
 * implements an ordered sequence of TrajectoryPoint objects, each of
 * which has an ID, coordinates and a timestamp.  Those compose a
 * trajectory.
 *
 * We provide accessors so that you can treat a Trajectory as if it
 * were a std::vector.
 */

template< class PointT >
class Trajectory
{
  friend class boost::serialization::access;
  
public:
  /// Convenient aliases for template parameters and types from internal storage
  //
  // These typedefs make this class look almost exactly like a
  // std::vector so that you can cleanly use it as such with the C++
  // STL.
  typedef PointT point_type;
  typedef std::vector<PointT> point_vector_type;
  typedef typename point_vector_type::iterator iterator;
  typedef typename point_vector_type::const_iterator const_iterator;
  typedef typename point_vector_type::size_type size_type;
  typedef typename point_vector_type::value_type value_type;
  typedef typename point_vector_type::difference_type difference_type;
  typedef typename point_vector_type::reference reference;
  typedef typename point_vector_type::const_reference const_reference;

  /// Instantiate an empty trajectory
  Trajectory() { }
  ~Trajectory() { }

  /// Create a trajectory a copy of another
  Trajectory(const Trajectory& other) :
    Points(other.Points),
    Properties(other.Properties)
      { }

  /// Make this trajectory a copy of another
  Trajectory& operator=(const Trajectory& other)
    {
      this->Points = other.Points;
      this->Properties = other.Properties;
      return *this;
    }

  /** Return the start time if available.
   *
   * If there are any points in the trajectory this method will return
   * the timestamp on the first point.  If not, it will return an
   * invalid Timestamp.
   */
  Timestamp start_time() const
    {
      if (this->Points.size())
        {
        return this->Points[0].timestamp();
        }
      else
        {
        return ::tracktable::no_such_timestamp();
        }
    }

  /** Return the end time if available.
   *
   * If there are any points in the trajectory this method will return
   * the timestamp on the last point.  If not, it will return an
   * invalid Timestamp.
   */
  Timestamp end_time() const
    {
      if (this->Points.size())
        {
        return this->Points[this->Points.size() - 1].timestamp();
        }
      else
        {
        return ::tracktable::no_such_timestamp();
        }
    }

  /** Return the duration, if available.
  *
  * If there are any points in the trajectory, this method will return
  * the duration of the trajectory.  If not it will return a duration of 0.
  *
  * @return the difference of end_time and start_time or 0 if no points.
  */
  Duration duration() const
  {
	  if (this->Points.size())
	  {
		  return this->Points[this->Points.size() - 1].timestamp() -
			  this->Points[0].timestamp();
	  }
	  else
	  {
		  return Duration(0,0,0,0);
	  }
  }

  /** Return the ID of the moving object.
   *
   * If there are any points in the trajectory, return the object ID
   * of the first one.  Otherwise return the string "(empty)".
   */
  std::string object_id() const
    {
      if (this->Points.size() == 0)
        {
        return std::string("(empty)");
        }
      else
        {
        return this->Points[0].object_id();
        }
    }

  /** Return a unique ID for the trajectory.
   *
   * Return a unique ID for the trajectory incorporating its object
   * ID, start time and end time.  If the trajectory is empty then we
   * will return the string "(empty)".
   */
  std::string trajectory_id() const
    {
      if (this->Points.size() == 0)
        {
        return std::string("(empty)");
        }
      else
        {
        std::ostringstream outbuf;
        outbuf << this->object_id() << "//"
               << this->start_time() << "//"
               << this->end_time();
        return outbuf.str();
        }
    }

  /// Set a named property with a variant value (let the caller handle the type)
  void set_property(std::string const& name, PropertyValueT const& value)
    {
      ::tracktable::set_property(this->Properties, name, value);
    }

  /// Retrieve a named property with checking
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a boost::variant
  PropertyValueT property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::property(this->Properties, name, ok);
    }

  /// Retrieve a named property without safety checking
  //
  // It is the caller's responsibility to know whether the requested
  // property actually exists when using this function.
  //
  // \param name Name of property to retrieve
  // \return Property as a boost::variant
  PropertyValueT property_without_checking(std::string const& name) const
    {
      bool ok;
      return ::tracktable::property(this->Properties, name, &ok);
    }

  /// Safely retrieve a named property with a string value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a std::string
  std::string string_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::string_property(this->Properties, name, ok);
    }

  /// Safely retrieve a named property with a floating-point value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a double
  double real_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::real_property(this->Properties, name, ok);
    }

  /// Safely retrieve a named property with an integer value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as an int64_t
  int64_t integer_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::real_property(this->Properties, name, ok);
    }

  /// Safely retrieve a named property with a timestamp value
  //
  // \param name Name of property to retrieve
  // \param ok If specified, this will be set to true or false as the property is found/not found
  // \return Property as a timestamp
  Timestamp timestamp_property(std::string const& name, bool *ok=0) const
    {
      return ::tracktable::timestamp_property(this->Properties, name, ok);
    }

  /// Check whether a property is present
  //
  // \param name Name of desired property
  // \return True if present, false if not
  bool has_property(std::string const& name) const
    {
      return ::tracktable::has_property(this->Properties, name);
    }

  /// INTERNAL METHOD
  //
  // This method is for use by the Python wrappers that can provide
  // their own access to the property map.
  PropertyMap const& __properties() const { return this->Properties; }
  PropertyMap& __non_const_properties() { return this->Properties; }

  /// INTERNAL METHOD
  //
  // This method is for use by the Python wrappers that can provide
  // their own access to the property map.
  void __set_properties(PropertyMap const& props) { this->Properties = props; }

  // Below here are all the methods that make this container usable
  // just like a std::vector.  There's no magic here -- all we do is
  // forward to the Points vector.

  /** Create a new trajectory with pre-specified length
   *
   * Create a new trajectory with n elements.  You may also supply a
   * point that will be copied into each element.
   *
   * @param[in] n             Length of the trajectory
   * @param[in] initial_value Point to be used to fill the new vector
   */

  Trajectory(size_type n, point_type initial_value=point_type())
    : Points(n, initial_value)
    { }

  /** Create a new trajectory from a range of points
   *
   * Create a new trajectory by copying points from [first, last).
   *
   * @param[in] first   Iterator pointing to the first point for the new trajectory
   * @param[in] last    Iterator pointing past the last point for the new trajectory
   */
  template<class InputIterator>
  Trajectory(InputIterator first, InputIterator last)
    : Points(first, last)
    {
      this->compute_current_length(0);
    }

  /** Return the length of the trajectory in points.
   */
  size_type size() const
    {
      return this->Points.size();
    }

  /** Return the maximum number of entries the points array can hold.
   */
  size_type max_size() const
    {
      return this->Points.max_size();
    }

  /** Return the current allocated capacity of the points array.
   */
  size_type capacity() const
    {
      return this->Points.capacity();
    }

  /** Resize the points array to contain exactly the number of entries requested.
   *
   * \param new_size Desired length of the vector
   * \param default_value Value for newly allocated entries
   */
  void resize(size_type new_size, point_type default_value=point_type())
    {
      this->Points.resize(new_size, default_value);
    }

  /** Return whether or not the trajectory is empty.
   */
  bool empty() const
    {
      return this->Points.empty();
    }

  /** Preallocate enough space in the array for the specified number of entries.
   *
   * @param[in]   n   Allocate space for this many points.
   */
  void reserve(size_type n)
    {
      this->Points.reserve(n);
    }

  /** Populate a trajectory from a sequence ot points.
   *
   * @param[in]  iter_begin  Iterator pointing to first point
   * @param[in]  iter_end    Iterator pointing after last point
   */
  template<typename iter_type>
  void assign(iter_type iter_begin, iter_type iter_end)
    {
      this->Points.assign(iter_begin, iter_end);
      this->compute_current_length(0);
    }

  /** Check whether one trajectory is equal to another by comparing all the points.
   *
   * Two trajectories are equal if all of their points are equal.
   *
   * \param other Trajectory for comparison
   */

  bool operator==(const Trajectory& other) const
    {
      return (this->Points == other.Points &&
              this->Properties == other.Properties);
    }

  /** Check whether two trajectories are unequal.
   *
   * \param other Trajectory for comparison
   */

  bool operator!=(const Trajectory& other) const
    {
      return ((*this == other) == false);
    }

  /** Return a given point from the trajectory.
   *
   * Return the requested point from the trajectory.  It is the
   * caller's responsibility to ensure that a valid index has been
   * requested.
   *
   * \param i Index of desired point
   */
  point_type const& operator[](size_type i) const
    {
      return this->Points[i];
    }

  /** Return a mutable reference to a given point in the trajectory.
   *
   * As with the const version of operator[], it is the caller's
   * responsibility to ensure that a valid index has been requested.
   *
   * \note If you change the point's coordinates you are responsible
   * for calling trajectory->compute_current_length(i) to update the
   * points' current_length parameter.
   *
   * \param i Index of desired point
   */
  point_type& operator[](size_type i)
    {
      return this->Points[i];
    }

  /** Append a point to the trajectory.
   *
   * Note that this uses copy semantics rather than move semantics.
   * Since move semantics are part of C++11 we will not use them until
   * we can be reasonable sure that suitable compilers are available
   * in all environments that we care about.
   *
   * \param pt Point to append
   *
   * \note Why do we have this alias?
   */
  void push_back(point_type const& pt)
    {
      this->Points.push_back(pt);
      this->compute_current_length(this->size() - 1);
    }

  /** Retrieve the point at a given index with bounds checking.
   *
   * Retrieve a point.  Unlike operator[], at() does bounds checking
   * and will throw an exception if you ask for a point outside the
   * range [0, num_points).
   *
   * This version of the function will be called if you try to modify
   * the point.  For example:
   *
   * my_trajectory.at(3).set_latitude(15);
   *
   * \note If you modify the point's coordinates, you are responsible
   * for calling trajectory->update_current_length(i).
   *
   * @param[in] i Which point to retrieve
   * \return Mutable reference to the requested point
   */
  point_type& at(size_type i)
    {
      return this->Points.at(i);
    }

  /** Retrieve the point at a given index with bounds checking.
   *
   * Retrieve a point.  Unlike operator[], at() does bounds checking
   * and will throw an exception if you ask for a point outside the
   * range [0, num_points).
   *
   * This version of the function will be called if the compiler can
   * tell that you're not trying to modify the point.  For example:
   *
   * TrajectoryPoint my_point = my_trajectory.at(3);
   *
   * @param[in] i Which point to retrieve
   * \return Immutable reference to the requested point
   */
  point_type const& at(size_type i) const
    {
      return this->Points.at(i);
    }

  /** Remove a point from the trajectory.
   *
   * Delete the point at the specified position (specified by an
   * iterator).  The points after the one deleted will be moved up one
   * spot to fill the gap.
   *
   * \note This operation takes linear time in the number of points in
   * the trajectory.
   *
   * @param[in] position  Iterator pointing at the location to erase.
   */
  iterator erase(iterator position)
    {
      iterator result(this->Points.erase(position));
      if (result != this->end())
        {
        // XXX CHECK THIS
        this->compute_current_length(std::distance(this->begin(), result));
        }
      return result;
    }

  /** Remove a range of points from the trajectory.
   *
   * Delete points from trajectories starting at 'first' and ending at
   * the point just before 'last'.  Points after the deleted range
   * will be moved up to fill the gap.
   *
   * \note This operation takes linear time in the number of points in
   * the trajectory.
   *
   * @param[in] first Iterator pointing at the first point to erase
   * @param[in] last  Iterator pointing to the location after the last point to erase
   *
   */
  iterator erase(iterator first, iterator last)
    {
      iterator result = this->Points.erase(first, last);
      if (result != this->end())
        {
        // XXX CHECK THIS
        this->compute_current_length(std::distance(this->begin(), result));
        }
      return result;
    }

  /** Reset the trajectory to an empty state.
   *
   * This clears out the vector of points.
   */
  void clear()
    {
      this->Points.clear();
    }

  /** Return the first point in the trajectory.
   *
   * \return First point in trajectory (mutable reference)
   *
   * \note TODO: Document behavior if trajectory is empty
   */
  point_type& front()
    {
      return this->Points.front();
    }

  /** Return the (immutable) first point in the trajectory.
   *
   * \return First point in trajectory (immutable reference)
   *
   * \note TODO: Document behavior if trajectory is empty
   */
   point_type const& front() const
    {
      return this->Points.front();
    }

  /** Return the last point in the trajectory.
   *
   * \return Last point in trajectory (mutable reference)
   *
   * \note TODO: Document behavior if trajectory is empty
   */
  point_type& back()
    {
      return this->Points.back();
    }

  /** Return the (immutable) last point in the trajectory.
   *
   * \return Last point in trajectory (immutable reference)
   *
   * \note TODO: Document behavior if trajectory is empty
   */
   point_type const& back() const
    {
      return this->Points.back();
    }

  /** Insert a single element into the trajectory at an arbitrary position.
   *
   * Insert a point into any position in the trajectory.  All points
   * after this location will be moved farther down.
   *
   * @param[in]   position   Location to insert the point
   * @param[in]   value      Point to insert
   */
  iterator insert(iterator position, point_type const& value)
    {
      iterator result(this->Points.insert(position, value));
      this->compute_current_length(std::distance(this->begin(), position));
      return result;
    }

  /** Fill a range in the trajectory.
   *
   * Insert n copes of the point specified as 'value' starting at the
   * specified 'position'.  All points after this location will be
   * moved farther down in the trajectory.
   *
   * @param[in] position  Where to insert the points
   * @param[in] n         How many points to insert
   * @param[in] value     What point to insert
   */
  void insert(iterator position, size_type n, point_type const& value)
    {
      this->Points.insert(position, n, value);
      this->compute_current_length(std::distance(this->begin(), position));
    }

  /** Insert a range of points into the trajectory.
   *
   * Insert all points in the range [first, last) into the trajectory.
   * All points after this location will be moved farther down in the
   * trajectory.
   *
   * @param[in] position   Where to start inserting the points
   * @param[in] first      The first point to insert
   * @param[in] last       The location after the last point to insert
   */
  template<class InputIterator>
  void insert(iterator position, InputIterator first, InputIterator last)
    {
      this->Points.insert(position, first, last);
      this->compute_current_length(std::distance(this->begin(), position));
    }

  void compute_current_length(std::size_t start_index)
    {
      if (start_index >= this->size())
        {
        return;
        }

      for (std::size_t i = start_index; i < this->size(); ++i)
        {
        if (i == 0)
          {
          (*this)[i].set_current_length(0);
          }
        else
          {
          (*this)[i].set_current_length(
            (*this)[i-1].current_length() +
            distance((*this)[i-1], (*this)[i])
            );
          }
        }
    }

protected:
  /// Internal storage for the points in the trajectory
  point_vector_type Points;
  PropertyMap Properties;

private:
  template<class Archive>
  void serialize(Archive& ar, const unsigned int version)
  {
    ar & BOOST_SERIALIZATION_NVP(Points);
    ar & BOOST_SERIALIZATION_NVP(Properties);
  }
  
public:

  /** Return an iterator pointing to the beginning of the trajectory
   *
   * The point underneath this iterator can be changed.
   */
  iterator begin() { return this->Points.begin(); }

  /** Return an iterator pointing to the beginning of the trajectory
   *
   * The point underneath this iterator cannot be changed.
   */
  const_iterator begin() const { return this->Points.begin(); }

  /** Return an iterator pointing beyond the last point in the trajectory
   *
   * The point underneath this iterator, if there is one, can be changed.
   */
  iterator end() { return this->Points.end(); }

  /** Return an iterator pointing beyond the last point in the trajectory
   *
   * The point underneath this iterator, if there is one, cannot be changed.
   */
  const_iterator end() const { return this->Points.end(); }

  
};

} // exit namespace tracktable

namespace tracktable { namespace traits {

template<typename point_type>
struct has_properties< Trajectory<point_type> > : boost::mpl::bool_<true> {};

template<typename point_type>
struct domain<Trajectory<point_type> > : domain<point_type> {};
    
} } // end namespace tracktable::traits

// We get our implementations for trajectory_subset and point_at_time
// from detail headers.

namespace tracktable { namespace algorithms {

template<class PointT>
struct point_at_time< Trajectory< PointT > > : implementations::generic_point_at_time< Trajectory<PointT> >
{ };

template<class PointT>
struct point_at_fraction< Trajectory< PointT > > : implementations::generic_point_at_fraction< Trajectory<PointT> >
{ };

template<class PointT>
struct point_at_length_fraction< Trajectory< PointT > > : implementations::generic_point_at_length_fraction< Trajectory<PointT> >
{ };

template<class PointT>
struct time_at_fraction< Trajectory< PointT > > : implementations::generic_time_at_fraction< Trajectory<PointT> >
{ };

template<class PointT>
struct subset_during_interval< Trajectory<PointT> > : implementations::generic_subset_during_interval< Trajectory<PointT> >
{ };

//Used when comparing a point to a compatible trajectory
template<class PointT, template<class> class TrajectoryT>
struct point_to_trajectory_distance
{
   static double inline apply(PointT const& from, TrajectoryT<PointT> const& to)
   {
       return boost::geometry::distance(from, to);
   }
};

/**
 * Default implementation of end_to_end_distance
 *
 * This uses tracktable::distance to compute the distance between the
 * first and last points of the trajectory.  We will probably never
 * need to override this implementation.
 */
template<class PointT>
struct end_to_end_distance< Trajectory<PointT> >
{
  typedef Trajectory<PointT> trajectory_type;

  static inline double apply(
    trajectory_type const& path
    )
    {
      if (path.size() < 2)
        {
        return 0;
        }
      else
        {
        return ::tracktable::distance(path.front(), path.back());
        }
    }
};

} }

BOOST_GEOMETRY_REGISTER_LINESTRING_TEMPLATED(tracktable::Trajectory)

#endif
