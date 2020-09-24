#ifndef PointGenerator_h
#define PointGenerator_h

#include <tracktable/Core/Timestamp.h>
#include <tracktable/Domain/Terrestrial.h>

#include <algorithm>
#include <cmath>
#include <stdexcept>

#define PRINT(X) std::cout << #X ": " << (X) << std::endl;

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

  PointGenerator() : PointGenerator(PointT()) {}
  /** Sets the initial point to _position
   * @param _position Initial point to use, including all metadata */
  PointGenerator(const PointT& _position) : PointGenerator(_position, tracktable::seconds(60)) {}
  /** Sets the initial point to _position, and the time interval
   * @param _position Initial point to use
   * @param _interval Interval to increase timestamp by */
  PointGenerator(const PointT& _position, const DurationT& _interval)
      : position(_position), interval(_interval) {}
  /** Updates position and returns a point
   * @returns new point */
  virtual PointT next() {
    if (count++ != 0) {
      position.set_timestamp(position.timestamp() + interval);
    }
    return position;
  }

  DurationT getInterval() const { return interval; }
  void setInterval(const DurationT& _interval) { interval = _interval; }

  std::string getObjectId() const { return position.object_id(); }
  void setObjectId(const std::string& _id) { position.set_object_id(_id); }

 protected:
  DurationT interval;  ///< Update Interval
  size_t count = 0;    ///< Count of points generated
  PointT position;     ///< Last point generated
};

/** Generates points based on a heading and speed
 * each point is callculated based on the last point */
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
   * @param _origin   The starting point
   * @param _distance The distance traveled [m]
   * @param _heading  The compass heading to travel
   * @return PointT   The final destination
   */
  static PointT reckon(PointT _origin /*lon,lat*/, double _distance /*m*/, double _heading /*deg*/) {
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
   * @param _origin Start location
   * @param _speed  Speed traveled [m/s]
   * @param _heading Compass heading to travel
   * @param _dt  Duration of travel
   * @return PointT resulting point
   */
  static PointT reckon2(const PointT& _origin /*lon,lat*/, const double& _speed /*m/s*/,
                        const double& _heading /*deg*/, const DurationT& _dt) {
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

  ConstantSpeedPointGenerator() : BaseType() {}
  ConstantSpeedPointGenerator(const PointT& _position) : BaseType(_position) {}
  ConstantSpeedPointGenerator(const PointT& _position, const DurationT& _interval)
      : BaseType(_position, _interval) {}
  ConstantSpeedPointGenerator(const PointT& _position, const DurationT& _interval, const double& _speed,
                              const double& _heading)
      : BaseType(_position, _interval), speed(_speed), heading(_heading) {}

  PointT next() override {
    BaseType::next();
    if (count > 1) {
      auto d = speed * double(interval.total_seconds());
      // position = reckon(position, d, heading);
      position = reckon2(position, speed, heading, interval);
    }
    return position;
  }

  double getSpeed() const { return speed; }
  void setSpeed(const double& _speed) { speed = _speed; }
  double getHeading() const { return heading; }
  void setHeading(const double& _heading) { heading = _heading; }

 private:
  double speed = 44.704;  // ~100Mi/h in m/s
  double heading = 0.0;   // North
};

class CircularPointGenerator : public ConstantSpeedPointGenerator {
 protected:
  using ThisType = CircularPointGenerator;
  using BaseType = ConstantSpeedPointGenerator;

 public:
  using DurationT = BaseType::DurationT;
  using PointT = BaseType::PointT;

 public:
  CircularPointGenerator() : BaseType() {}
  CircularPointGenerator(const PointT& _position) : BaseType(_position) {}
  CircularPointGenerator(const PointT& _position, const DurationT& _interval)
      : BaseType(_position, _interval) {}
  CircularPointGenerator(const PointT& _position, const DurationT& _interval, const double& _speed,
                         const double& _heading)
      : BaseType(_position, _interval, _speed, _heading) {}
  CircularPointGenerator(const PointT& _position, const DurationT& _interval, const double& _speed,
                         const double& _heading, const double& _turnRate)
      : BaseType(_position, _interval, _speed, _heading), turnRate(_turnRate) {}

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
  double getTurnRate() const { return turnRate; }
  void setTurnRate(const double& _rate) { turnRate = _rate; }

 private:
  double turnRate = .6;  // deg/s == circle per 10 min
};

/**
 * Generator for generating boxes, snakes, or anything else on a grid
 *
 * take a length vector that tell how long each side is. if the length is
 * negative, then it will turn left afterwards, otherwise it will turn right
 *
 * use a length vector of {10} to create a box with 10 points on each side
 * use a length vector of {10,2,-10,-2} to create a mapping flight
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
  GridPointGenerator() : BaseType() {}
  GridPointGenerator(const PointT& _position) : BaseType(_position) {}
  GridPointGenerator(const PointT& _position, const DurationT& _interval) : BaseType(_position, _interval) {}
  GridPointGenerator(const PointT& _position, const DurationT& _interval, const double& _speed,
                     const double& _heading)
      : BaseType(_position, _interval, _speed, _heading) {}
  GridPointGenerator(const PointT& _position, const DurationT& _interval, const double& _speed,
                     const double& _heading, std::vector<int> _lengths)
      : BaseType(_position, _interval, _speed, _heading), lengths(_lengths) {}

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
  double getTurnRate() const { return turnRate; }
  void setTurnRate(const double& _rate) { turnRate = _rate; }

 private:
 private:
  size_t current = 0;
  size_t gridCount = 0;
  double turnRate = .6;
  std::vector<int> lengths = {10};  // deg/s == circle per 10 min
};

/**
 * The collator lets you put together multiple generators and create a stream of points that is in
 * chronological order.
 *
 * use addGenerator() to add generators
 * use generate(COUNT) to generate COUNT points for each generator and sort them
 * use next() to access each point as they come out
 *
 * subsequent calls tos generate will have the new points sorted into the list, but
 * there are no rule that the 'next' point is after any points retrieved prior to the call
 *
 */
template <typename Point_T>
class MultipleGeneratorCollator {
  using PointT = Point_T;

 public:
  void addGenerator(std::shared_ptr<PointGenerator<PointT>> _generator) {
    if (_generator == nullptr) {
      throw std::runtime_error("Pointer is nullptr");
    }
    generators.push_back(_generator);
  }
  const size_t getGeneratorCount() const { return generators.size(); }
  PointT next() {
    static size_t index = 0;
    if (0 == points.size()) {
      throw std::runtime_error("No generated points");
    }
    auto result = points.back();
    points.pop_back();
    return result;
  }
  void generate() { generate(10); }
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

#endif