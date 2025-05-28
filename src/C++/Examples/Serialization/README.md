Compare storage costs for various methods of serializing trajectories

  We have three ways to save trajectories:

 1. tracktable::TrajectoryWriter (C++, Python)
    This uses our own home-grown delimited text format.  It is rather
    verbose.

  2. tracktable.rw.read_write_json (Python)
     Write to JSON.  This is also rather verbose and has trouble with
     incremental loads.

 3. boost::serialization
    Write to Boost's archive format (text, binary or XML).

 This example runs #1 and #3 on a sample trajectory and compares the
 storage requirements.

 This example demonstrates:
   - use of boost program options
   - use of boost archives
   - use of trajectory writer
   - Manual construction of points and trajectories

Typical use:
    ./serialize_trajectories --trajectory-count=100 --point-count=100