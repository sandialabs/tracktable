#ifndef PointGenerator_h
#define PointGenerator_h

#include <tracktable/Core/Timestamp.h>
#include <tracktable/Domain/Terrestrial.h>

#include <algorithm>
#include <cmath>
#include <stdexcept>

#define PRINT(X) std::cout << #X ": " << (X) << std::endl;

namespace tracktable {

/** Point Generator for terrestrial points
 * The is a basic point generator used as a base for all others.
 * It will just keep incrementing points for a stationary object forever.
 * Each call to next will increment the timestamp of the returned point by the set interval
 */
template <typename Point_T>
class PointGenerator {
 public:
  using PointT = Point_T;
  using DurationT = tracktable::Duration;

  /** Instantiate an empty point generator
   */
  PointGenerator() : PointGenerator(PointT()) {}

  /** Sets the initial point to `_position`
   *
   * @param [in] _position Initial point to use, including all metadata
   */
  PointGenerator(const PointT& _position) : PointGenerator(_position, tracktable::seconds(60)) {}

  /** Sets the initial point to `_position`, and the time interval to `_interval`
   *
   * @param [in] _position Initial point to use
   * @param [in] _interval Interval to increase timestamp by
   */
  PointGenerator(const PointT& _position, const DurationT& _interval)
      : position(_position), interval(_interval) {}

  /** Updates position and returns a point
   *
   * @return new point
   */
  virtual PointT next() {
    if (count++ != 0) {
      position.set_timestamp(position.timestamp() + interval);
    }
    return position;
  }

  /** Retrieve the interval of the points in the generator
   *
   * @return Interval of the points
   */
  DurationT getInterval() const { return interval; }

  /** Set the interval of the points
   */
  void setInterval(const DurationT& _interval) { interval = _interval; }

  /** Retrieve the object ID at the given position
   *
   * @return ID of the object
   */
  std::string getObjectId() const { return position.object_id(); }

  /** Set the object at a given position
   */
  void setObjectId(const std::string& _id) { position.set_object_id(_id); }

 protected:
  DurationT interval;  ///< Update Interval
  size_t count = 0;    ///< Count of points generated
  PointT position;     ///< Last point generated
};

/** Generates points based on a heading and speed
 * each point is calculated based on the last point
 */
class ConstantSpeedPointGenerator
    : public PointGenerator<tracktable::domain::terrestrial::trajectory_type::point_type> {
 protected:
  using ThisType = ConstantSpeedPointGenerator;
  using BaseType = PointGenerator<tracktable::domain::terrestrial::trajectory_type::point_type>;

 public:
  using DurationT = BaseType::DurationT;
  using PointT = BaseType::PointT;

  /**
   * @brief Calculates a new lat/lon based on a point, distance, and direction
   * method is trig based, centered around transforms back and forth to cartesian
   *
   * @param [in] _origin   The (lon, lat) starting point
   * @param [in] _distance The distance, in meters, traveled
   * @param [in] _heading  The compass heading to travel in degrees
   * @return PointT   The final destination
   */
  static PointT reckon(PointT _origin, double _distance, double _heading) {
    using tracktable::conversions::degrees;
    using tracktable::conversions::radians;
    constexpr auto R = tracktable::conversions::constants::EARTH_RADIUS_IN_KM;
    // TODO: convert math for elipsoid??

    long double h = radians(_heading);

    long double latR = radians(_origin.latitude());   // rad
    long double lonR = radians(_origin.longitude());  // rad
    auto d = (long double)(_distance / 1000.0);       // km
    auto dR = d / R;                                  // radial distance
    auto cdR = std::cos(dR);
    auto sdR = std::sin(dR);
    auto slatR = std::sin(latR);

    auto lat2 = std::asin(slatR * cdR + std::cos(latR) * sdR * std::cos(h));
    auto lon2 = lonR + std::atan2(std::sin(h) * sdR * std::cos(latR), cdR - slatR * std::sin(lat2));

    auto lon2d = degrees(lon2);
    auto lat2d = degrees(lat2);
    PointT result(_origin);
    result.set_latitude(lat2d);
    result.set_longitude(lon2d);
    return result;
  }

  /**
   * @brief Calculates a new lat/lon based on an initial point, speed, heading, and duration.
   * uses spherical coordinates and angular velocities.
   *
   * @param [in] _origin Start location (lon, lat)
   * @param [in] _speed  Speed traveled (meters/second)
   * @param [in] _heading Compass heading to travel (degrees)
   * @param [in] _dt  Duration of travel
   * @return PointT resulting point
   */
  static PointT reckon2(const PointT& _origin, const double& _speed,
                        const double& _heading, const DurationT& _dt) {
    using tracktable::conversions::degrees;
    using tracktable::conversions::radians;
    constexpr auto R = tracktable::conversions::constants::EARTH_RADIUS_IN_KM;
    auto speed = _speed / 1000.0;                 // m/s -> km/s
    auto heading = radians(-(_heading - 90.0));   // rad
    auto dt = _dt.total_milliseconds() / 1000.0;  // seconds
    auto sLo = std::cos(heading) * speed;         // lon tangental speed
    auto sLa = std::sin(heading) * speed;         // lat tangental speed
    auto wLo = sLo / R;                           // lon radial speed
    auto wLa = sLa / R;                           // lat radial speed

    PointT result(_origin);
    auto lat = _origin.latitude() + degrees(wLa * dt);
    auto lon = _origin.longitude() + degrees(wLo * dt);
    if (lon > 180.0) {
      lon -= 360;
    } else if (lon < -180.0) {
      lon += 360;
    }
    if (lat > 90.0) {
      lat = 180 - lat;
    } else if (lat < -90.0) {
      lat = -180 + lat;
    }
    // TODO: address need for speed reversal if lat crosses over?
    result.set_latitude(lat);
    result.set_longitude(lon);
    return result;
  }

  /** Instantiate an empty constant speed point generator
   */
  ConstantSpeedPointGenerator() : BaseType() {}

  /** Sets the initial point to `_position`
   * @param [in] _position Initial point to use, including all metadata
   */
  ConstantSpeedPointGenerator(const PointT& _position) : BaseType(_position) {}

  /** Sets the initial point to `_position`, and the time interval to `_interval`
   *
   * @param [in] _position Initial point to use
   * @param [in] _interval Interval to increase timestamp by
   */
  ConstantSpeedPointGenerator(const PointT& _position, const DurationT& _interval)
      : BaseType(_position, _interval) {}

  /** Sets the initial speed to `_speed`, and the heading to `_heading`
   *
   * @param [in] _position Initial point to use
   * @param [in] _interval Interval to increase timestamp by
   * @param [in] _speed Initial speed to use
   * @param [in] _heading Initial heading to use
   */
  ConstantSpeedPointGenerator(const PointT& _position, const DurationT& _interval, const double& _speed,
                              const double& _heading)
      : BaseType(_position, _interval), speed(_speed), heading(_heading) {}

  /** Updates position and returns a point
   *
   * @return new point
   */
  PointT next() override {
    BaseType::next();
    if (count > 1) {
      auto d = speed * double(interval.total_seconds());
      // position = reckon(position, d, heading);
      position = reckon2(position, speed, heading, interval);
    }
    return position;
  }

  /** Retrieve the spped of the points in the generator
   *
   * @return Speed of the points
   */
  double getSpeed() const { return speed; }

  /** Set the speed of the points
   */
  void setSpeed(const double& _speed) { speed = _speed; }

  /** Retrieve the heading of the points in the generator
   *
   * @return Heading of the points
   */
  double getHeading() const { return heading; }

  /** Set the heading of the points
   */
  void setHeading(const double& _heading) { heading = _heading; }

 private:
  double speed = 44.704;  ///< ~100Mi/h in m/s
  double heading = 0.0;   ///< North
};

/** Generates points based on a turn rate
 * each point is calculated based on the last point
 */
class CircularPointGenerator : public ConstantSpeedPointGenerator {
 protected:
  using ThisType = CircularPointGenerator;
  using BaseType = ConstantSpeedPointGenerator;

