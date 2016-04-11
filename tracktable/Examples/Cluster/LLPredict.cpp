/*
 * Copyright (c) 2015, Sandia Corporation.  All rights
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

#include "Predict.h"
#include "KmlOut.h"
#include "ConvexHull.h"
#include "my_rtree.h"
#include "Mem.h"
#include <numeric>
#include <boost/bind.hpp>

void LLPredict(Trajectories &trajectories, std::vector<my_data> &features, 
 std::vector<my_data> &to_be_predicted, unsigned int sample_size)
{
  // Use the rtree from "my_rtree.h", and the value typedef.  The value
  // typedef basically contains the features, a value reserved (not used) for
  // doing work on, and an id number that corresponds to the feature.

  my_rtree rtree;
  std::vector<value> data;

  // Build the feature vector/id number combo for the rtree.  There is an
  // unused value set to 0 that might be used in the future.

  for (unsigned int i = 0; i < features.size(); ++i) {
    data.push_back(&(features[i]));
  }

  std::cout << "Made data vector" << std::endl;
  print_mem_usage();
  // Insert the values into the rtree;

  rtree.insert(data.begin(),data.end());
  std::cout << "Inserted into rtree" << std::endl;
  print_mem_usage();

  // Okay.  Here is where the work is done.  Go through each flight and 
  // find all of its neighbors to predict where it will land.

  std::vector<double> dists;
  std::vector<my_data>::iterator orig = to_be_predicted.begin();
  for (; orig != to_be_predicted.end(); ++orig) {
	  std::vector<value> result_n;

    // Note we are getting more results than sample_size.  This is because
    // we will throw out the hits that corresponds to the trajectory itself.
    // It would be cheating to use that for prediction. 

    my_rtree::const_query_iterator it =
     rtree.qbegin(boost::geometry::index::nearest(orig->Point,sample_size+10));

    for (; (it != rtree.qend()) && (result_n.size() < sample_size); ++it ) {
      if ((*it)->index != orig->index)
        result_n.push_back(*it);
    }
//	  rtree.query(boost::geometry::index::nearest(orig->Point,sample_size+1),
//	   std::back_inserter(result_n));
	
    // typedef for storing the destination/weight pair.
    typedef std::pair<point_ll,double> w_pair;
    std::vector<w_pair> weights;
//    Trajectories results;

    point_ll dest = orig->index->back();	
	  double total_weight = 0.0;
	
    // Take the results from the rtree query, and then build a vector that
    // has the resulting flights.  In addition, build a table of weights for
    // each potential destination (via a map) using what is essentially a
    // 1/d^2 weight.  The d^2 term comes from the "comparable_distance"
    // function.

	  std::vector<value>::iterator itr = result_n.begin();
	  for (; itr != result_n.end(); ++itr) {
      value found = *itr;
	    double weight = 1.0/(0.01 + boost::geometry::comparable_distance(
       orig->Point,found->Point));
	    total_weight += weight;
//      results.push_back(*(found->index));
	    weights.push_back(std::make_pair(found->index->back(),weight));
	  }

    // Do the actual sorting.  Have to specify using the second element since
    // sort will use the first element (destination) by default.

    std::sort(weights.begin(),weights.end(),
     boost::bind(&w_pair::second,_1) > boost::bind(&w_pair::second,_2));

    // Code to find the nearest hit.  It shouldn't be this ugly.  

    std::vector<w_pair>::iterator small = 
     std::min_element(weights.begin(),weights.end(),
     boost::bind(std::less<double>(),
     boost::bind(tracktable::algorithms::distance<point_ll>::apply,
      dest,boost::bind(&w_pair::first,_1)),
     boost::bind(tracktable::algorithms::distance<point_ll>::apply,
      dest,boost::bind(&w_pair::first,_2))));

    point_ll guess = GetWeightedLatLonSlerp(weights);

    dists.push_back(boost::geometry::distance(dest,guess));

    std::cout << boost::geometry::distance(dest,small->first) << "\t";
    std::cout << dists.back() << std::endl;

/*    if ((pos == sorted.size()) && (total_weight > 0)) {
      std::string s1 = "output/" + orig->index->object_id() + "cand.kml";
      writeKmlTrajectories(results,s1.c_str());
      std::string s = "output/" + orig->index->object_id() + ".kml";
      std::ofstream outfile(s.c_str());
      writeKmlTrajectory(*(orig->index),outfile,"FFFFFFFF",3.0);
      outfile.clear();
      outfile.close();
    } */
  }

  return;
}
