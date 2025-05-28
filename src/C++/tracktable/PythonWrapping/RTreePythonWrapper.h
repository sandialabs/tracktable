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

#ifndef __tracktable_python_rtree_wrapper_h
#define __tracktable_python_rtree_wrapper_h

#include <tracktable/PythonWrapping/GuardedBoostPythonHeaders.h>

// possible hotfix for compile errors in 1.65.0 and 1.65.1
#include <boost/geometry/strategies/strategies.hpp>

#include <tracktable/Analysis/RTree.h>
#include <tracktable/Domain/FeatureVectors.h>

template<typename PointT>
class RTreePythonWrapper
{
public:
  typedef PointT point_type;
  typedef std::pair<point_type, int> indexed_point_type;
  typedef tracktable::RTree<indexed_point_type> rtree_type;

  RTreePythonWrapper() { }
  ~RTreePythonWrapper() { }

  void set_points(boost::python::object const& new_points)
    {
      this->insert_points(new_points);
    }

  std::size_t size() const
    {
      return this->Tree.size();
    }

  // ---------------------------------------------------------------------

  void insert_point(boost::python::object const& new_point)
  {
    int point_id = this->Tree.size();
    indexed_point_type new_indexed_point(
      boost::python::extract<point_type>(new_point),
      point_id
      );

    this->Tree.insert(new_indexed_point);
  }

  // ---------------------------------------------------------------------

  void insert_points(boost::python::object const& new_points)
  {
    boost::python::stl_input_iterator<point_type> point_begin(new_points),
        point_end;
    std::vector<indexed_point_type> indexed_points;
    int point_id = this->Tree.size();
    for (; point_begin != point_end; ++point_begin, ++point_id)
      {
      // Unlike insert_point() above, we don't have to call boost::python::
      // extract() here -- bp::stl_input_iterator<> does that for us.
      //
      // TODO: We could save memory by constructing the indexed points
      // using a transform iterator instead of accumulating a list here.
      indexed_point_type next_point(
        //boost::python::extract<point_type>(*point_begin),
        *point_begin,
        point_id
        );
      indexed_points.push_back(next_point);
      }
    this->Tree.insert(indexed_points.begin(), indexed_points.end());
  }


  // ----------------------------------------------------------------------

  boost::python::object find_points_in_box(boost::python::object const& min_corner,
                                           boost::python::object const& max_corner)
    {
      std::vector<indexed_point_type> points_in_box;
      point_type _min_corner((boost::python::extract<point_type>(min_corner)));
      point_type _max_corner((boost::python::extract<point_type>(max_corner)));

      this->Tree.find_points_inside_box(
        _min_corner, _max_corner,
        std::back_inserter(points_in_box)
        );

      boost::python::list point_indices;
      for (typename std::vector<indexed_point_type>::const_iterator iter = points_in_box.begin();
           iter != points_in_box.end();
           ++iter)
        {
        point_indices.append(iter->second);
        }

      return std::move(point_indices);
    }

  // ----------------------------------------------------------------------

  boost::python::object intersects(boost::python::object const& min_corner,
                                   boost::python::object const& max_corner)
    {
      std::vector<indexed_point_type> points_in_box;
      point_type _min_corner((boost::python::extract<point_type>(min_corner)));
      point_type _max_corner((boost::python::extract<point_type>(max_corner)));

      this->Tree.intersects(
        _min_corner, _max_corner,
        std::back_inserter(points_in_box)
        );

      boost::python::list point_indices;
      for (typename std::vector<indexed_point_type>::const_iterator iter = points_in_box.begin();
           iter != points_in_box.end();
           ++iter)
        {
        point_indices.append(iter->second);
        }

      return std::move(point_indices);
    }

  // ----------------------------------------------------------------------

  boost::python::object find_nearest_neighbors(boost::python::object const& search_point,
                                               std::size_t num_neighbors)
    {
      // The double parens here are present to ward off the "vexing
      // parse" problem.
      point_type query_location((boost::python::extract<point_type>(search_point)));
      indexed_point_type query_point(query_location, -1);
      std::vector<indexed_point_type> neighbors;

      this->Tree.find_nearest_neighbors(query_point, boost::numeric_cast<int>(num_neighbors), std::back_inserter(neighbors));
      boost::python::list result;
      for (typename std::vector<indexed_point_type>::const_iterator neighbor_iter = neighbors.begin();
           neighbor_iter != neighbors.end();
           ++neighbor_iter)
        {
        result.append(neighbor_iter->second);
        }
      return std::move(result);
    }

private:
  rtree_type Tree;
};


#endif
