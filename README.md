# create-pybossa-tasks
Create tasks ready to use in PyBossa.

What does grid.py:
- calculate grid polygons from given input geometry
- grid polygon size adjusted to specific resolution (e.g. 480x640 pixel) and orientation
- grid polygon size adjusted to specific zoomlevel
- two output files: e.g. polygon_grid.shp (for use in your GIS) and polygon_grid.csv (to upload in PyBossa)
- polygon_grid.csv contains: id;wkt_geometry;zoomlevel;dev_height;dev_width

How to use the script grid.py:
- example run: python grid.py polygon.shp 18 480x640 landscape
- for arguments mandatory:
	- input file: e.g. polygon.shp, polygon.geojson, polygon.kml
	- zoomlevel: 1- 20
	- device resolution: e.g. "480x640", but also custom sizes like "333x999"
	- device orientation: "landscape" or "portrait"

Constraints:
- requires python packages ogr, osr
- supported input file formats: .shp, .kml, .geojson
- input file projection: EPGS 4326 (WGS 84)
- only one geometry per input file supported right now, if you have an input file with two geometries only the first will be used for the calculation
