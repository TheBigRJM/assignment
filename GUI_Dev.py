import numpy as np
import pandas as pd
import rasterio as rio
import geopandas as gpd
import cartopy.crs as ccrs
import contextily as cx
from cartopy.feature import ShapelyFeature
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry import Point, LineString, Polygon, LinearRing
from shapely.ops import unary_union
import PySimpleGUI as sg
import bng


##### GUI #####
# Create GUI layout elements and structure

column1 = [[sg.Text("Enquiry number:"), sg.InputText(size=2, key="-ENQYEAR-"), sg.Text("/"),
            sg.InputText(size=3, key="-ENQNO-")],
           [sg.Text("Search area name:"), sg.InputText(size=50, key="-SITENAME-")],
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

# Declare functions from within the GUI
def searcharea_frompoint(xin, yin, buffer_radius):

    """
    Creates a point and buffer based on the user inputted arguments.

    point_x and point_y require pure easting and northing values.

    buffer_area value is in metres
    """

    userpoint = Point(xin, yin) # shapely geometry
    bufferGeom = userpoint.buffer(buffer_radius, resolution=50) # shapely geometry for running search

    # convert to geoseries for mapping in matplotlib
    userfeat = gpd.GeoSeries(Point(xin, yin)).set_crs(epsg=27700, inplace=True)
    userbuffer = gpd.GeoSeries(userfeat.buffer(buffer_radius, resolution=50)).set_crs(epsg=27700, inplace=True)

    return userfeat, userbuffer, bufferGeom


def searcharea_frompoly(user_polypath, buffer_radius):
    """ """


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
                           'Date', 'Year', 'Source', 'SampleMeth', 'SexStage', 'RecType', 'EuProt',
                           'UKProt', 'PrincipalS', 'RareSpp', 'StatInvasi', 'StaffsINNS', 'RecordStat', 'Confidenti',
                           'Easting', 'Northing', 'Precision']]


    return sppSearch, sppConcat, sppOutput

def sppstyle():
    sppSearch.plot(ax=ax, color='indigo', edgecolor='black')

    mammal = sppSearch[(sppSearch['InformalGr'] == 'mammal') & ~(sppSearch['CommonName'] == 'Otter')
                       & ~(sppSearch['CommonName'] == 'Water Vole') & ~(sppSearch['CommonName'] == 'Eurasian Badger')]\
        .plot(ax=ax, marker='^', color='none', edgecolor='red', linewidth=2)

    otter = sppSearch[sppSearch['CommonName'] == 'Otter']\
        .plot(ax=ax, marker='^', color='red', edgecolor='black')

    wv = sppSearch[sppSearch['CommonName'] == 'Water Vole']\
        .plot(ax=ax, marker='s', color='green', edgecolor='black')

    bats = sppSearch[sppSearch['InformalGr'] == 'mammal - bat']\
        .plot(ax=ax, marker='v', color='deepskyblue', edgecolor='black')

    birds = sppSearch[sppSearch['InformalGr'] == 'bird']\
        .plot(ax=ax, marker='v', color='deepskyblue', edgecolor='black')

    amrep = sppSearch[(sppSearch['InformalGr'] == 'amphibian') & (sppSearch['InformalGr'] == 'reptile')
                      & ~(sppSearch['CommonName'] == 'Great Crested Newt')]\
        .plot(ax=ax, marker='s', color='none', edgecolor='deepskyblue', linewidth=2)

    gcn = sppSearch[sppSearch['CommonName'] == 'Great Crested Newt']\
        .plot(ax=ax, marker='o', color='yellow', edgecolor='black')

    crayfish = sppSearch[sppSearch['CommonName'] == 'White-clawed Freshwater Crayfish']\
        .plot(ax=ax, marker='P', color='deepskyblue', edgecolor='black')

    plants = sppSearch[(sppSearch['InformalGr'] == 'flowering plant') & ~(sppSearch['ComonName'] == 'Bluebell')]\
        .plot(ax=ax, marker='v', color='none', edgecolor='green', linewidth=2)

    bluebell = sppSearch[sppSearch['CommonName'] == 'Bluebell']\
        .plot(ax=ax, marker='o', color='green', edgecolor='black')

    spptypes = [mammal, otter, wv, bats, birds, amrep, gcn, crayfish, plants, bluebell, lep, other]

    #for spptype in spptypes:
        #if spptype.empty == False:
            #spptype
            #print(spptype)

    return spptypes #mammal, otter, wv, bats, birds, amrep, gcn, crayfish, plants, bluebell, lep, other

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

    #MapTitle = 'bats map'

    return batSearch, batOutput#, MapTitle


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

    #MapTitle = 'Great Crested Newts map'

    return gcnSearch, gcnOutput#, MapTitle


