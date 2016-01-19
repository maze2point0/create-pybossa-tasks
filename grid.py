#!/bin/python
# -*- coding: UTF-8 -*-
# Author: B. Herfort, 2016
###########################################

import os, sys
from math import ceil
import math

def main(infile, zoomlevel, dev_height, dev_width):
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
	
	# average latitude of the area of interest
	y_average = ymin+((ymax-ymin)/2)
	
	# get feature geometry
	input_feature= layer.GetFeature(0)
	in_geometry= input_feature.GetGeometryRef()

	# get Zoomlevel
	zoomlevel = float(zoomlevel)
	
	# Calculate GridWidth and GridHeight from given inputs
	ground_resolution = (math.cos(y_average*math.pi/180)*360)/(256*math.pow(2,zoomlevel))	
	ground_resolution_2 = (360)/(256*math.pow(2,zoomlevel))
	gridWidth = float(dev_width)*ground_resolution_2
	gridHeight = float(dev_height)*ground_resolution
	
	# get rows
	rows = ceil((ymax-ymin)/gridHeight)
	# get columns
	cols = ceil((xmax-xmin)/gridWidth)

	# start grid cell envelope
	ringXleftOrigin = xmin
	ringXrightOrigin = xmin + gridWidth
	ringYtopOrigin = ymax
	ringYbottomOrigin = ymax-gridHeight

	# create output file

	outputGridfn = infile_name + '_grid.' + infile_extension
	
	outfile = infile_name + '_grid.csv'
	l = 0
	if os.path.exists(outfile):
		os.remove(outfile)
	fileobj_output = file(outfile,'w')
	fileobj_output.write('id;wkt;zoomlevel;dev_height;dev_width\n')

	outDriver = driver
	if os.path.exists(outputGridfn):
		os.remove(outputGridfn)
	outDataSource = outDriver.CreateDataSource(outputGridfn)
	outLayer = outDataSource.CreateLayer(outputGridfn,geom_type=ogr.wkbPolygon )
	featureDefn = outLayer.GetLayerDefn()

	# create grid cells
	countcols = 0
	while countcols < cols:
		countcols += 1

		# reset envelope for rows
		ringYtop = ringYtopOrigin
		ringYbottom =ringYbottomOrigin
		countrows = 0

		while countrows < rows:
			countrows += 1
			ring = ogr.Geometry(ogr.wkbLinearRing)
			ring.AddPoint(ringXleftOrigin, ringYtop)
			ring.AddPoint(ringXrightOrigin, ringYtop)
			ring.AddPoint(ringXrightOrigin, ringYbottom)
			ring.AddPoint(ringXleftOrigin, ringYbottom)
			ring.AddPoint(ringXleftOrigin, ringYtop)
			poly = ogr.Geometry(ogr.wkbPolygon)
			poly.AddGeometry(ring)

			# add new geom to layer
			intersect = in_geometry.Intersect(poly)
			if intersect == True:
				l = l+1
				o_line = poly.ExportToWkt()
				fileobj_output.write(str(l)+';'+o_line+';'+';'+str(zoomlevel)+';'+str(dev_height)+';'+str(dev_width)+'\n')
				
				outFeature = ogr.Feature(featureDefn)
				outFeature.SetGeometry(poly)
				outLayer.CreateFeature(outFeature)
				outFeature.Destroy

			# new envelope for next poly
			ringYtop = ringYtop - gridHeight
			ringYbottom = ringYbottom - gridHeight

		# new envelope for next poly
		ringXleftOrigin = ringXleftOrigin + gridWidth
		ringXrightOrigin = ringXrightOrigin + gridWidth
	
	# Close DataSources
	outDataSource.Destroy()
	
	print '############ END ######################################'
	print '##'
	print '## input file: '+infile
	print '##'
	print '## zoomlevel: '+str(zoomlevel)
	print '##'
	print '## device characteristics:'
	print '##      height: '+str(dev_height)
	print '##      width: '+str(dev_width)
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
    # example run : $ python grid.py polygon.shp 18 480 640
    #

    if len( sys.argv ) != 5: 
        print "[ ERROR ] you must supply four arguments: input-shapefile-name.shp zoomlevel device_height device_width"
        sys.exit( 1 )

    main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )
