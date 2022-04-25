import numpy as np
import pandas as pd
import rasterio as rio
import geopandas as gpd
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString, Polygon, LinearRing
from shapely.ops import unary_union
import PySimpleGUI as sg
import bng


##### GUI #####
# Create GUI layout elements and structure

column1 = [[sg.Text("Enquiry number:"), sg.InputText(size=2, key="-ENQYEAR-"), sg.Text("/"),
            sg.InputText(size=3, key="-ENQNO-")],
           [sg.Text("----------------------------------------")],
           [sg.Text("Search from Grid Reference or Shapefile")],
           [sg.Text("Easting/Northing"),
            sg.Input(size=12, key="-EASTING-", enable_events=True),
            sg.Input(size=12, key="-NORTHING-", enable_events=True)],
            [sg.Text('-OR-')],
            [sg.Text("BNG Grid Reference"),
            sg.Input(size=12, key="-GRIDREF-", enable_events=True)],
            [sg.Text('-OR-')],
            [sg.Text("Shapefile"), sg.Input(size=30, key="-BDYFILE-", enable_events=True),
            sg.FileBrowse()],
            [sg.Text('-AND-')],
           [sg.Text("Search Radius (in metres)"), sg.Input(size=12, key="-RADIUS-", enable_events=True)],
           [sg.Text("Please specify a search area", text_color='red', key="-DIALOGUE-", enable_events=True)],
           [sg.Text("Please specify search parameters", text_color='red', key="-SEARCHSTATUS-", enable_events=True)]]


column2 = [[sg.Text('Select search parameters')],
           [sg.Checkbox('Species', default=False, key="-SPP-", enable_events=True)],
           [sg.Checkbox('Bats only', default=False, key="-BATS-", enable_events=True)],
           [sg.Checkbox('GCN only', default=False, key="-GCN-", enable_events=True)],
           [sg.Checkbox('Invasives', default=False, key="-INV-", enable_events=True)],
           [sg.Checkbox('Sites', default=False, key="-SITES-", enable_events=True)],
           [sg.Checkbox('Species and Sites', default=False, key="-SITESSPP-", enable_events=True)]]

layout = [[sg.Text('Enquiry creator tool')],
          [sg.Column(column1), sg.VSeparator(), sg.Column(column2)],
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

# TODO: bugfix the file conversion to run intersects between polybuffer and target data

    userfile = gpd.read_file(user_polypath) # import user selected file
    union = unary_union(userfile.geometry)
    userbuffer = gpd.GeoSeries(userfile.buffer(buffer_radius))  # buffer user file with user input buffer (for plotting)
    bufferGeom = union.buffer(buffer_radius) # Create shapely geometry to carry out intersects

    return userfile, userbuffer, bufferGeom


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



# GUI event loop
while True:
    event, values = window.read()
    print(values)

    # Window close loop
    if event == sg.WIN_CLOSED or event == "-CANCEL-":
        print('User cancelled')
        break

# TODO: add if statement to check and prompt the enquiry number
#   and reference for map title and filesaving

    # Only call map when proceed has been pressed
    if event == "-PROCEED-":
        # create empy axis
        fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# TODO: Add basemap to axis
# TODO: bugfix dialogue messages prompting user for input and parameter selection

    # Create buffer from user specified point
    if values["-EASTING-"] and values["-NORTHING-"] and values["-RADIUS-"]:
            window["-DIALOGUE-"].update('Point and buffer selected', text_color='green')
            buffer_radius = float(values["-RADIUS-"])
            easting = float(values["-EASTING-"])
            northing = float(values["-NORTHING-"])

            if event == "-PROCEED-":
                point, userbuffer, buffer_feature = searcharea_frompoint(easting, northing, buffer_radius)
                userbuffer.plot(ax=ax, color='none', edgecolor='black')
                point.plot(ax=ax, marker='*', color='red', markersize=20)

    # Create buffer from BNG grid reference
    elif values["-GRIDREF-"] and values["-RADIUS-"]:
            window["-DIALOGUE-"].update('Point and buffer selected', text_color='green')
            buffer_radius = float(values["-RADIUS-"])
            gridref = bng.to_osgb36(str(values["-GRIDREF-"]))
            easting = gridref[0]
            northing = gridref[1]

            if event == "-PROCEED-":
                point, userbuffer, buffer_feature = searcharea_frompoint(easting, northing, buffer_radius)
                userbuffer.plot(ax=ax, color='none', edgecolor='black')
                point.plot(ax=ax, marker='*', color='red', markersize=20)

    # Create buffer from user specified polygon
    elif values["-BDYFILE-"] and values["-RADIUS-"]:
            window["-DIALOGUE-"].update('polygon and buffer selected', text_color='green')
            buffer_radius = float(values["-RADIUS-"])

            if event == "-PROCEED-":
                userpoly, userbuffer, buffer_feature = searcharea_frompoly(values["-BDYFILE-"], buffer_radius)
                userpoly.plot(ax=ax, edgecolor='blue', color='none', hatch='//')
                userbuffer.plot(ax=ax, color='none', edgecolor='black')


    else:
        window["-DIALOGUE-"].update('Please specify a search area')


    # Search for all species in user created buffer
    if values["-SPP-"] and event == "-PROCEED-":
            sppSearch, sppOutput = searchSpecies()
            sppSearch.plot(ax=ax, color='indigo', edgecolor='black')
            window["-SEARCHSTATUS-"].update('Species search completed')

    elif values["-SPP-"]:
            window["-SEARCHSTATUS-"].update('Species search selected', text_color='green')

    else:
        if not values["-SPP-"]:
            window["-SEARCHSTATUS-"].update('Please specify search criteria')
        else:
            window["-SEARCHSTATUS-"].update('There was an issue')

    # Search for GCN only
    if values["-GCN-"] and event == "-PROCEED-":
        gcnSearch, gcnOutput = searchGCNs()
        gcnSearch.plot(ax=ax, marker='o', color='yellow', edgecolor='black')
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
        batSearch.plot(ax=ax, marker='^', color='blue', edgecolor='black')
        window["-SEARCHSTATUS-"].update('Species search completed')

    elif values["-BATS-"]:
            window["-SEARCHSTATUS-"].update('Bat search selected')

    else:
        if not values["-BATS-"]:
            window["-SEARCHSTATUS-"].update('Please specify search criteria')
        else:
            window["-SEARCHSTATUS-"].update('There was an issue')

# TODO: Import invasive layer and double check function to ensure this runs properly
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

    # Search for sites only
    if values["-SITES-"] and event == "-PROCEED-":
        sbiIntersect, basIntersect = searchSites()
        sbiIntersect.plot(ax=ax, color='green', alpha=0.5)
        basIntersect.plot(ax=ax, color='blue', alpha=0.5)
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
        sbiIntersect.plot(ax=ax, color='green', alpha=0.5)
        basIntersect.plot(ax=ax, color='blue', alpha=0.5)
        sppSearch.plot(ax=ax, color='indigo', edgecolor='black')
        window["-SEARCHSTATUS-"].update('Sites and species search completed')

    elif values["-SITESSPP-"]:
        window["-SEARCHSTATUS-"].update('Site and species search selected')

    else:
        if not values["-SITESSPP-"]:
            window["-SEARCHSTATUS-"].update('Please specify search criteria')
        else:
            window["-SEARCHSTATUS-"].update('There was an issue')