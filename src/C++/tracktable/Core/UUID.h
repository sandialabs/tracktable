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


#ifndef __tracktable_UUID_h
#define __tracktable_UUID_h

#include <memory>

#include <tracktable/Core/TracktableCoreWindowsHeader.h>
#include <tracktable/Core/PlatformDetect.h>

#define BOOST_ALLOW_DEPRECATED_HEADERS
#include <boost/enable_shared_from_this.hpp>
#include <boost/uuid/uuid.hpp>
#include <boost/uuid/uuid_io.hpp>
#include <boost/uuid/random_generator.hpp>
#include <boost/random/mersenne_twister.hpp>

#ifdef TT_WINDOWS
  #include <boost/thread.hpp>
#else
  #include <pthread.h>
#endif

#undef BOOST_ALLOW_DEPRECATED_HEADERS

namespace tracktable
{

/** A convenience typedef for uuids in tracktable */
typedef boost::uuids::uuid uuid_type;

/**
 * Serves as a common base for all generators of random uuids
 *
 * With a common base, the global uuid generator may be changed to different
 * implementations, including different random number generation mechanisms.
 *
 * This class is necessary because the boost random uuid generators do not
 * have any common hierarchy. This class provides a common hierarchy around
 * the `generate()` method.
 *
 * This base class also provides a basic mutex to allow threadsafe generation.
 */
class TRACKTABLE_CORE_EXPORT UUIDGenerator
{
public:
  /** A convenience typedef for a smart pointer to a generator */
  typedef boost::shared_ptr<UUIDGenerator> pointer;

  /// Instantiate an uninitialized UUID generator
  UUIDGenerator() {
    #ifdef TT_WINDOWS
      this->mutex = new boost::mutex();
    #else // not defined TT_WINDOWS
      this->mutex_initialized = false;
      if (pthread_mutex_init(&(this->mutex), NULL) == 0)
        this->mutex_initialized = true;
    #endif // ifdef TT_WINDOWS
  }

  /// Destructor for the UUID Generator
  virtual ~UUIDGenerator() {
    #ifdef TT_WINDOWS
      delete this->mutex;
    #endif // ifdef TT_WINDOWS
  }

  /** This pure virtual method provides a common method for generating uuids */
  virtual uuid_type generate_uuid() = 0;

protected:

  /// Lock the mutex for generator
  inline void lock_mutex() {
    #ifdef TT_WINDOWS
    this->mutex->lock();
    #else // not defined TT_WINDOWS
    if (this->mutex_initialized)
      pthread_mutex_lock(&(this->mutex));
    #endif // ifdef TT_WINDOWS
  }

  /// Unlock the mutex for generator
  inline void unlock_mutex() {
    #ifdef TT_WINDOWS
    this->mutex->unlock();
    #else // not defined TT_WINDOWS
    if (this->mutex_initialized)
      pthread_mutex_unlock(&(this->mutex));
    #endif // ifdef TT_WINDOWS
  }

private:
  /** Mutexes used to ensure `generate_uuid()` is threadsafe */
  #ifdef TT_WINDOWS
    boost::mutex* mutex;
  #else // not defined TT_WINDOWS
    pthread_mutex_t mutex;
    bool mutex_initialized;
  #endif // ifdef TT_WINDOWS
};

/** Wraps a boost uuid random generator to act as a RandomUUIDGenerator
 *
 * The boost random number generator is templated to use various random
 * number generation mechanisms. The default boost implementation is the
 * mt19937 which is also the default template type of this class.
 *
 * However, any random number generator suitable for the boost classes can
 * be used with this thin wrapper template.
 *
 * To create an instance of this class, use the various static `create()` methods
 * that mimic the available boost random generator constructors.
 */
template <typename UniformRandomNumberGenerator=boost::random::mt19937>
class TRACKTABLE_CORE_EXPORT BoostRandomUUIDGenerator : public UUIDGenerator
{
private:
  /** Instantiate a Boost random UUID generator
   * Use BoostRandomUUIDGenerator<URNG type>::create()
   */
  BoostRandomUUIDGenerator()
  {
    this->_generator = new random_generator_type();
  }

  /** Instantiate a Boost random UUID generator
   *  Use BoostRandomUUIDGenerator<URNG type>::create(URNG type &)
   */
  BoostRandomUUIDGenerator ( UniformRandomNumberGenerator& gen )
  {
    this->_generator = new random_generator_type(gen);
  }