 public:
  using DurationT = BaseType::DurationT;
  using PointT = BaseType::PointT;

 public:

   /** Instantiate an empty circular point generator
   */
  CircularPointGenerator() : BaseType() {}

  /** Sets the initial point to `_position`
   * @param [in] _position Initial point to use, including all metadata
   */
  CircularPointGenerator(const PointT& _position) : BaseType(_position) {}

  /** Sets the initial point to `_position`, and the time interval to `_interval`
   *
   * @param [in] _position Initial point to use
   * @param [in] _interval Interval to increase timestamp by
   */
  CircularPointGenerator(const PointT& _position, const DurationT& _interval)
      : BaseType(_position, _interval) {}

  /** Sets the initial speed to `_speed`, and the heading to `_heading`
   *
   * @param [in] _position Initial point to use
   * @param [in] _interval Interval to increase timestamp by
   * @param [in] _speed Initial speed to use
   * @param [in] _heading Initial heading to use
   */
  CircularPointGenerator(const PointT& _position, const DurationT& _interval, const double& _speed,
                         const double& _heading)
      : BaseType(_position, _interval, _speed, _heading) {}

  /** Sets the initial turn rate to `_turnRate`
   *
   * @param [in] _position Initial point to use
   * @param [in] _interval Interval to increase timestamp by
   * @param [in] _speed Initial speed to use
   * @param [in] _heading Initial heading to use
   * @param [in] _turnRate Initial turn rate to use
   */
  CircularPointGenerator(const PointT& _position, const DurationT& _interval, const double& _speed,
                         const double& _heading, const double& _turnRate)
      : BaseType(_position, _interval, _speed, _heading), turnRate(_turnRate) {}

  /** Updates position and returns a point
   *
   * @return new point
   */
  PointT next() override {
    // flies straight and adjust heading at next point
    BaseType::next();
    if (count > 1) {  // Base will already increment it
      auto h = getHeading();
      h += turnRate * (interval.total_milliseconds() / 1000.0);
      if (h >= 360.0) {
        h -= 360;
      }
      setHeading(h);
    }
    return position;
  }

  /** Retrieve the turn rate of the points in the generator
   *
   * @return Turn rate of the points
   */
  double getTurnRate() const { return turnRate; }

  /** Set the heading of the points
   */
  void setTurnRate(const double& _rate) { turnRate = _rate; }

 private:
  double turnRate = .6;  ///< deg/s == circle per 10 min
};

/**
 * Generator for generating boxes, snakes, or anything else on a grid
 *
 * Take a length vector that tell how long each side is. if the length is
 * negative, then it will turn left afterwards, otherwise it will turn right
 *
 * Use a length vector of `{10}` to create a box with 10 points on each side.
 * Use a length vector of `{10,2,-10,-2}` to create a mapping flight
 *
 */
class GridPointGenerator : public ConstantSpeedPointGenerator {
 protected:
  using ThisType = GridPointGenerator;
  using BaseType = ConstantSpeedPointGenerator;

 public:
  using DurationT = BaseType::DurationT;
  using PointT = BaseType::PointT;

 public:

  /** Instantiate an empty grid point generator
   */
  GridPointGenerator() : BaseType() {}

 /** Sets the initial point to `_position`
   * @param [in] _position Initial point to use, including all metadata
   */
  GridPointGenerator(const PointT& _position) : BaseType(_position) {}

  /** Sets the initial point to `_position`, and the time interval to `_interval`
   *
   * @param [in] _position Initial point to use
   * @param [in] _interval Interval to increase timestamp by
   */
  GridPointGenerator(const PointT& _position, const DurationT& _interval) : BaseType(_position, _interval) {}

