#ifndef __tracktable_analysis_detail_PairMember_h
#define __tracktable_analysis_detail_PairMember_h

#include <algorithm>


template<typename first_type, typename second_type>
struct GetFirst
{
  typedef std::pair<first_type, second_type> my_pair_type;
  
  GetFirst() { }

  first_type operator()(my_pair_type const& my_pair) const
  {
    return my_pair.first;
  }
};


template<typename first_type, typename second_type>
struct GetSecond
{
  typedef std::pair<first_type, second_type> my_pair_type;
  
  GetSecond() { }

  second_type operator()(my_pair_type const& my_pair) const
  {
    return my_pair.second;
  }
};



#endif
