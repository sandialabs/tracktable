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

#ifndef __tracktable_rw_GenericReader_h
#define __tracktable_rw_GenericReader_h

#include <boost/shared_ptr.hpp>
#include <iterator>
#include <stdexcept>
#include <iostream>

namespace tracktable {

/** Generic reader that exposes an `InputIterator`
 *
 * This reader implements a pattern where new objects can be retrieved
 * one at a time and exposes the resulting sequence as an
 * `InputIterator`. You must implement the following method:
 *
 * `sequence_object_type* next_item()`: Retrieve and return the next
 * item in the sequence (or `NULL` if the sequence has terminated).
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
  /// Instantiate an empty reader
  GenericReader() { }

  /** Copy contructor, create a reader with a copy of another
   *
   * @param [in] other Reader to copy from
   */
  GenericReader(GenericReader const& other)
    : CurrentSequenceObject(other.CurrentSequenceObject)
    , PreviousSequenceObject(other.PreviousSequenceObject)
    { }

  /// Destructor for a generic reader
  virtual ~GenericReader() { }

private:
  typedef boost::shared_ptr<sequence_object_type> sequence_object_ptr;
  sequence_object_ptr CurrentSequenceObject;
  sequence_object_ptr PreviousSequenceObject;

  /** Advance the pointer to the next item in the sequence
   */
  virtual void advance()
    {
      this->PreviousSequenceObject = this->CurrentSequenceObject;
      this->CurrentSequenceObject = sequence_object_ptr(this->next_item());
    }

  /** Check if the sequence is finished
   *
   * @return Boolean indicating completion of sequence
   */
  virtual bool sequence_is_finished() const
    {
      return (this->CurrentSequenceObject == 0);
    }


protected:
    /// Pure virtual function to get the next item in the sequence
    virtual sequence_object_ptr next_item() = 0;

private:
  /** Generic input iterator class
   *
   * Generates a iterator that can traverse the given parent
   * generic reader sequence
   */
  class GenericInputIterator
  {
  public:
    using iterator_category = std::input_iterator_tag;
    using value_type        = sequence_object_type;
    using difference_type   = std::ptrdiff_t;
    // This looks wrong: we expect reference to be 'value_type &' without
    // the const.  If we do that, though, we get a compilation error in
    // Examples/FilterTime/filter_by_time.cpp where something deep in
    // Boost tries to bind a const value to a non-const reference.
    //
    // That's an issue to investigate another time.
    using reference         = value_type const &;
    using const_reference   = value_type const &;
    using pointer           = value_type *;
    using const_pointer     = const value_type *;

    /// Instantiate an empty input iterator
    GenericInputIterator()
      : Parent(0)
      { }

    /// Copy contructor, create a input iterator with a copy of a parent `GenericReader`
    GenericInputIterator(GenericReader* parent)
      : Parent(parent)
      {
        if (this->Parent)
          {
          this->CurrentSequenceObject = this->Parent->CurrentSequenceObject;
          }
      }

    /// Copy contructor, create a input iterator with a copy of another
    GenericInputIterator(GenericInputIterator const& other)
      : CurrentSequenceObject(other.CurrentSequenceObject)
      , Parent(other.Parent)
      { }

    /// Destructor for a generic input iterator
    virtual ~GenericInputIterator() { }

    GenericInputIterator& operator=(GenericInputIterator const& other)
      {
        this->CurrentSequenceObject = other.CurrentSequenceObject;
        this->Parent = other.Parent;
        return *this;
      }

    /** Check whether one iterator is equal to another by comparing all the items.
     *
     * Two items are equal if all of their points are equal.
     *
     * @param [in] other Iterator for comparison
     * @return Boolean indicating equivalency
     */
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
          // The sources are not equal. The iterators cannot be
          // equal.
          return false;
          }
      }

    /** Check whether two iterators are unequal.
     *
     * @param [in] other Iterator for comparison
     * @return Boolean indicating equivalency
     */
    bool operator!=(GenericInputIterator const& other) const
      {
        return !(*this == other);
      }

    /** Multiply an iterator.
     *
     * @return Result of the multiplication
     */
    reference operator*()
      {
        return *this->CurrentSequenceObject;
      }

    /** Multiply an iterator.
     *
     * @return Result of the multiplication
     */
    const_reference operator*() const
      {
        return *this->CurrentSequenceObject;
      }

    /** Get the current iterator object.
     *
     * @return Current iterator
     */
    pointer operator->()
      {
        return this->CurrentSequenceObject;
      }

    /** Get the current iterator object.
     *
     * @return Current iterator
     */
    const_pointer operator->() const
      {
        return this->CurrentSequenceObject;
      }

    /** Advance the iterator to the next position in the sequence.
     *
     * @return Pointer to the next iterator in the sequence
     * @throw std::runtime_error If iterator is at the end of the sequence
     */
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

    /** Advance the iterator to the next position in the sequence.
     *
     * @return Pointer to the next iterator in the sequence
     * @throw std::runtime_error If iterator is at the end of the sequence
     */
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
   * @note
   *    We assume that `begin()` will usually be called just once
   *    in order to iterate over the entire sequence from beginning to
   *    end. Since this is an `InputIterator`, we do not guarantee that
   *    calling `begin()` a second time will yield a new iterator that
   *    will reproduce the sequence. (In fact, we can almost guarantee
   *    the opposite.)
   *
   * @return Iterator pointing to current sequence
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
   * @return Iterator pointing to end of sequence
   */
  GenericInputIterator end()
    {
      return GenericInputIterator(0);
    }

};

} // close namespace tracktable

#endif
