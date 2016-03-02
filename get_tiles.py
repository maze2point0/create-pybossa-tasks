#!/bin/python
# -*- coding: UTF-8 -*-
# Author: B. Herfort, 2016
###########################################

import os, sys
from math import ceil
import math
import urllib
import numpy as np
import time

def tile_coords_and_zoom_to_quadKey(x, y, zoom):
    quadKey = ''
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if(x & mask) != 0:
            digit += 1
        if(y & mask) != 0:
            digit += 2
        quadKey += str(digit)
    #print "\nThe quadkey is {}".format(quadKey)
    return quadKey

		
def main(infile,outDirectory):
	
	#Take start time
	start_time = time.time()
	
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
	
	# Create output directory from input file name 
	if not os.path.exists(outDirectory):
		os.makedirs(outDirectory)
	
	# Get the driver --> supported formats: Shapefiles, GeoJSON, kml
	
	if infile_extension == 'csv':
		csv = np.genfromtxt (infile, delimiter=";")
		num_features = np.size(csv,0)-1
	else:
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
		num_features = layer.GetFeatureCount()
	
	
	for i in range(0,num_features):
		#in_geometry= input_feature.GetGeometryRef()
		if infile_extension == 'csv':
			TileX = int(csv[i+1][2])
			TileY = int(csv[i+1][3])
			TileZ = int(csv[i+1][4])
		else:
			# get feature geometry
			input_feature= layer.GetFeature(i)
			if infile_extension == 'kml':
				TileX = int(input_feature.GetFieldAsString('name').split('_')[0])
				TileY = int(input_feature.GetFieldAsString('name').split('_')[1])
				TileZ = int(input_feature.GetFieldAsString('name').split('_')[2])
			else:
				TileX = input_feature.GetFieldAsInteger('TileX')
				TileY = input_feature.GetFieldAsInteger('TileY')
				TileZ = input_feature.GetFieldAsInteger('TileZ')
		
		quad_key = tile_coords_and_zoom_to_quadKey(TileX,TileY,TileZ)
		
		
		try:
			f = open('api_key.txt')
			api_key = f.read()
		except:
			print ("Something is wrong with your API key."
				   "Do you even have an API key?")
		
		#TODO get this into a config file, and set up others (Google, OSM, etc) 
		tile_url = ("http://t0.tiles.virtualearth.net/tiles/a{}.jpeg?"
						"g=854&mkt=en-US&token={}".format(quad_key, api_key))
			#print "\nThe tile URL is: {}".format(tile_url)
			
		
		local_file = outDirectory + '/' + str(TileX)+'_'+str(TileY)+'_'+str(TileZ)+'.png'
		urllib.urlretrieve(tile_url, local_file)
		
		progress = round(100*float(i+1)/float(num_features),2)
		sys.stdout.write('Saved files: '+str(i+1)+' (progress: '+str(progress)+'%)'+'\r')
		sys.stdout.flush()
	
	#Take end time and calculate program run time
	end_time = time.time()
	run_time = end_time - start_time
	
	print '############ END ######################################'
	print '##'
	print '## input file: '+infile
	print '##'
	print '## output directory: '+outDirectory
	print '## number of output files: '+str(num_features)
	print '##'
	print '## runtime: '+str(run_time)+' s'
	print '##'
	print '## B. Herfort, GIScience Research Group'
	print '##'
	print '#######################################################'

if __name__ == "__main__":

    #
    # example run : $ python tiles_grid.py polygon.shp 18
    #

    if len( sys.argv ) != 3: 
        print "[ ERROR ] you must supply 2 arguments: input-shapefile-name.shp output_directory"
        sys.exit( 1 )

    main( sys.argv[1], sys.argv[2] )