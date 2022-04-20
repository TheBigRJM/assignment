#data search enquiry creator, R. Middleton 2022

#Test data bounding box =
# xmin: 380000.00
# xmax: 390000.00
# ymin: 330000.00
# ymax: 340000.00

import numpy as np
import rasterio as rio
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString, Polygon
import PySimpleGUI as sg

myCRS = ccrs.epsg(27700) # note that this matches with the CRS of our image
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS)) # Create an empty plot

dboundary = gpd.read_file('SampleData/SHP/SampleDataSelector_rectangle.shp')
specieslayer = gpd.read_file('SampleData/SHP/ProtSpp_font_point.shp')
sbilayer = gpd.read_file('SampleData/SHP/SBI_region.shp')
baslayer = gpd.read_file('SampleData/SHP/BAS_region.shp')


def searcharea_frompoint(xin, yin, buffer_radius):

    """
    Creates a point and buffer based on the user inputted arguments.

    point_x and point_y require pure easting and northing values.

    buffer_area value is in metres
    """

# create global variables to use outside the function
    global bufferGeom
    global userfeat
    global userbuffer

    pointGeom = Point(xin, yin)
    bufferGeom = pointGeom.buffer(buffer_radius, resolution=50)

    userfeat = gpd.GeoSeries(Point(xin, yin)).set_crs(epsg=27700, inplace=True)
    userbuffer = gpd.GeoSeries(userfeat.buffer(buffer_radius, resolution=50)).set_crs(epsg=27700, inplace=True)

    return userfeat, userbuffer, bufferGeom

def searcharea_frompoly(user_poly, buffer_radius, bufferGeom):
    """ """

    userfeat = gpd.read_file(user_poly)
    userbuffer = gpd.GeoSeries(userfeat.buffer(buffer_radius))

def searchSpecies
    """function to carry out a species search based on input parameters"""




def searchBats
    """function to carry out a bats search based on input parameters"""

def searchGCNs
    """function to carry out a Great Crested Newt search based on input parameters"""

def searchInvasive
    """function to carry out an Invasive Species search based on input parameters"""

def searchSites():
    '''
    function to carry out a nature conservation sites search based on input parameters
    note the buffer must be a shapely geometry as intersecting two GeoDataFrames requires equal indexes
    '''
    sbiIntersect = sbilayer[sbilayer.intersects(bufferGeom, align=True)]
    basIntersect = baslayer[baslayer.intersects(bufferGeom, align=True)]

    sbiIntersect.plot(ax=ax, color='green', alpha=0.5)
    basIntersect.plot(ax=ax, color='blue', alpha=0.5)

    return sbiIntersect, basIntersect

searcharea_frompoint(385000.00, 33500.00, 2000)
searchSites()
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))



userbuffer.plot(ax=ax, color='white', edgecolor='black') # adapt to accept user defined variable from GUI
userfeat.plot(ax=ax, marker='o', color='red', markersize=2) # adapt to accept user defined variable from GUI
sbilayer.plot(ax=ax, color='green', alpha=0.5)
baslayer.plot(ax=ax, color='blue', alpha=0.5)

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