#data search enquiry creator, R. Middleton 2022

#Test data bounding box =
# xmin: 380000.00
# xmax: 390000.00
# ymin: 330000.00
# ymax: 340000.00

import numpy as np
import pandas as pd
import rasterio as rio
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString, Polygon


def searcharea_frompoint(xin, yin, buffer_radius):

    """
    Creates a point and buffer based on the user inputted arguments.

    point_x and point_y require pure easting and northing values.

    buffer_area value is in metres
    """

    userpoint = Point(xin, yin) # shapely feature
    bufferGeom = userpoint.buffer(buffer_radius, resolution=50) # shapely feature for running search

    userfeat = gpd.GeoSeries(Point(xin, yin)).set_crs(epsg=27700, inplace=True) # convert to geoseries for mapping
    userbuffer = gpd.GeoSeries(userfeat.buffer(buffer_radius, resolution=50)).set_crs(epsg=27700, inplace=True)

    return userfeat, userbuffer, bufferGeom

def searcharea_frompoly(user_polypath, buffer_radius):
    """ """

    userfile = gpd.read_file(user_polypath)
    userbuffer = gpd.GeoSeries(userfile.buffer(buffer_radius))
    userbuffer = gpd.GeoDataFrame(geometry=gpd.GeoSeries(userbuffer))
    bufferGeom = ShapelyFeature(userbuffer['geometry'], myCRS)

    return userfile, userbuffer, bufferGeom

def searchSpecies():
    """
    function to carry out a species search based on input parameters
    """
    # Run search on spp records <= 100m precision
    sppSearch = specieslayer[specieslayer.intersects(buffer_feature, align=True)]

    # Run 1km data species search
    spp1kmSearch = species1kmlayer[species1kmlayer.intersects(buffer_feature, align=True)]

    # Concatenate the 1km and <=100m species records search results
    sppConcat = pd.concat([sppSearch, spp1kmSearch])

    # Remove extraneous columns for GDPR
    sppOutput = sppConcat[['SciName', 'CommonName', 'InformalGr', 'Location', 'LocDetail', 'GridRef', 'Grid1km',
                           'Date', 'Year', 'Source', 'SampleMeth', 'SexStage', 'RecType', 'EuProt', 'UKProt',
                           'PrincipalS', 'RareSpp', 'StatInvasi', 'StaffsINNS', 'RecordStat', 'Confidenti',
                           'Easting', 'Northing', 'Precision']]

    return sppSearch, sppOutput

def searchBats():
    """
    function to carry out a bats search based on input parameters
    """

    batrecs = specieslayer[specieslayer['InformalGr'] == 'mammal - bat']
    batSearch = batrecs[batrecs.intersects(buffer_feature, align=True)]

    # Remove extraneous columns for GDPR
    batOutput = batSearch[['SciName', 'CommonName', 'InformalGr', 'Location', 'LocDetail', 'GridRef', 'Grid1km',
                           'Date', 'Year', 'Source', 'SampleMeth', 'SexStage', 'RecType', 'EuProt', 'UKProt',
                           'PrincipalS', 'RareSpp', 'StatInvasi', 'StaffsINNS', 'RecordStat', 'Confidenti',
                           'Easting', 'Northing', 'Precision']]

    return batSearch, batOutput

def searchGCNs():
    """
    function to carry out a Great Crested Newt search based on input parameters
    """
    df = specieslayer
    gcnrecs = df[df['CommonName'] == 'Great Crested Newt']
    gcnSearch = gcnrecs[gcnrecs.intersects(buffer_feature, align=True)]

    # Remove extraneous columns for GDPR
    gcnOutput = gcnSearch[['SciName', 'CommonName', 'InformalGr', 'Location', 'LocDetail', 'GridRef', 'Grid1km',
                           'Date', 'Year', 'Source', 'SampleMeth', 'SexStage', 'RecType', 'EuProt', 'UKProt',
                           'PrincipalS', 'RareSpp', 'StatInvasi', 'StaffsINNS', 'RecordStat', 'Confidenti',
                           'Easting', 'Northing', 'Precision']]

    return gcnSearch, gcnOutput


def searchInvasive():
    """
    function to carry out an Invasive Species search based on input parameters
    """
    df = specieslayer
    invrecs = df[(df['StatInvasive'] == 'Yes') & df['StaffsINNS'] == 'Yes']
    invSearch = invrecs[invrecs.intersects(buffer_feature, align=True)]

    invOutput = invSearch[['SciName', 'CommonName', 'InformalGr', 'Location', 'LocDetail', 'GridRef', 'Grid1km',
                           'Date', 'Year', 'Source', 'SampleMeth', 'SexStage', 'RecType', 'EuProt', 'UKProt',
                           'PrincipalS', 'RareSpp', 'StatInvasi', 'StaffsINNS', 'RecordStat', 'Confidenti',
                           'Easting', 'Northing', 'Precision']]

    return invSearch, invOutput


def searchSites():
    '''
    function to carry out a nature conservation sites search based on input parameters
    note the buffer must be a shapely geometry feature as intersecting two GeoDataFrames requires equal indexes
    '''
    sbiIntersect = sbilayer[sbilayer.intersects(buffer_feature, align=True)]
    basIntersect = baslayer[baslayer.intersects(buffer_feature, align=True)]



    return sbiIntersect, basIntersect


### main program ###

dboundary = gpd.read_file('SampleData/SHP/SampleDataSelector_rectangle.shp')
specieslayer = gpd.read_file('SampleData/SHP/ProtSpp_font_point.shp')
species1kmlayer = gpd.read_file('SampleData/SHP/ProtSpp1km_region.shp')
sbilayer = gpd.read_file('SampleData/SHP/SBI_region.shp')
baslayer = gpd.read_file('SampleData/SHP/BAS_region.shp')

myCRS = ccrs.epsg(27700) # note that this matches with the CRS of our image

# Create point and buffer using user defined co-ordinates & buffer feature for interrogation
#point, buffer, buffer_feature = searcharea_frompoint(385000.00, 335000.00, 2000)
# from polygon
#userpoly, buffer, buffer_feature = \
   # searcharea_frompoly("D:/UlsterProgramming/assignment/SampleData/SHP/ExampleBoundarySearch_region.shp", 2000)

# Calls all species search
sppSearch, sppOutput = searchSpecies()

# Calls sites search function
sbiIntersect, basIntersect = searchSites()

# Calls bat only search
batSearch, batOutput = searchBats()

# Calls GCN only search
gcnSearch, gcnOutput = searchGCNs()

#Call

# Create an empty plot
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# Note: set this as separate function to call last
plotBuffer = buffer.plot(ax=ax, color='white', edgecolor='black') # adapt to accept user defined variable from GUI
plotPoint = point.plot(ax=ax, marker='*', color='red', markersize=2) # adapt to accept user defined variable from GUI
#plotUserPoly = userpoly.plot(ax=ax, color='black', alpha=0.5)
plotSBI = sbiIntersect.plot(ax=ax, color='green', alpha=0.5)
plotBAS = basIntersect.plot(ax=ax, color='blue', alpha=0.5)
plotPS100 = sppSearch.plot(ax=ax, color='indigo', edgecolor='black')
plotbats = batSearch.plot(ax=ax, marker='^', color='blue', edgecolor='black')
plotGCN = gcnSearch.plot(ax=ax, marker='o', color='yellow', edgecolor='black')

gridlines = ax.gridlines(draw_labels=True,
                         xlocs=range(360000,430000,1000),
                         ylocs=range(270000,370000,1000))

plt.show();