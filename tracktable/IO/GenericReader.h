/*
 * Copyright (c) 2014-2017 National Technology and Engineering
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

#ifndef __tracktable_io_GenericReader_h
#define __tracktable_io_GenericReader_h

#include <boost/shared_ptr.hpp>
#include <iterator>
#include <stdexcept>
#include <iostream>

namespace tracktable { 

/** Generic reader that exposes an InputIterator
 *
 * This reader implements a pattern where new objects can be retrieved
 * one at a time and exposes the resulting sequence as an
 * InputIterator.  You must implement the following method:
 *
 * sequence_object_type* next_item(): Retrieve and return the next
 * item in the sequence (or NULL if the sequence has terminated).
 *
 * The template takes care of the mechanics of exposing the objects
 * and maintaining references for as long as necessary.
 *
 * You must also implement whatever machinery you need to set up the
 * input source to the reader.
 */

template<typename sequence_object_type>
class GenericReader
{
public:
  GenericReader() { }
  GenericReader(GenericReader const& other)
    : CurrentSequenceObject(other.CurrentSequenceObject)
    , PreviousSequenceObject(other.PreviousSequenceObject)
    { }
  virtual ~GenericReader() { }

private:
  typedef boost::shared_ptr<sequence_object_type> sequence_object_ptr;
  sequence_object_ptr CurrentSequenceObject;
  sequence_object_ptr PreviousSequenceObject;

  virtual void advance()
    {
      this->PreviousSequenceObject = this->CurrentSequenceObject;
      this->CurrentSequenceObject = sequence_object_ptr(this->next_item());
    }

  virtual bool sequence_is_finished() const
    {
      return (this->CurrentSequenceObject == 0);
    }


protected:
    virtual sequence_object_ptr next_item() = 0;

private:
  class GenericInputIterator : public std::iterator<
  std::input_iterator_tag,
  sequence_object_type
  >

  {
  public:
    typedef std::ptrdiff_t          difference_type;
    typedef sequence_object_type    value_type;
    typedef value_type const&             reference;
    typedef value_type const&       const_reference;
    typedef value_type const*             pointer;
    typedef value_type const*       const_pointer;
    typedef std::input_iterator_tag iterator_category;

    GenericInputIterator()
      : Parent(0)
      { }

    GenericInputIterator(GenericReader* parent)
      : Parent(parent)
      {
        if (this->Parent)
          {
          this->CurrentSequenceObject = this->Parent->CurrentSequenceObject;
          }
      }

    GenericInputIterator(GenericInputIterator const& other)
      : CurrentSequenceObject(other.CurrentSequenceObject)
      , Parent(other.Parent)
      { }

    virtual ~GenericInputIterator() { }

    GenericInputIterator& operator=(GenericInputIterator const& other)
      {
        this->CurrentSequenceObject = other.CurrentSequenceObject;
        this->Parent = other.Parent;
        return *this;
      }

    bool operator==(GenericInputIterator const& other) const
      {
        if (this->Parent == other.Parent)
          {
          if (this->Parent == 0)
            {
            // Both iterators are past-the-end and therefore equal.
            return true;
            }
          else
            {
            // Neither iterator is past the end.
            return (this->CurrentSequenceObject == other.CurrentSequenceObject);
            }
          }
        else
          {
          // The sources are not equal.  The iterators cannot be
          // equal.
          return false;
          }
      }

    bool operator!=(GenericInputIterator const& other) const
      {
        return !(*this == other);
      }

    reference operator*()
      {
        return *this->CurrentSequenceObject;
      }

    const_reference operator*() const
      {
        return *this->CurrentSequenceObject;
      }

    pointer operator->()
      {
        return this->CurrentSequenceObject;
      }

    const_pointer operator->() const
      {
        return this->CurrentSequenceObject;
      }

    GenericInputIterator& operator++()
      {
        if (this->Parent == 0)
          {
          throw std::runtime_error("Cannot advance iterator past end");
          }
        else
          {
          if (this->Parent->sequence_is_finished())
            {
            // it might already know
            this->Parent = 0;
            }
          else
            {
            this->Parent->advance();
            if (this->Parent->sequence_is_finished())
              {
              // it might have just found out
              this->Parent = 0;
              }
            else
              {
              this->CurrentSequenceObject = this->Parent->CurrentSequenceObject;
              }
            }
          }
        return *this;
      }

    GenericInputIterator operator++(int)
      {
        GenericInputIterator old(*this);
        this->operator++();
        return old;
      }

  private:
    typedef boost::shared_ptr<sequence_object_type> sequence_object_ptr;
    sequence_object_ptr CurrentSequenceObject;
    GenericReader*      Parent;

  }; // end iterator class

public:
  typedef GenericInputIterator iterator;

  /** Get an iterator pointing to the current sequence
   *
   * NOTE: We assume that begin() will usually be called just once
   * in order to iterate over the entire sequence from beginning to
   * end.  Since this is an InputIterator, we do not guarantee that
   * calling begin() a second time will yield a new iterator that
   * will reproduce the sequence.  (In fact, we can almost guarantee
   * the opposite.)
   */

  GenericInputIterator begin()
    {
      this->advance();
      if (!this->sequence_is_finished())
        {
        return GenericInputIterator(this);
        }
      else
        {
        return GenericInputIterator(0);
        }
    }

  /** Get an iterator pointing past the end of the sequence
   *
   */
  GenericInputIterator end()
    {
      return GenericInputIterator(0);
    }

};

} // close namespace tracktable

#endif
