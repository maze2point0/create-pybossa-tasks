# create-pybossa-tasks
Create tasks ready to use in PyBossa.


Update: Use create_custom_grid.py instead of grid.py.
What does create_custom_grid.py:
- calculate grid polygons from given input geometry
- grid polygon size adjusted to specific resolution (e.g. 480x640 pixel)
- grid polygon size adjusted to specific zoomlevel
- two output files: e.g. polygon_grid.shp (for use in your GIS) and polygon_grid.csv (to upload in PyBossa)
- polygon_grid.csv contains: id;wkt_geometry;zoomlevel;dev_height;dev_width

How to use the script create_custom_grid.py:
- example run: python create_custom_grid.py polygon.shp 18 640 480
- for arguments mandatory:
	- input file: e.g. polygon.shp, polygon.geojson, polygon.kml
	- zoomlevel: 1- 20
	- device height in pixel: e.g. 640
	- device width in pixel: e.g. 480

Constraints:
- requires python packages ogr, osr
- supported input file formats: .shp, .kml, .geojson
- input file projection: EPGS 4326 (WGS 84)
- only one geometry per input file supported right now, if you have an input file with two geometries only the first will be used for the calculation

Test your results:
- adjust the file "simple_map.html"
- change the geometry in line 12, e.g. copy and paste a single geometry from the output .csv file
- adjust the height and width of the map in line 46, so that they fit to the height and width you specified before
- open the file in your webbrowser
