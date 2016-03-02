#!/bin/python
# -*- coding: UTF-8 -*-
# Author: B. Herfort, 2016
###########################################

import os, sys
from math import ceil
import math

class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class Tile:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


def lat_long_zoom_to_pixel_coords(lat, lon, zoom):
    p = Point()
    sinLat = math.sin(lat * math.pi/180.0)
    x = ((lon + 180) / 360) * 256 * math.pow(2,zoom)
    y = (0.5 - math.log((1 + sinLat) / (1 - sinLat)) / 
          (4 * math.pi)) * 256 * math.pow(2,zoom)
    p.x = int(math.floor(x))
    p.y = int(math.floor(y))
    #print "\nThe pixel coordinates are x = {} and y = {}".format(p.x, p.y)
    return p

def pixel_coords_to_tile_address(x,y):
    t = Tile()
    t.x = int(math.floor(x / 256))
    t.y = int(math.floor(y / 256))
    #print"\nThe tile coordinates are x = {} and y = {}".format(t.x, t.y)
    return t


def main(infile, width, height, zoomlevel):
	try:
		from osgeo import ogr, osr
		print 'Import of ogr and osr from osgeo worked.  Hurray!\n'
	except:
		print '############ ERROR ######################################'
		print '## Import of ogr from osgeo failed\n\n'
		print '#########################################################'
		sys.exit()
	
	# Get filename and extension
	try:
		infile_name = infile.split('.')[0]
		infile_extension = infile.split('.')[-1]
	except:
		print "check input file"
		sys.exit()
	

	# Get the driver --> supported formats: Shapefiles, GeoJSON, kml
	if infile_extension == 'shp':
		driver = ogr.GetDriverByName('ESRI Shapefile')
	elif infile_extension == 'geojson':
		driver = ogr.GetDriverByName('GeoJSON')
	elif infile_extension == 'kml':
		driver = ogr.GetDriverByName('KML')
	else:
		print 'Check input file format for '+infile
		print 'Supported formats .shp .geojson .kml'
		sys.exit()
	# open the data source
	datasource = driver.Open(infile, 0)
	try:
		# Get the data layer
		layer = datasource.GetLayer()
	except:
		print '############ ERROR ######################################'
		print '##'
		print '## Check input file!'
		print '## '+infile
		print '##'
		print '#########################################################'
		sys.exit()
	# Get layer definition
	layer_defn = layer.GetLayerDefn()

	# Get layer extent
	extent = layer.GetExtent()
	xmin = extent[0]
	xmax = extent[1]
	ymin = extent[2]
	ymax = extent[3]
	
	
	# get feature geometry of all features of the input file
	geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
	for feature in layer:
		geomcol.AddGeometry(feature.GetGeometryRef())

	# get Zoomlevel
	zoom = float(zoomlevel)
	
	# create output file
	outputGridfn = infile_name + '_grid.' + infile_extension
	
	outfile = infile_name + '_grid.csv'
	l = 0
	if os.path.exists(outfile):
		os.remove(outfile)
	fileobj_output = file(outfile,'w')
	fileobj_output.write('id;wkt;width;height\n')

	outDriver = driver
	if os.path.exists(outputGridfn):
		os.remove(outputGridfn)
	outDataSource = outDriver.CreateDataSource(outputGridfn)
	outLayer = outDataSource.CreateLayer(outputGridfn,geom_type=ogr.wkbPolygon )
	featureDefn = outLayer.GetLayerDefn()
	
	
	# get upper left pixel coordinates
	pixel = lat_long_zoom_to_pixel_coords(ymax, xmin, zoom)
	pixel_left = pixel.x
	pixel_top = pixel.y
	
	# get lower right pixel coordinates
	pixel = lat_long_zoom_to_pixel_coords(ymin, xmax, zoom)
	pixel_right = pixel.x
	pixel_bottom = pixel.y
	
	aoi_width = pixel_right - pixel_left
	aoi_height = pixel_bottom - pixel_top
	
	x_grids = int((pixel_right - pixel_left)/float(width))+1
	y_grids = int((pixel_bottom - pixel_top)/float(height))+1

	
	for i in range(0,y_grids):
		for j in range(0,x_grids):
			
			# Calculate lat, lon of upper left corner of tile
			PixelX = pixel_left + (j*int(width))
			PixelY = pixel_top + (i*int(height))
			MapSize = 256*math.pow(2,zoom)
			x = (PixelX / MapSize) - 0.5
			y = 0.5 - (PixelY / MapSize)
			lon_left = 360 * x
			lat_top = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi
			
			# Calculate lat, lon of lower right corner of tile
			PixelX = pixel_left + ((j+1)*int(width))
			PixelY = pixel_top + ((i+1)*int(height))
			MapSize = 256*math.pow(2,zoom)
			x = (PixelX / MapSize) - 0.5
			y = 0.5 - (PixelY / MapSize)
			lon_right = 360 * x 
			lat_bottom = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi
			
			# Create Geometry
			ring = ogr.Geometry(ogr.wkbLinearRing)
			ring.AddPoint(lon_left, lat_top)
			ring.AddPoint(lon_right, lat_top)
			ring.AddPoint(lon_right, lat_bottom)
			ring.AddPoint(lon_left, lat_bottom)
			ring.AddPoint(lon_left, lat_top)
			poly = ogr.Geometry(ogr.wkbPolygon)
			poly.AddGeometry(ring)

			# add new geom to layer
			intersect = geomcol.Intersect(poly)
			if intersect == True:
				l = l+1
				o_line = poly.ExportToWkt()
				fileobj_output.write(str(l)+';'+o_line+';'+width+';'+height+'\n')
				
				outFeature = ogr.Feature(featureDefn)
				outFeature.SetGeometry(poly)
				outLayer.CreateFeature(outFeature)
				outFeature.Destroy

	
	# Close DataSources
	outDataSource.Destroy()
	
	print '############ END ######################################'
	print '##'
	print '## input file: '+infile
	print '##'
	print '## zoomlevel: '+str(zoomlevel)
	print '##'
	print '## output files:'
	print '##      '+outputGridfn
	print '##      '+outfile
	print '##'
	print '## B. Herfort, GIScience Research Group'
	print '##'
	print '#######################################################'


if __name__ == "__main__":

    #
    # example run : $ python tiles_grid.py polygon.shp 360 480 18
    #

    if len( sys.argv ) != 5: 
        print "[ ERROR ] you must supply 4 arguments: input-shapefile-name.shp width height zoomlevel"
        sys.exit( 1 )

    main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],)
