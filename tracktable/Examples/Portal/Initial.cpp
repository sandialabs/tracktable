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

#include "Initial.h"
#include <boost/geometry/algorithms/intersects.hpp> 

void MakeInitialPairs(Trajectories &trajectories, PP &Full,
 Pair_heap &pairs, unsigned int thresh)
{

  // Initialize the simulation by making one big portal out of the Full
  // and then decomposing it.

  for (Ts_itr itr = trajectories.begin(); itr != trajectories.end(); ++itr)
    if (boost::geometry::intersects(*itr,*Full))
      AddTrajectory(Full,&(*itr));

  // Note: The Full map defined by the coordinates above has an aspect ratio
  // of 12 by 5.  Using a different aliquot than that in the command below
  // will result in non-square portals.  Not that there is anything wrong
  // with that.

  SubDividePortal(Full,12,5);

  // Now initialize pair list with all of the children...

  for (pp_itr itr = Full->children.begin(); itr != Full->children.end(); ++itr)
    for (pp_itr itr2 = itr; ++itr2 != Full->children.end(); /* */)
      MakeNewPair(pairs,*itr,*itr2);

  return;
}

void MakeInitialSingles(Trajectories &trajectories, PP &Full,
 my_pq<PP,std::vector<PP>,PPCompare> &portals, const unsigned int &x_div, 
 const unsigned int &y_div, unsigned int thresh)
{

  // Initialize the simulation by making one big portal out of the Full
  // and then decomposing it.

  for (Ts_itr itr = trajectories.begin(); itr != trajectories.end(); ++itr)
    if (boost::geometry::intersects(*itr,*Full))
      Full->trajectories.insert(&(*itr));

  // Note: The Full map defined by the coordinates above has an aspect ratio
  // of 12 by 5.  Using a different aliquot than that in the command below
  // will result in non-square portals.  Not that there is anything wrong
  // with that.

  SubDividePortal(Full,x_div,y_div);

  // Now initialize with all of the children...

  for (pp_itr itr = Full->children.begin(); itr != Full->children.end(); ++itr)
    portals.push(*itr);

  return;
}
