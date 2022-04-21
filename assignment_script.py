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
import PySimpleGUI as sg


def searcharea_frompoint(xin, yin, buffer_radius):

    """
    Creates a point and buffer based on the user inputted arguments.

    point_x and point_y require pure easting and northing values.

    buffer_area value is in metres
    """

    pointGeom = Point(xin, yin)
    bufferGeom = pointGeom.buffer(buffer_radius, resolution=50)

    userfeat = gpd.GeoSeries(Point(xin, yin)).set_crs(epsg=27700, inplace=True)
    userbuffer = gpd.GeoSeries(userfeat.buffer(buffer_radius, resolution=50)).set_crs(epsg=27700, inplace=True)

    return userfeat, userbuffer, bufferGeom

def searcharea_frompoly(user_polypath, buffer_radius):
    """ """

    userfeat = gpd.read_file(user_polypath)
    userbuffer = gpd.GeoSeries(userfeat.buffer(buffer_radius))
    bufferGeom = ShapelyFeature(userbuffer['geometry'], myCRS)

    return userfeat, userbuffer, bufferGeom

def searchSpecies():
    """
    function to carry out a species search based on input parameters
    """
    # Run search on spp records <= 100m precision
    sppSearch = specieslayer[specieslayer.intersects(buffer_feature, align=True)]

    # Run 1km data species search
    spp1kmSearch = species1kmlayer[species1kmlayer.intersects(buffer_feature, align=True)]

    # Concatenate the 1km and <=100m species records search results
    sppSearch = pd.concat([sppSearch, spp1kmSearch])

    # Remove extraneous columns for GDPR
    sppOutput = sppSearch[['SciName', 'CommonName', 'InformalGr', 'Location', 'LocDetail', 'GridRef', 'Grid1km',
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

    return batSearch

def searchGCNs():
    """
    function to carry out a Great Crested Newt search based on input parameters
    """
    df = specieslayer
    gcnrecs = df[(df['InformalGr'] == 'amphibian') & df['CommonName'] == 'Great Crested Newt']
    gcnSearch = gcnrecs[gcnrecs.intersects(buffer_feature, align=True)]

    return gcnSearch


def searchInvasive():
    """
    function to carry out an Invasive Species search based on input parameters
    """
    df = specieslayer
    invrecs = df[(df['StatInvasive'] == 'Yes') & df['StaffsINNS'] == 'Yes']
    invSearch = invrecs[invrecs.intersects(buffer_feature, align=True)]

    return invSearch


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
point, buffer, buffer_feature = searcharea_frompoint(385000.00, 335000.00, 2000)

# Calls all species search
sppSearch, sppOutput = searchSpecies()

# Calls sites search function
sbiIntersect, basIntersect = searchSites()

# Calls bat only search
batSearch = searchBats()

# Calls GCN only search
gcnSearch = searchGCNs()

#Call

# Create an empty plot
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))


plotBuffer = buffer.plot(ax=ax, color='white', edgecolor='black') # adapt to accept user defined variable from GUI
plotPoint = point.plot(ax=ax, marker='*', color='red', markersize=2) # adapt to accept user defined variable from GUI
plotSBI = sbiIntersect.plot(ax=ax, color='green', alpha=0.5)
plotBAS = basIntersect.plot(ax=ax, color='blue', alpha=0.5)
plotPS100 = sppSearch.plot(ax=ax, color='indigo', edgecolor='black')
plotbats = batSearch.plot(ax=ax, marker='^', color='blue', edgecolor='black')
plotGCN = gcnSearch.plot(ax=ax, marker='o', color='yellow', edgecolor='black')

gridlines = ax.gridlines(draw_labels=True,
                         xlocs=range(360000,430000,1000),
                         ylocs=range(270000,370000,1000))

plt.show();




##### GUI #####

# Create GUI layout elements and structure
layout = [[sg.Text("Tool for the production of standard data searches")],
          [sg.Text("Please input grid reference (6,8 or 10 fig)"), sg.Input(key='-userGR-')],
          [sg.Button('Submit'),sg.Button('Cancel')]]

# put gui elements in a window
window = sg.Window("Data Search Enquiry", layout, margins=(200,100))


event, values = window.read(close=True)

if event == 'Submit':
  print('The events was ', event, 'You input', values['-userGR-'])
else:
  print('User cancelled')

# event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()
