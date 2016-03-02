# create-pybossa-tasks
Create tasks ready to use in PyBossa.

# Some basic workflows
- you may use test_geometry.kml for this

### Download all tiles for specific area of interest
1. Define the area of interest and get a .shp, .geojson, .kml file of it. Infile projection: EPSG 4326 (WGS84)! (e.g. here: https://osm.wno-edv-service.de/boundaries/)
	* result: aoi.shp
2. Find all tiles that intersect with your area of interest. Specify a zoomlevel. Use the script create_tiles_grid.py. 
	* input file: aoi.shp
	* result: aoi_tiles_grid.shp
3. Download all tiles. Specify an output directory. Use the script get_tiles.py.
	* input file: aoi_tiles_grid.shp
	* result: many .png files in the output directory you specified

### Create tiles that fit to a custom resolution
1. Define the area of interest and get a .shp, .geojson, .kml file of it. Infile projection: EPSG 4326 (WGS84)!  (e.g. here: https://osm.wno-edv-service.de/boundaries/)
	* result: aoi.shp
2. Create grids that have your custom resolution and intersect with the area of interest. Specifiy width, height and zoomlevel. Use the script create_custom_grid.py.
	* input file: aoi.shp
	* result: aoi_grid.shp
3. Find all tiles that intersect with your grids. Specify a zoomlevel. Use the script create_tiles_grid.py. 
	* input file: aoi_grid.shp
	* result: aoi_grid_tiles_grid.shp
4. Download all tiles. Specify an output directory. Use the script get_tiles.py.
	* input file: aoi_grid_tiles_grid.shp
	* result: many .png files in the output directory you specified
5. Stitch the tiles together and clip to your grid extent. Specify a directory with the png files of the tiles, an output directory and an compression modus. Use the script stitch_tiles.py.
	* input file: aoi_grid.shp
	* result: beautiful .png files that fit to your needs in the output directory you specified

# Scripts
### create_custom_grid.py

- calculate grid polygons from given input file, area of interest (.shp, .geojson, .kml)
- grid polygon size adjusted to specific resolution (e.g. 480x640 pixel)
- grid polygon size adjusted to specific zoomlevel
- two output files: e.g. polygon_grid.shp (for use in your GIS) and polygon_grid.csv (to upload in PyBossa)
- polygon_grid.csv contains: id;wkt_geometry;zoomlevel;width;height
- polygon_grid.shp and polygon_tiles_grid.geojson contain fields 'width', 'height', 'zoom'
- polygon_grid.kml contains field 'description' with 'width_height_zoom' as value

How to use the script create_custom_grid.py:
- example run: python create_custom_grid.py polygon.shp 480 640 18
- four arguments mandatory:
	- input file: e.g. polygon.shp, polygon.geojson, polygon.kml
	- device width in pixel: e.g. 480
	- device height in pixel: e.g. 640
	- zoomlevel: 1- 20

Constraints:
- requires python packages ogr, osr
- supported input file formats: .shp, .kml, .geojson
- input file projection: EPGS 4326 (WGS 84)


### create_tiles_grid.py
- get geometry of all tiles that intersect with input file, area of interest
- two output files: e.g. polygon_tiles_grid.shp (for use in your GIS) and polygon_tiles_grid.csv
- polygon_tiles_grid.csv contains: id;wkt_geometry;TileX;TileY;TileZ
- polygon_tiles_grid.shp and polygon_tiles_grid.geojson contain fields 'TileX', 'TileY', 'TileZ'
- polygon_tiles_grid.kml contains field 'description' with 'TileX_TileY_TileZ' as value

How to use the script create_tiles_grid.py:
- example run: python create_tiles_grid.py polygon.shp 18
- two arguments mandatory:
	- input file: e.g. polygon.shp, polygon.geojson, polygon.kml
	- zoomlevel: 1- 20

Constraints:
- requires python packages ogr, osr
- supported input file formats: .shp, .kml, .geojson
- input file projection: EPGS 4326 (WGS 84)

### get_tiles.py
- download all tiles as .png file for given tiles grid polygon
- save files to specified output directory
- check if files are already stored in output directory and will only download tiles that do not exist in the directory (when script exits, e.g. due to connection error, it will start from where it failed and will not download all the tiles again)
- requires file 'api_key.txt' with (BingMaps) api key in the same directory!
 
How to use the script create_tiles_grid.py:
- example run: python get_tiles.py polygon_tiles_grid.shp tiles_directory
- two arguments mandatory:
	- input file: e.g. polygon_tiles_grid.shp, polygon_tiles_grid.geojson, polygon_tiles_grid.kml, polygon_tiles_grid.csv
	- output directory: e.g. directory_path
	
Constraints:
- requires python packages ogr, osr, urllib, numpy
- input file must be in a format according to the result of the script create_tiles_grid.py
- supported input file formats: .shp, .kml, .geojson, .csv
- input file projection: EPGS 4326 (WGS 84)
- requires file 'api_key.txt' with (BingMaps) api key in the same directory 

### stitch_tiles.py
- creates custom PNG-files that fit to input grid
- find all tiles within one input grid geometry
- stitch all tiles together
- extract pixels that intersect with input grid geometry
- resulting PNG-file has the same size as specified in the input grid (e.g. 360x480 pixels)

How to use the script stitch_tiles.py:
- example run: python stitch_tiles.py polygon_grid.shp tiles_directory stitch_directory JPEG
- four arguments mandatory:
	- input file: e.g. polygon_grid.shp, polygon_grid.geojson, polygon_grid.kml
	- tiles directory: e.g. tiles_directory
	- stitch directory: e.g. stitch_directory
	- compression: e.g. JPEG or None (for more information see: http://www.gdal.org/frmt_gtiff.html)

Constraints:
- ...

# Test your results:
- adjust the file "simple_map.html"
- change the geometry in line 12, e.g. copy and paste a single geometry from your output .csv file
- (adjust the height and width of the map in line 46, so that they fit to the height and width you specified before)
- open the file in your webbrowser
