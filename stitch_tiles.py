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

def main(infile, tiles_dir, outDirectory, compression):#, tiles_dir, Outdir):

	#Take start time
	start_time = time.time()
	
	try:
		from osgeo import ogr, osr, gdal
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
	num_features = layer.GetFeatureCount()
	
	# Create output directory from input file name 
	if not os.path.exists(outDirectory):
		os.makedirs(outDirectory)
	
	id = 0
	for feature in layer:
		id = id+1
		out_file = outDirectory + '/'+infile_name+'_'+str(id-1)+'.png'
	
		geom = feature.GetGeometryRef()
		envelope = geom.GetEnvelope()
		
		xmin = envelope[0]
		xmax = envelope[1]
		ymin = envelope[2]
		ymax = envelope[3]
		
		# get width, height, zoom
		if infile_extension == 'kml':
			width = int(feature.GetFieldAsString('name').split('_')[0])
			height = int(feature.GetFieldAsString('name').split('_')[1])
			zoom = int(feature.GetFieldAsString('name').split('_')[2])
		else:
			width = feature.GetFieldAsInteger('width')
			height = feature.GetFieldAsInteger('height')
			zoom = feature.GetFieldAsInteger('zoom')
		
		# get upper left left tile coordinates
		pixel = lat_long_zoom_to_pixel_coords(ymax, xmin, zoom)
		Pixel_left = pixel.x
		Pixel_top = pixel.y
		
		tile = pixel_coords_to_tile_address(pixel.x, pixel.y)
		TileX_left = tile.x
		TileY_top = tile.y
		
		# get lower right tile coordinates
		pixel = lat_long_zoom_to_pixel_coords(ymin, xmax, zoom)
		Pixel_right = pixel.x
		Pixel_bottom = pixel.y
		
		tile = pixel_coords_to_tile_address(pixel.x, pixel.y)
		TileX_right = tile.x
		TileY_bottom = tile.y
		
		
		for TileY in range(TileY_top,TileY_bottom+1):
			for TileX in range(TileX_left,TileX_right+1):
				
				tile_file = tiles_dir + '/' + str(TileX)+'_'+str(TileY)+'_'+str(zoom)+'.png'
				
				# Read tile_file and save as array
				ds= gdal.Open( tile_file )
				band1 = ds.GetRasterBand(1) #redchannel
				data1 = band1.ReadAsArray(0, 0, 256, 256).astype(float)

				band2 = ds.GetRasterBand(2) #redchannel
				data2 = band2.ReadAsArray(0, 0, 256, 256).astype(float)

				band3 = ds.GetRasterBand(3) #redchannel
				data3 = band3.ReadAsArray(0, 0, 256, 256).astype(float)
				
				if TileX == TileX_left:
					x_merge_band1 = data1
					x_merge_band2 = data2
					x_merge_band3 = data3
				else:	
					x_merge_band1 = np.concatenate((x_merge_band1,data1),axis=1)
					x_merge_band2 = np.concatenate((x_merge_band2,data2),axis=1)
					x_merge_band3 = np.concatenate((x_merge_band3,data3),axis=1)
					
			
			if TileY == TileY_top:
				merge_band1 = x_merge_band1
				merge_band2 = x_merge_band2
				merge_band3 = x_merge_band3
			else:
				merge_band1 = np.concatenate((merge_band1,x_merge_band1),axis=0)
				merge_band2 = np.concatenate((merge_band2,x_merge_band2),axis=0)
				merge_band3 = np.concatenate((merge_band3,x_merge_band3),axis=0)
	
		
		# get array size
		
		# calculate mask
		mask_left = (Pixel_left % 256)
		mask_right = mask_left + width
		mask_top = (Pixel_top % 256)
		mask_bottom = mask_top + height
		
		# extract values from array using mask
		merge_band1 = merge_band1[mask_top:mask_bottom,mask_left:mask_right]
		merge_band2 = merge_band2[mask_top:mask_bottom,mask_left:mask_right]
		merge_band3 = merge_band3[mask_top:mask_bottom,mask_left:mask_right]
		
		
		# create output raster file
		driver = gdal.GetDriverByName('GTiff')
		outRaster= driver.Create(out_file, width, height, 3, gdal.GDT_Byte, options = [ 'COMPRESS='+compression ])
		pixelWidth = 1
		pixelHeight = 1
		originX = 0
		originY = 0
		outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
		
		outband = outRaster.GetRasterBand(1)
		outband.SetNoDataValue(-9999)
		outband.WriteArray(merge_band1)

		outband = outRaster.GetRasterBand(2)
		outband.SetNoDataValue(-9999)
		outband.WriteArray(merge_band2)

		outband = outRaster.GetRasterBand(3)
		outband.SetNoDataValue(-9999)
		outband.WriteArray(merge_band3)
		
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
    # example run : $ python stitch_tiles.py l_grid_sample.kml lichtenberg_tiles
    #

    if len( sys.argv ) != 5: 
        print "[ ERROR ] you must supply 4 arguments: input-shapefile-name.shp tiles_directory output_directory compression"
        sys.exit( 1 )

    main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] )
