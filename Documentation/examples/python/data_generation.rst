.. _Python_Data_Generation_Example:

***************
Data Generation
***************

When real or quality trajectory data is not available, it is possible
to generate data sets given some constraints. Current methods for
auto generation of trajectories are based on using airports or bounding
boxes as the start and end points of the trajectory. Current methods for
generating heatmap points are based on placing points around a given set of
largest cities.

------------------------------------
Generate Airport-based Trajectories
------------------------------------

Tracktable includes data on many airports around the world. This data includes
latitude/longitude, airport codes, and size rankings based on traffic. This
data is available via the ``tracktable.info.airports`` package. The data generation
package provides methods for generating direct trajectories between pairs of airports
or between sets of airports. This can allow the user to simulate air traffic across
the whole world or in a specific locality.

Important constraints for generating trajectories include speed, time between points,
and the minimum number of points that make up the trajectory.

Generate Single Trajectory Between Airports
-------------------------------------------

This example shows how to retrieve airport data using airport codes and create a single trajectory.

.. code-block:: python
   :linenos:

   from datetime import datetime
   from tracktable.examples.data.generators import generate_trajectories
   from tracktable.info import airports

   ABQ_AIRPORT = airports.airport_information("ABQ")
   DEN_AIRPORT = airports.airport_information("DEN")
   new_trajectory = generate_trajectories.generate_airport_trajectory(
                                             start_airport=ABQ_AIRPORT,
                                             end_airport=DEN_AIRPORT,
                                             start_time=datetime.now(),
                                             object_id='ABQ-DEN',
                                             desired_speed=400,
                                             seconds_between_points=60,
                                             minimum_num_points=10)


Generate Multiple Trajectories Between Lists Of Airports
--------------------------------------------------------

This example shows how to retrieve a set of the ten largest airports and use it as input
to the ``tracktable.examples.data.generators.generate_trajectories`` package.
Alternatively, the ``tracktable.info.airports`` package could be used directly to get airports based
on other criteria. The result will be a list of airports that start and end at
random airports sampled from the given list.

.. code-block:: python
   :linenos:

   from tracktable.examples.data.generators import generate_trajectories

   ten_largest_airports = generate_trajectories.n_largest_airports(10)
   new_trajectories = generate_trajectories.generate_random_airport_trajectories(
                                          start_airport_list=ten_largest_airports[:5],
                                          end_airport_list=ten_largest_airports[5:],
                                          num_paths=5,
                                          desired_speed=400,
                                          seconds_between_points=60)


Generate Multiple Trajectories Between Random Airports
------------------------------------------------------

This example shows the method call for generating trajectories between completely
random airports. This is done by not defining lists for the starting and ending
points.

.. code-block:: python
   :linenos:

   from tracktable.examples.data.generators import generate_trajectories

   new_trajectories = generate_trajectories.generate_random_airport_trajectories(
                                      start_airport_list=None,
                                      end_airport_list=[],
                                      num_paths=5,
                                      desired_speed=400,
                                      seconds_between_points=60)

--------------------------------------------
Generate Trajectories Between Bounding Boxes
--------------------------------------------

Bounding boxes can be created and used as the start and end points as part
of trajectory generation. Points within the bounding boxes are randomly generated
and used as the endpoints.

The constraints for creating these trajectories are identical to the ones used in the
airport examples above.

This example shows one method for creating the bounding boxes and using them as input to
generate a list of 5 new trajectories.

.. code-block:: python
   :linenos:

    from datetime import datetime
    from tracktable.examples.data.generators import generate_trajectories
    from tracktable.domain.terrestrial import TrajectoryPoint as TerrestrialTrajectoryPoint

    bbox_type = TerrestrialTrajectoryPoint.domain_classes['BoundingBox']
    starting_min_corner = TerrestrialTrajectoryPoint.domain_classes['BasePoint']()
    starting_max_corner = TerrestrialTrajectoryPoint.domain_classes['BasePoint']()
    ending_min_corner = TerrestrialTrajectoryPoint.domain_classes['BasePoint']()
    ending_max_corner = TerrestrialTrajectoryPoint.domain_classes['BasePoint']()

    albuquerque = TerrestrialTrajectoryPoint(-106.6504, 35.0844)
    san_francisco = TerrestrialTrajectoryPoint( -122.4194, 37.7749)
    atlanta = TerrestrialTrajectoryPoint(-84.42806, 33.636719)
    miami = TerrestrialTrajectoryPoint(-80.290556, 25.79325)

    starting_min_corner[0] = san_francisco[0]
    starting_min_corner[1] = albuquerque[1]
    starting_max_corner[0] = albuquerque[0]
    starting_max_corner[1] = san_francisco[1]

    ending_min_corner[0] = atlanta[0]
    ending_min_corner[1] = miami[1]
    ending_max_corner[0] = miami[0]
    ending_max_corner[1] = atlanta[1]

    starting_bbox = bbox_type(starting_min_corner, starting_max_corner)
    ending_bbox = bbox_type(ending_min_corner, ending_max_corner)

    new_trajectories = generate_trajectories.generate_bbox_trajectories(
                                                    starting_bbox,
                                                    ending_bbox,
                                                    5,
                                                    'BBOXTST',
                                                    start_time=datetime.now(),
                                                    desired_speed=400,
                                                    seconds_between_points=60,
                                                    minimum_num_points=10)

--------------------------------
Generate Port-based Trajectories
--------------------------------

TBD

.. todo:: Create this section once Tracktable is able to intelligently generate trajectories between ports

----------------------------------
Generate City-based Heatmap Points
----------------------------------

Tracktable includes data on many large cities around the world. This data includes
toponymic information and offical standard names. This
data is available via the ``tracktable.info.cities`` package. The data generation
package provides methods for generating heatmap points around a given number of large cities.

Important constraints for generating heatmap points include location
and the minimum number of points that that will be generated around in a given radius around the given
cities.

Generate Heatmap Points Around Cities
-------------------------------------

This example shows how to generate heatmap points around 10 of the largest cities.

.. note:: The generated heatmap can be saved to a file by setting the ``write_file`` flag.

.. code-block:: python
   :linenos:

   from tracktable.examples.data.generators import generate_heatmap_points

   heatmap = generate_heatmap_points.generate_heatmap_points(
                                             num_cities=10,
                                             num_points_per_city=30,
                                             write_file=False,
                                             outfilename='SampleHeatmapPoints.csv')