def searchInvasive():
    '''
    function to carry out an Invasive Species search based on input parameters
    :return:
    '''

    df = invasivespecies
    df1km = invasivespecies1km
    # Run search on invasive species records <= 100m precision
    invSearch = df[df.intersects(buffer_feature, align=True)]

    # Run 1km data invasive species search
    inv1kmSearch = df1km[df1km.intersects(buffer_feature, align=True)]

    # Concatenate the 1km and <=100m invasive species records search results
    invConcat = pd.concat([sppSearch, inv1kmSearch])

    # Prepare output for excel export
    invOutput = invConcat[['SciName', 'CommonName', 'InformalGr', 'Location', 'LocDetail', 'GridRef', 'Grid1km',
                           'Date', 'Year', 'Source', 'SampleMeth', 'SexStage', 'RecType', 'EuProt', 'UKProt',
                           'PrincipalS', 'RareSpp', 'StatInvasi', 'StaffsINNS', 'RecordStat', 'Confidenti',
                           'Easting', 'Northing', 'Precision']]

    return invSearch, invOutput


def searchSites():
    '''
    function to carry out a nature conservation sites search based on input parameters
    note the buffer must be a shapely geometry feature as intersecting two GeoDataFrames requires equal indexes
    :return:
    '''

    sbiIntersect = sbilayer[sbilayer.intersects(buffer_feature, align=True)]
    basIntersect = baslayer[baslayer.intersects(buffer_feature, align=True)]

    #MapTitle = 'nature conservation sites map'

    return sbiIntersect, basIntersect#, MapTitle



#def savetoexcel():



# Load files to search from
dboundary = gpd.read_file('SampleData/SHP/SampleDataSelector_rectangle.shp')
specieslayer = gpd.read_file('SampleData/SHP/ProtSpp_font_point.shp')
species1kmlayer = gpd.read_file('SampleData/SHP/ProtSpp1km_region.shp')
sbilayer = gpd.read_file('SampleData/SHP/SBI_region.shp')
baslayer = gpd.read_file('SampleData/SHP/BAS_region.shp')
invasivespecies = gpd.read_file('SampleData/SHP/InvasiveSpp_font_point.shp')
invasivespecies1km = gpd.read_file('SampleData/SHP/InvasiveSpp1km_region.shp')

# Setup parameters
myCRS = ccrs.epsg(27700) # Set project CRS to British National Grid, matches the CRS of datafiles


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

    # Produce map plot
    if event == "-PROCEED-": # Only call map when proceed has been pressed
        # create empy axis
        fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))
        #cx.add_basemap(ax = ax, crs='epsg:27700', url=cx.providers.OpenStreetMap.Mapnik, zoom=15) # add openstreetmap basemap using contextily
        ax.add_artist(ScaleBar(1))


        # Create north arrow
        # (source: https://stackoverflow.com/questions/58088841/how-to-add-a-north-arrow-on-a-geopandas-map)
        x, y, arrow_length = 0.03, 0.98, 0.05
        ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
                    arrowprops=dict(facecolor='black', width=5, headwidth=15),
                    ha='center', va='center', fontsize=15,
                    xycoords=ax.transAxes)


