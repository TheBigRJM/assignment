import numpy as np
import pandas as pd
import rasterio as rio
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString, Polygon, LinearRing
import PySimpleGUI as sg


##### GUI #####
# Create GUI layout elements and structure

column1 = [[sg.Text("Enquiry number:"), sg.InputText(size=2, key="-ENQYEAR-"), sg.InputText(size=3, key="-ENQNO-"), ],
           [sg.Text("----------------------------------------")],
           [sg.Text("Search from Grid Reference or Shapefile")],
           [sg.Text("Grid Reference"), sg.Input(key="-EASTING-"), sg.Input(key="-NORTHING-"),
            sg.Text('-OR-'), sg.Text("Shapefile"), sg.Input(key="-BDYFILE-", enable_events=True), sg.FileBrowse()],
           [sg.Text("Search Radius (in metres)"), sg.Input(key="-RADIUS-", enable_events=True)],
           [sg.Text("", key="-DIALOGUE-")]]


column2 = [[sg.Text("Select Search parameters")],
           [sg.Checkbox('Species', default=False, key="-SPP-")],
           [sg.Checkbox('Bats only', default=False, key="-BATS-")],
           [sg.Checkbox('GCN only', default=False, key="-GCN-")],
           [sg.Checkbox('Invasives', default=False, key="-INV-")],
           [sg.Checkbox('Sites', default=False, key="-SITES-")]]

layout = [[sg.Column(column1), sg.VSeparator(), sg.Column(column2)],
          [sg.Button('Proceed', key=("-PROCEED-")), sg.CloseButton('Cancel', key=("-CANCEL-"))]]

# put gui elements in a window
window = sg.Window("Data Search Enquiry", layout, margins=(200, 100))

# Declare GUI functions
def searcharea_frompoint(xin, yin, buffer_radius):

    """
    Creates a point and buffer based on the user inputted arguments.

    point_x and point_y require pure easting and northing values.

    buffer_area value is in metres
    """

    userpoint = Point(xin, yin) # shapely geometry
    bufferGeom = userpoint.buffer(buffer_radius, resolution=50) # shapely geometry for running search

    userfeat = gpd.GeoSeries(Point(xin, yin)).set_crs(epsg=27700, inplace=True) # convert to geoseries for mapping
    userbuffer = gpd.GeoSeries(userfeat.buffer(buffer_radius, resolution=50)).set_crs(epsg=27700, inplace=True)

    return userfeat, userbuffer, bufferGeom

def searcharea_frompoly(user_polypath, buffer_radius):
    """ """

    userfile = gpd.read_file(user_polypath) # import user selected file
    userbuff = gpd.GeoSeries(userfile.buffer(buffer_radius)) # buffer user file with user input buffer
    userbuffer = gpd.GeoDataFrame(geometry=gpd.GeoSeries(userbuff)) # transform buffer to geoseries
    bufferGeom = ShapelyFeature(userbuffer['geometry'], myCRS) # convert to shapely feature. INCORRECT FORMAT FOR INTERSECTS

    return userfile, userbuffer, bufferGeom


def coord_lister(geom):
    coords = list(geom.exterior.coords)
    return (coords)

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



# Load files to search on
dboundary = gpd.read_file('SampleData/SHP/SampleDataSelector_rectangle.shp')
specieslayer = gpd.read_file('SampleData/SHP/ProtSpp_font_point.shp')
species1kmlayer = gpd.read_file('SampleData/SHP/ProtSpp1km_region.shp')
sbilayer = gpd.read_file('SampleData/SHP/SBI_region.shp')
baslayer = gpd.read_file('SampleData/SHP/BAS_region.shp')

myCRS = ccrs.epsg(27700) # note that this matches with the CRS of our image



# GUI event loop
while True:
    event, values = window.read()
    print(values)

    if event == sg.WIN_CLOSED or event=="-CANCEL-":
        print('User cancelled')
        break


    user_polypath = values["-BDYFILE-"]
    buffer_radius =  values["-RADIUS-"]


    if values["-EASTING-"] and  values["-NORTHING-"] and values["-RADIUS-"]:
            buffer_radius = float(values["-RADIUS-"])
            point, buffer, buffer_feature = searcharea_frompoint(values["-EASTING-"], values["-NORTHING-"], buffer_radius)
            window["-DIALOGUE-"].update('point and buffer selected')

    elif values["-BDYFILE-"] and values["-RADIUS-"]:
            buffer_radius = float(values["-RADIUS-"])
            userpoly, buffer, buffer_feature = searcharea_frompoly(values["-BDYFILE-"], buffer_radius)
            window["-DIALOGUE-"].update('polygon and buffer selected')

    else:
        print('search area required')


    if values["-SPP-"] and event == "-PROCEED-":
            sppSearch, sppOutput = searchSpecies()

    else:
            print("there was an issue")
