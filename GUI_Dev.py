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
           [sg.Text("Grid Reference"),
            sg.Input(key="-EASTING-", enable_events=True),
            sg.Input(key="-NORTHING-", enable_events=True),
            sg.Text('-OR-'), sg.Text("Shapefile"),
            sg.Input(key="-BDYFILE-", enable_events=True),
            sg.FileBrowse()],
           [sg.Text("Search Radius (in metres)"), sg.Input(key="-RADIUS-", enable_events=True)],
           [sg.Text("Please specify a search area", key="-DIALOGUE-")],
           [sg.Text("Please specify search criteria", key="-SEARCHSTATUS-")]]


column2 = [[sg.Text("Select Search parameters")],
           [sg.Checkbox('Species', default=False, key="-SPP-", enable_events=True)],
           [sg.Checkbox('Bats only', default=False, key="-BATS-", enable_events=True)],
           [sg.Checkbox('GCN only', default=False, key="-GCN-", enable_events=True)],
           [sg.Checkbox('Invasives', default=False, key="-INV-", enable_events=True)],
           [sg.Checkbox('Sites', default=False, key="-SITES-", enable_events=True)],
           [sg.Checkbox('Species and Sites', default=False, key="-SITESSPP-", enable_events=True)]]

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

    # Attempt to convert datatypes for polygon searches
    #coordinates = userbuffer.geometry.apply(coord_lister)
    #coordinates = coordinates.tolist()
    #buffer_feature = Polygon(coordinates)

    bufferGeom = ShapelyFeature(userbuffer['geometry'], myCRS) # convert to shapely feature. INCORRECT FORMAT FOR INTERSECTS

    return userfile, userbuffer, bufferGeom


def coord_lister(geom):
    coords = list(geom.exterior.coords)
    return (coords)

def searchSpecies():
    """
    function to carry out a species search based on input parameters
    """
    df = specieslayer
    df1km = species1kmlayer
    # Run search on spp records <= 100m precision
    sppSearch = df[df.intersects(buffer_feature, align=True)]

    # Run 1km data species search
    spp1kmSearch = df1km[df1km.intersects(buffer_feature, align=True)]

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
    df = specieslayer
    df1km = species1kmlayer
    batrecs = df[df['InformalGr'] == 'mammal - bat']
    batSearch = batrecs[batrecs.intersects(buffer_feature, align=True)]

    batrecs1km = df1km[df1km['InformalGr'] == 'mammal - bat']
    batsearch1km = batrecs1km[batrecs1km.intersects(buffer_feature, align=True)]

    batConcat = pd.concat([batSearch, batsearch1km])

    # Remove extraneous columns for GDPR
    batOutput = batConcat[['SciName', 'CommonName', 'InformalGr', 'Location', 'LocDetail', 'GridRef', 'Grid1km',
                           'Date', 'Year', 'Source', 'SampleMeth', 'SexStage', 'RecType', 'EuProt', 'UKProt',
                           'PrincipalS', 'RareSpp', 'StatInvasi', 'StaffsINNS', 'RecordStat', 'Confidenti',
                           'Easting', 'Northing', 'Precision']]

    return batSearch, batOutput

def searchGCNs():
    """
    function to carry out a Great Crested Newt search based on input parameters
    """
    df = specieslayer
    df1km = species1kmlayer
    gcnrecs = df[df['CommonName'] == 'Great Crested Newt']
    gcnSearch = gcnrecs[gcnrecs.intersects(buffer_feature, align=True)]

    gcnrecs1km = df1km[df1km['CommonName'] == 'Great Crested Newt']
    gcnsearch1km = gcnrecs1km[gcnrecs1km.intersects(buffer_feature, align=True)]

    gcnConcat = pd.concat([gcnSearch, gcnsearch1km])

    # Remove extraneous columns for GDPR
    gcnOutput = gcnConcat[['SciName', 'CommonName', 'InformalGr', 'Location', 'LocDetail', 'GridRef', 'Grid1km',
                           'Date', 'Year', 'Source', 'SampleMeth', 'SexStage', 'RecType', 'EuProt', 'UKProt',
                           'PrincipalS', 'RareSpp', 'StatInvasi', 'StaffsINNS', 'RecordStat', 'Confidenti',
                           'Easting', 'Northing', 'Precision']]

    return gcnSearch, gcnOutput


def searchInvasive():
    """
    function to carry out an Invasive Species search based on input parameters
    """
    df = specieslayer
    invSearch = df[df.intersects(buffer_feature, align=True)]

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

#def savetoexcel():



