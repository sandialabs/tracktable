# Jupyter Notebook Examples

This directory contains the Jupyter notebook examples showcasing the Python functionality
of the Tracktable library.

## Recommended Viewing Order
* Point Reader
* Trajectory Reader
* Trajectory Builder
* Static Image Trajectory Rendering
* Interactive Trajectory Rendering
* Heatmap Rendering
* Clustering with Distance Geometry


## Notebook Descriptions
### Clustering with Distance Geometry
This notebook is an end-to-end example of how to cluster trajectories in Tracktable using distance geometry. It goes through the following steps:

1. Read in points from a file.

2. Assemble those points into trajectories.

3. Create a distance geometry signature for each trajectory.

4. Using those signatures as feature vectors, compute clusters using DBSCAN.

5. Print statistics about each cluster.

6. Render the resulting clusters onto a map.

Eventually, distance geometry computation will move into the library itself.

### Heatmap Rendering
This notebook is an example of how to render heatmap of points. It goes through the following steps:

1. Read in points from a file.

2. Place the points into a list.

3. Create a heatmap of the points.

### Interactive Trajectory Rendering
This notebook is a tutorial showing many of the options available for rendering trajectories. This includes:

1. Read in points and assembling trajectories.

2. Render trajectories using all defaults parameters.
    * This renders trajectories with a hue that transitions from light to dark and a white dot showing the point with
     the latest timestamp.

3. Render trajectories using a different backed.
    * Default is Jupyter is folium otherwise default is cartopy.

4. Render a single trajectory.

5. Render trajectories separately each with their own map.

6. Render trajectories ontop a map with a custom title.

7. Render trajectories ontop a map with a custom map tile.

8. Render trajectories ontop a map with a smaller/larger bounding box(viewing area).

9. Render trajectories that have `object_ids` as a strings or a list of strings.

10. Render trajectories with a specified solid color or a list of specified solid colors.

11. Render trajectories with a specified color map or a list of specified color maps.

12. Render trajectories with a specified gradient hue or a list of specified gradient hue.

13. Render trajectories with specified scalar mappings.

14. Render trajectories with thiner/thicker linewidths.

15. Render trajectories with sample points displayed in the trajectory line.
    * Point information and color can be specified.

16. Render the trajectories with the end dot enabled or disabled.

17. Render the trajectories with the distance geometry calculation.
    * Only applicable to folium

18. Save rendered trajectories as an html file with a generic or specifed filename

### Point Reader
This notebook demonstrates how to create and use a terrestrial point reader.
The basic object in tracktable is the point reader.
The point reader data structure reads tabular data from a file and saves it as points containing, at the least:
* Object ID
* Timestamp
* Longitude
* Latitude

### Static Image Trajectory Rendering
This notebook is an example of how to statically render assembled trajectories. Similar to the `Interactive Trajectory Rendering`
notebook description above, trajectory characteristics can be modifed (linewidth, color, etc.).
Trajectories can be rendered with certain constraints. For example, we can have trajectories with a minimum number of points. Or we acknowledge that the points in the trajectory should be within a certain time and/or distance threshold to belong to the same trajectory.

### Trajectory Builder
This notebook is an example of how to assemble points into trajectories.
When you read in points from a file, you need to build those points into trajectories. As we know, data can be noisy, therefore we want to filter our trajectories to have a minimum number of points and/or a certain time or distance between points in a trajectory. The trajectory builder does all of this.

### Trajectory Reader
This notebook demonstrates how to create and use a Trajectory Reader.
If you have a file of already formed trajectories, you can use the Trajectory Reader to read them from file. Like the point reader, you can iterate over the trajectories you have and access the properties of the points in each trajectory.