  /** Sets the initial speed to `_speed`, and the heading to `_heading`
   *
   * @param [in] _position Initial point to use
   * @param [in] _interval Interval to increase timestamp by
   * @param [in] _speed Initial speed to use
   * @param [in] _heading Initial heading to use
   */
  GridPointGenerator(const PointT& _position, const DurationT& _interval, const double& _speed,
                     const double& _heading)
      : BaseType(_position, _interval, _speed, _heading) {}

  /** Sets the initial lengths rate to `_lengths`
   *
   * @param [in] _position Initial point to use
   * @param [in] _interval Interval to increase timestamp by
   * @param [in] _speed Initial speed to use
   * @param [in] _heading Initial heading to use
   * @param [in] _lengths Initial length to use
   */
  GridPointGenerator(const PointT& _position, const DurationT& _interval, const double& _speed,
                     const double& _heading, std::vector<int> _lengths)
      : BaseType(_position, _interval, _speed, _heading), lengths(_lengths) {}

  /** Updates position and returns the new position
   *
   * @return new position
   */
  PointT next() override {
    // flies straight and adjust heading at next point
    BaseType::next();
    if (count > 1) {
      auto l = lengths[current];
      if (++gridCount == std::abs(l)) {
        auto h = getHeading();
        h += ((l > 0) ? 90 : -90);  // if negative, turn left, otherwise right
        if (h >= 360.0) {
          h -= 360;
        }
        setHeading(h);
        if (++current >= lengths.size()) {
          current = 0;
        }
        gridCount = 0;
      }
    }
    return position;
  }
  /** Retrieve the turn rate of the points in the generator
   *
   * @return Turn rate of the points
   */
  double getTurnRate() const { return turnRate; }

  /** Set the heading of the points
   */
  void setTurnRate(const double& _rate) { turnRate = _rate; }

 private:
 private:
  size_t current = 0;
  size_t gridCount = 0;
  double turnRate = .6;
  std::vector<int> lengths = {10};  ///< deg/s == circle per 10 min
};

/**
 * The collator lets you put together multiple generators and create a stream of points that is in
 * chronological order.
 *
 * * Use `addGenerator()` to add generators.
 * * Use `generate(COUNT)` to generate COUNT points for each generator and sort them.
 * * Use `next()` to access each point as they come out.
 *
 * Subsequent calls to generate will have the new points sorted into the list, but
 * there are no rule that the `next` point is after any points retrieved prior to the call
 *
 */
template <typename Point_T>
class MultipleGeneratorCollator {
  using PointT = Point_T;

 public:

  /** Add a generator to the list of generators
   */
  void addGenerator(std::shared_ptr<PointGenerator<PointT>> _generator) {
    if (_generator == nullptr) {
      throw std::runtime_error("Pointer is nullptr");
    }
    generators.push_back(_generator);
  }

  /** Retrieve the number of created generators
   *
   * @return The numbers of generators
   */
  const size_t getGeneratorCount() const { return generators.size(); }

    /** Updates position and returns a point
   *
   * @return new point
   */
  PointT next() {
    static size_t index = 0;
    if (0 == points.size()) {
      throw std::runtime_error("No generated points");
    }
    auto result = points.back();
    points.pop_back();
    return result;
  }

  /** Generate a generator with 10 points
   */
  void generate() { generate(10); }

  /** Generate a generator with n points
   *
   * @param [in] _count Number of points to create generator with
   */
  void generate(const size_t _count) {
    if (0 == generators.size()) {
      throw std::runtime_error("No generators");
    }
    for (auto i = 0u; i < _count; ++i) {
      for (auto& g : generators) {
        points.push_back(g->next());
      }
    }
    std::sort(points.begin(), points.end(),
              [](const PointT& _lhs, const PointT& _rhs) { return _lhs.timestamp() > _rhs.timestamp(); });
  }

 private:
  std::vector<std::shared_ptr<PointGenerator<PointT>>> generators;
  std::vector<PointT> points;
};

}//namespace tracktable

#undef PRINT

#endif