# Load files to carry out searches on
dboundary = gpd.read_file('SampleData/SHP/SampleDataSelector_rectangle.shp')
specieslayer = gpd.read_file('SampleData/SHP/ProtSpp_font_point.shp')
species1kmlayer = gpd.read_file('SampleData/SHP/ProtSpp1km_region.shp')
sbilayer = gpd.read_file('SampleData/SHP/SBI_region.shp')
baslayer = gpd.read_file('SampleData/SHP/BAS_region.shp')


# Setup parameters
myCRS = ccrs.epsg(27700) # Matches the CRS of datafiles
# create empy axis
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))




# GUI event loop
while True:
    event, values = window.read()
    print(values)

    # Window close loop
    if event == sg.WIN_CLOSED or event=="-CANCEL-":
        print('User cancelled')
        break

    # Create buffer from user specified point
    if values["-EASTING-"] and  values["-NORTHING-"] and values["-RADIUS-"]:
            window["-DIALOGUE-"].update('Point and buffer selected')
            buffer_radius = float(values["-RADIUS-"])
            easting = float(values["-EASTING-"])
            northing = float(values["-NORTHING-"])
            point, userbuffer, buffer_feature = searcharea_frompoint(easting, northing, buffer_radius)
            point.plot(ax=ax, marker='*', color='red', markersize=2)
            userbuffer.plot(ax=ax, edgecolor='black')

    # Create buffer from user specified polygon
    elif values["-BDYFILE-"] and values["-RADIUS-"]:
            window["-DIALOGUE-"].update('polygon and buffer selected')
            buffer_radius = float(values["-RADIUS-"])
            userpoly, userbuffer, buffer_feature = searcharea_frompoly(values["-BDYFILE-"], buffer_radius)

    else:
        window["-DIALOGUE-"].update('Please specify a search area')


    # Search for all species in user created buffer
    if values["-SPP-"] and event == "-PROCEED-":
            sppSearch, sppOutput = searchSpecies()
            sppSearch.plot(ax=ax, color='indigo', edgecolor='black')
            window["-SEARCHSTATUS-"].update('Species search completed')

    elif values["-SPP-"]:
            window["-SEARCHSTATUS-"].update('Species search selected')

    else:
        if not values["-SPP-"]:
            window["-SEARCHSTATUS-"].update('Please specify search criteria')
        else:
            window["-SEARCHSTATUS-"].update('There was an issue')

    # Search for GCN only
    if values["-GCN-"] and event == "-PROCEED-":
        gcnSearch, gcnOutput = searchGCNs()
        window["-SEARCHSTATUS-"].update('Species search completed')

    elif values["-GCN-"]:
            window["-SEARCHSTATUS-"].update('GCN search selected')

    else:
        if not values["-GCN-"]:
            window["-SEARCHSTATUS-"].update('Please specify search criteria')
        else:
            window["-SEARCHSTATUS-"].update('There was an issue')

    # Search for Bats only
    if values["-BATS-"] and event == "-PROCEED-":
        batSearch, batOutput = searchBats()
        window["-SEARCHSTATUS-"].update('Species search completed')

    elif values["-BATS-"]:
            window["-SEARCHSTATUS-"].update('Bat search selected')

    else:
        if not values["-BATS-"]:
            window["-SEARCHSTATUS-"].update('Please specify search criteria')
        else:
            window["-SEARCHSTATUS-"].update('There was an issue')

# Search for invasive species only
#    if values["-INV-"] and event == "-PROCEED-":
#        batSearch, batOutput = searchBats()
#        window["-SEARCHSTATUS-"].update('Species search completed')
#
#   elif values["-INV-"]:
#            window["-SEARCHSTATUS-"].update('Bat search selected')
#
#    else:
#        if not values["-INV-"]:
#            window["-SEARCHSTATUS-"].update('Please specify search criteria')
#        else:
#            window["-SEARCHSTATUS-"].update('There was an issue')

    # Search for sites species only
    if values["-SITES-"] and event == "-PROCEED-":
        sbiIntersect, basIntersect = searchSites()
        window["-SEARCHSTATUS-"].update('Species search completed')

    elif values["-SITES-"]:
            window["-SEARCHSTATUS-"].update('Sites only search selected')

    else:
        if not values["-SITES-"]:
            window["-SEARCHSTATUS-"].update('Please specify search criteria')
        else:
            window["-SEARCHSTATUS-"].update('There was an issue')

    # Search for sites and species
    if values["-SITESSPP-"] and event == "-PROCEED-":
        sppSearch, sppOutput = searchSpecies()
        sbiIntersect, basIntersect = searchSites()
        window["-SEARCHSTATUS-"].update('Sites and species search completed')

    elif values["-SITESSPP-"] and values["-SPP-"]:
        window["-SEARCHSTATUS-"].update('Site and species search selected')

    else:
        if not values["-SITESSPP-"]:
            window["-SEARCHSTATUS-"].update('Please specify search criteria')
        else:
            window["-SEARCHSTATUS-"].update('There was an issue')