  /** Instantiate a Boost random UUID generator
   * Use BoostRandomUUIDGenerator<URNG type>::create(URNG type *)
   */
  BoostRandomUUIDGenerator ( UniformRandomNumberGenerator* pGen )
  {
    this->_generator = new random_generator_type(pGen);
  }

public:
  typedef boost::uuids::basic_random_generator<UniformRandomNumberGenerator> random_generator_type;

  /// Destructor for the Boost Random UUID Generator
  virtual ~BoostRandomUUIDGenerator() {
    delete _generator;
  }

  /** Static method to create an instance using the default uniform random number generator type
   *
   * Example setting a new default uuid generator with mt19937:
   *
   * @code
   *
   * ::tracktable::set_automatic_uuid_generator(::tracktable::BoostRandomUUIDGenerator<boost::random::mt19937>::create());
   *
   * @endcode
   *
   * @return Pointer to the new Boost random UUID generator
   */
  static UUIDGenerator::pointer create() {
    return UUIDGenerator::pointer(new BoostRandomUUIDGenerator());
  }

  /** Static method to create an instance using a supplied uniform random number generator type
   *
   * @return Pointer to the new Boost random UUID generator
  */
  static UUIDGenerator::pointer create( UniformRandomNumberGenerator& gen ) {
    return UUIDGenerator::pointer(new BoostRandomUUIDGenerator(gen));
  }

  /** Static method to create an instance using a supplied uniform random number generator type
   *
   * @return Pointer to the new Boost random UUID generator
  */
  static UUIDGenerator::pointer create( UniformRandomNumberGenerator* pGen ) {
    return UUIDGenerator::pointer(new BoostRandomUUIDGenerator(pGen));
  }

  /** Generate a UUID for the given generator
   *
   * @return The generated UUID
   */
  inline
  uuid_type generate_uuid()
  {
    this->lock_mutex();
    uuid_type new_uuid = this->_generator->operator()();
    this->unlock_mutex();
    return new_uuid;
  }

private:
  random_generator_type* _generator;

};

/** Wraps a boost uuid pure generator to act as a RandomUUIDGenerator
 *
 * The boost uuid pure generator is a lighter weight generator with less
 * entropy, but as stated in the boost documentation it "will satisfy the
 * majority of use cases."
 */
class TRACKTABLE_CORE_EXPORT BoostRandomUUIDGeneratorPure : public UUIDGenerator
{
private:
  /** Instantiate a boost random uuid pure generator
   */
  BoostRandomUUIDGeneratorPure() {
    _generator = new random_generator_type();
  }

public:
  typedef boost::uuids::random_generator random_generator_type;

  /** Static method to create an instance using the default uniform random number generator type
   *
   * Example setting a new default uuid generator:
   *
   * @code
   *
   * ::tracktable::set_automatic_uuid_generator(::tracktable::BoostRandomUUIDGeneratorPure::create());
   *
   * @endcode
   *
   * @return Pointer to the new pure Boost random UUID generator
   */
  static UUIDGenerator::pointer create() {
    return UUIDGenerator::pointer(new BoostRandomUUIDGeneratorPure());
  }

  /// Destructor for the UUID Generator
  virtual ~BoostRandomUUIDGeneratorPure() {
    delete _generator;
  }

  /** Generate a UUID for the given generator
   *
   * @return The generated UUID
   */
  inline
  uuid_type generate_uuid()
  {
    this->lock_mutex();
    uuid_type new_uuid = this->_generator->operator()();
    this->unlock_mutex();
    return new_uuid;
  }

private:
  random_generator_type* _generator;

};

/** Get the current global automatic uuid generator.
 *
 * A global automatic uuid generator is used to avoid the cost of continuously instantiating
 * a new generator, which could have a significant impact
 *
 * This could be used to generate uuids using the same mechanisms as the current
 * global generator.
 */
TRACKTABLE_CORE_EXPORT UUIDGenerator::pointer automatic_uuid_generator();

/** Set the global automatic uuid generator
 *
 * Allows the global uuid generator to be changed from the default generator
 * to any generator implementing the `generate()` method of `UUIDGenerator`.
 *
 * The default generator is a boost random uuid generator using mt19937 for
 * random number generation.
 *
 * The `BoostRandomUUIDGenerator` template can be used to quickly create
 * generators employing other random number generation approaches.
 */
TRACKTABLE_CORE_EXPORT void set_automatic_uuid_generator ( UUIDGenerator::pointer new_random_generator );

} // namespace tracktable

#endif // __tracktable_UUID_h