# TODO: Add basemap to axis

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
            gridref = str(values["-GRIDREF-"])
            if len(gridref) % 2 == 1: # Handle errors with grid reference lengths
                sg.popup('not a valid grid reference length')
                continue
            else:
                gridref = bng.to_osgb36(gridref)
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

    else: # Reset prompt to ask user for search area
        window["-DIALOGUE-"].update('Please specify a search area', text_color='red')


    # Search for all species in user created buffer
    if values["-SPP-"] and event == "-PROCEED-":
        sppSearch, sppConcat, sppOutput = searchSpecies()
        sppstyle()
        #sppSearch.plot(ax=ax, color='indigo', edgecolor='black')
        plt.suptitle(values["-SITENAME-"] + ' species map', fontsize=16)
        window["-SEARCHSTATUS-"].update('Species search completed')

    if values["-SPP-"]:
        window["-SEARCHSTATUS-"].update('Species search selected', text_color='green')

#    else:
#        window["-SEARCHSTATUS-"].update('Please specify search parameters')


    # Search for GCN only
    if values["-GCN-"] and event == "-PROCEED-":
        gcnSearch, gcnOutput = searchGCNs()
        gcnSearch.plot(ax=ax, marker='o', color='yellow', edgecolor='black')
        plt.suptitle(values["-SITENAME-"] + ' Great Crested Newt map')
        window["-SEARCHSTATUS-"].update('Species search completed')

    if values["-GCN-"]:
        window["-SEARCHSTATUS-"].update('GCN search selected')

#    else:
#        window["-SEARCHSTATUS-"].update('Please specify search parameters')


    # Search for Bats only
    if values["-BATS-"] and event == "-PROCEED-":
        batSearch, batOutput = searchBats()
        batSearch.plot(ax=ax, marker='^', color='blue', edgecolor='black')
        plt.suptitle(values["-SITENAME-"] + ' bats map')
        window["-SEARCHSTATUS-"].update('Species search completed')

    if values["-BATS-"]:
        window["-SEARCHSTATUS-"].update('Bat search selected')

#    else:
#        window["-SEARCHSTATUS-"].update('Please specify search parameters')


# Search for invasive species only
    if values["-INV-"] and event == "-PROCEED-":
        invSearch, invOutput = searchInvasive()
        invSearch.plot(ax=ax, marker='.', color='black')
        window["-SEARCHSTATUS-"].update('Species search completed')

    elif values["-INV-"]:
            window["-SEARCHSTATUS-"].update('Bat search selected')

#    else:
#            window["-SEARCHSTATUS-"].update('Please specify search criteria')

    # Search for sites only
    if values["-SITES-"] and event == "-PROCEED-":
        sbiIntersect, basIntersect = searchSites()
        sbiIntersect.plot(ax=ax, color='green', alpha=0.5)
        basIntersect.plot(ax=ax, color='blue', alpha=0.5)
        plt.suptitle(values["-SITENAME-"] + ' protected species and nature conservation sites map')
        window["-SEARCHSTATUS-"].update('Species search completed')

    if values["-SITES-"]:
        window["-SEARCHSTATUS-"].update('Sites only search selected')

#    else:
#            window["-SEARCHSTATUS-"].update('Please specify search parameters')


    # Search for sites and species
    if values["-SITESSPP-"] and event == "-PROCEED-":
        sppSearch, sppOutput = searchSpecies()
        sbiIntersect, basIntersect = searchSites()
        sbiIntersect.plot(ax=ax, color='green', alpha=0.5)
        basIntersect.plot(ax=ax, color='blue', alpha=0.5)
        sppSearch.plot(ax=ax, color='indigo', edgecolor='black')
        window["-SEARCHSTATUS-"].update('Sites and species search completed')

    if values["-SITESSPP-"]:
        window["-SEARCHSTATUS-"].update('Sites and species search selected')

    valuelist = [values]

    if valuelist == [None]:
       window["-SEARCHSTATUS-"].update('Please specify search parameters', text_color='red')