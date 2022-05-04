import numpy as np
import pandas as pd
import rasterio as rio
from rasterio.merge import merge
import geopandas as gpd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry import Point
from shapely.ops import unary_union
import PySimpleGUI as sg
import bng
from pathlib import Path
from datetime import date


# Create GUI layout elements and structure

year = date.today().year  # Get current year
tdyr = int(str(year)[2:4])  # Cut current year value into 2 digits

sg.theme('LightGreen')

# Specify values for first column of GUI
column1 = [[sg.Text("Enquiry number:"), sg.InputText(default_text=tdyr, size=2, key="-ENQYEAR-"), sg.Text("/"),
            sg.InputText(size=3, key="-ENQNO-")],
           [sg.Text("Search area name:"), sg.InputText(size=50, key="-SITENAME-")],
           [sg.Text("Specify output file directory:"), sg.Input(size=40, key="-OUTFOLDER-", enable_events=True),
            sg.FolderBrowse()],
           [sg.Text("----------------------------------------")],
           [sg.Text("Search from Grid Reference or Shapefile", font=("Helvectica", 15))],
           [sg.Text("Easting/Northing"),
            sg.Input(size=12, key="-EASTING-", enable_events=True),
            sg.Input(size=12, key="-NORTHING-", enable_events=True)],
           [sg.Text('-OR-')],
           [sg.Text("BNG Grid Reference"),
            sg.Input(size=12, key="-GRIDREF-", enable_events=True)],
           [sg.Text('-OR-')],
           [sg.Text("Shapefile"), sg.Input(size=30, key="-BDYFILE-", enable_events=True),
            sg.FileBrowse(file_types=(("Shapefile", "*.SHP"), ("MapInfo TAB", "*.TAB"),))],
           [sg.Text('-AND-')],
           [sg.Text("Search Radius (in metres)"), sg.Input(size=12, key="-RADIUS-", enable_events=True)],
           [sg.Text("Please specify a search area", text_color='red', key="-DIALOGUE-", enable_events=True)]]

# Specify values for second column of GUI
column2 = [[sg.Text('Select search parameters', font=("Helvetica", 15))],
           [sg.Checkbox('Species', default=False, key="-SPP-", enable_events=True)],
           [sg.Checkbox('Bats only', default=False, key="-BATS-", enable_events=True)],
           [sg.Checkbox('GCN only', default=False, key="-GCN-", enable_events=True)],
           [sg.Checkbox('Invasives', default=False, key="-INV-", enable_events=True)],
           [sg.Checkbox('Sites', default=False, key="-SITES-", enable_events=True)],
           [sg.Checkbox('Species and Sites', default=False, key="-SITESSPP-", enable_events=True)],
           [sg.Text("Please specify search parameters", text_color='red', key="-SEARCHSTATUS-", enable_events=True)]]

# Define the GUI layout
layout = [[sg.Text('Ecological data enquiry tool', font=("Helvetica", 25))],
          [sg.Text('A tool for the production of ecological data searches', font=("helvetica", 12))],
          [sg.Text('Specify a search area and radius on the left and select the parameters for the search on the right.'
                   ' The tool will produce a JPEG map and excel spreadsheets of the results and save them '
                   'in the specified folder.',
                   size=(100, 3), font=("helvetica", 12))],
          [sg.Column(column1), sg.VSeparator(), sg.Column(column2)],
          [sg.Button('Proceed', key="-PROCEED-"), sg.CloseButton('Cancel', key="-CANCEL-")]]

# Build the GUI window
window = sg.Window("Data Search Enquiry", layout, margins=(50, 50))


# Declare functions from within the GUI
# noinspection PyUnboundLocalVariable
def rastermosaic():
    """
    Returns a mosaic of raster tiles to form the basemap for the map plot. Only required to run once to produce
    the basemap, once this is produced the function is no longer required.
    :return:
    """

    path = Path('SampleData/basemaps/')  # folder path to basemap tifs
    Path('output').mkdir(parents=True, exist_ok=True)  # create output directory
    output_path = 'output/mosaic.tif'  # assign output path to variable

    raster_files = list(path.iterdir())  # iterate over the tifs in the directory
    raster_to_mosiac = []  # create empty list to hold tif names

    for p in raster_files:  # loop through raster files in folder and append to one another in empty list defined above
        bm = rio.open(p)
        raster_to_mosiac.append(bm)

    mosaic, output = merge(raster_to_mosiac)  # Merge tifs in folder together using populated list

    output_meta = bm.meta.copy()  # create a copy of each rasters metadata

    output_meta.update(  # update the metadata values to match values of the mosaic
        {"driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": output,
            "crs": "EPSG:27700"})

    # write mosaic to folder
    with rio.open(output_path, mode='w', ** output_meta) as m:
        m.write(mosaic)

    return output_path


def searcharea_frompoint(xin, yin, buffer_radius):

    """
    Creates a point and buffer based on the user inputted arguments.

    point_x and point_y require pure easting and northing values.

    buffer_area value is in metres

    :arg xin easting values as int or flt

    :arg yin northing values as int or flt

    :arg buffer_radius required buffer in metres, value as either int or flt
    """

    userpoint = Point(xin, yin)  # shapely geometry
    bufferGeom = userpoint.buffer(buffer_radius, resolution=50)  # shapely geometry for running search

    # Convert to geoseries for mapping in matplotlib
    userfeat = gpd.GeoSeries(Point(xin, yin)).set_crs(epsg=27700, inplace=True)
    userbuffer = gpd.GeoSeries(userfeat.buffer(buffer_radius, resolution=50)).set_crs(epsg=27700, inplace=True)

    # Plot the point and buffer
    userbuffer.plot(ax=ax, color='none', edgecolor='red')
    userfeat.plot(ax=ax, marker='*', color='red', markersize=20)

    # Create handles for legend
    userpoint_handle = mlines.Line2D([], [], linestyle='None', marker='*', color='red', label='User point')
    userbuffer_handle = mpatches.Patch(facecolor='None', edgecolor='red', label='Search buffer')

    # Combine legend items
    input_handles = [userpoint_handle, userbuffer_handle]

    return userfeat, userbuffer, bufferGeom, input_handles


def searcharea_frompoly(user_polypath, buffer_radius):
    """
    docstring
    """

    userfile = gpd.read_file(user_polypath)  # import user selected file
    union = unary_union(userfile.geometry)
    userbuffer = gpd.GeoSeries(userfile.buffer(buffer_radius))  # buffer user file with user input buffer (for plotting)
    bufferGeom = union.buffer(buffer_radius)  # Create shapely geometry to carry out intersects

    userpoly.plot(ax=ax, edgecolor='blue', color='none', hatch='//')
    userbuffer.plot(ax=ax, color='none', edgecolor='red', linewidth=1.5)

    userpoly_handle = mpatches.Patch(facecolor='None', hatch='//', edgecolor='blue',
                                     label='Search area')

    userbuffer_handle = mpatches.Patch(facecolor='None', edgecolor='red',
                                       label='Search buffer')

    input_handles = [userpoly_handle, userbuffer_handle]

    return userfile, userbuffer, bufferGeom, input_handles


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
    """
    docstring
    :return:
    """

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
        .plot(ax=ax, marker='o', color='None', edgecolor='yellow', linewidth=2)

    amrep = sppSearch[(sppSearch['InformalGr'] == 'amphibian') & (sppSearch['InformalGr'] == 'reptile')
                      & ~(sppSearch['CommonName'] == 'Great Crested Newt')]\
        .plot(ax=ax, marker='s', color='none', edgecolor='deepskyblue', linewidth=2)

    gcn = sppSearch[sppSearch['CommonName'] == 'Great Crested Newt']\
        .plot(ax=ax, marker='o', color='yellow', edgecolor='black')

    crayfish = sppSearch[sppSearch['CommonName'] == 'White-clawed Freshwater Crayfish']\
        .plot(ax=ax, marker='P', color='deepskyblue', edgecolor='black')

    plants = sppSearch[(sppSearch['InformalGr'] == 'flowering plant') & ~(sppSearch['CommonName'] == 'Bluebell')]\
        .plot(ax=ax, marker='v', color='none', edgecolor='green', linewidth=2)

    bluebell = sppSearch[sppSearch['CommonName'] == 'Bluebell']\
        .plot(ax=ax, marker='o', color='green', edgecolor='black')

    # Create proxy artist entries to create legend list

    mammal_handle = mlines.Line2D([], [], marker='^', color='None', markeredgecolor='red', markeredgewidth=2,
                                  linestyle='None', label='Mammal')

    otter_handle = mlines.Line2D([], [], marker='^', color='red', markeredgecolor='black',
                                 linestyle='None', label='Otter')

    wv_handle = mlines.Line2D([], [], marker='s', color='green', markeredgecolor='black',
                              linestyle='None', label='Water Vole')

    bats_handle = mlines.Line2D([], [], marker='v', color='deepskyblue', markeredgecolor='black',
                                linestyle='None', label='Bats')

    birds_handle = mlines.Line2D([], [], marker='o', color='None', markeredgecolor='yellow', markeredgewidth=2,
                                 linestyle='None', label='Birds')

    amrep_handle = mlines.Line2D([], [], marker='s', color='none', markeredgecolor='deepskyblue',
                                 linestyle='None', markeredgewidth=2, label='Amphibians and Reptiles')

    gcn_handle = mlines.Line2D([], [], marker='o', color='yellow', markeredgecolor='black',
                               linestyle='None', label='Great Crested Newt')

    crayfish_handle = mlines.Line2D([], [], marker='P', color='deepskyblue', markeredgecolor='black',
                                    linestyle='None', label='White-Clawed Crayfish')

    plants_handle = mlines.Line2D([], [], marker='v', color='none', markeredgecolor='green',
                                  linestyle='None', markeredgewidth=2, label='Plant')

    bluebell_handle = mlines.Line2D([], [], marker='o', color='green', markeredgecolor='black',
                                    linestyle='None', label='Bluebell')

    spptypes = [mammal, otter, wv, bats, birds, amrep, gcn, crayfish, plants, bluebell]  # lep, other

    spplegend = [mammal_handle, otter_handle, wv_handle, bats_handle, birds_handle, amrep_handle, gcn_handle,
                 crayfish_handle, plants_handle, bluebell_handle]


# TODO: add in way of catching zero result species + 'other' species

    return spptypes, spplegend


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


    bats_handle = mlines.Line2D([], [], marker='v', color='deepskyblue', markeredgecolor='black',
                                linestyle='None', label='Bats')

    bats_handle = [bats_handle]

    return batSearch, batOutput, bats_handle


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

    gcn_handle = mlines.Line2D([], [], marker='o', color='yellow', markeredgecolor='black',
                               linestyle='None', label='Great Crested Newt')

    gcn_handle = [gcn_handle]

    return gcnSearch, gcnOutput, gcn_handle


def searchInvasive():
    """
    function to carry out an Invasive Species search based on input parameters
    :return:
    """

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
    """
    function to carry out a nature conservation sites search based on input parameters
    note the buffer must be a shapely geometry feature as intersecting two GeoDataFrames requires equal indexes
    :return:
    """

    # Search for sites which intersect the buffer area
    sbiIntersect = sbilayer[sbilayer.intersects(buffer_feature, align=True)]
    basIntersect = baslayer[baslayer.intersects(buffer_feature, align=True)]

    # Concatenate the two search results
    sitesConcat = pd.concat([sbiIntersect, basIntersect])

    # Remove extraneous columns for GDPR
    sitesOutput = sitesConcat[['SiteID', 'SiteName', 'Status', 'Year', 'Abstract']]

    # Plot the sites on the map
    sbiIntersect.plot(ax=ax, color='None', hatch='.....', edgecolor='green')
    basIntersect.plot(ax=ax, color='None', hatch='.....', edgecolor='deepskyblue')

    #  Add site labels (https://stackoverflow.com/questions/38899190/geopandas-label-polygons)
    sbiIntersect.apply(lambda x: ax.annotate(text=x['SiteID'], size=8, color='green', weight='bold',
                                             xy=x.geometry.centroid.coords[0], ha='center'), axis=1)

    basIntersect.apply(lambda x: ax.annotate(text=x['SiteID'], size=8, color='deepskyblue', weight='bold',
                                             xy=x.geometry.centroid.coords[0], ha='center'), axis=1)

    # create legend items
    sbi_handle = mpatches.Patch(facecolor='None', hatch='.....', edgecolor='green',
                                label='Site of Biological Importance')
    bas_handle = mpatches.Patch(facecolor='None', hatch='.....', edgecolor='deepskyblue',
                                label='Biodiversity Alert Site')

    # list legend items to plot
    site_handles = [sbi_handle, bas_handle]

    return sbiIntersect, basIntersect, site_handles, sitesOutput


def load_basemap(filepath):
    """
    This is where you should write a docstring.
    """
    with rio.open(filepath) as dataset:
        img = dataset.read()
        bmxmin, bmymin, bmxmax, bmymax = dataset.bounds

    dispimg = img.copy().astype(np.float32)
    dispimg = dispimg.transpose([1, 2, 0])

    return bmxmin, bmymin, bmxmax, bmymax, dispimg

# Load files to search from
dboundary = gpd.read_file('SampleData/SHP/SampleDataSelector_rectangle.shp')
specieslayer = gpd.read_file('SampleData/SHP/ProtSpp_font_point.shp')
species1kmlayer = gpd.read_file('SampleData/SHP/ProtSpp1km_region.shp')
sbilayer = gpd.read_file('SampleData/SHP/SBI_region.shp')
baslayer = gpd.read_file('SampleData/SHP/BAS_region.shp')
invasivespecies = gpd.read_file('SampleData/SHP/InvasiveSpp_font_point.shp')
invasivespecies1km = gpd.read_file('SampleData/SHP/InvasiveSpp1km_region.shp')

# Setup CRS of the axis
myCRS = ccrs.epsg(27700)  # Set project CRS to British National Grid, matches the CRS of datafiles

# load basemap
# return extent values from load_basemap function
bmxmin, bmymin, bmxmax, bmymax, basemap = load_basemap('output/mosaic.tif')
# plot basemap using extents
basemap_kwargs = {'extent': [bmxmin, bmxmax, bmymin, bmymax], 'transform': myCRS}







# Begin GUI event loop

while True: # Create an infinite loop which the GUI runs inside.
    event, values = window.read()  # Read the layout detailed above and display as a window, track events and values
    print(values)  # Prints the selected values to the console for debugging and error checking

    # Window close loop
    if event == sg.WIN_CLOSED or event == "-CANCEL-":
        print('User cancelled')
        break

    # Check to see if the buffer radius is an integer to prevent early error termination
    if values["-RADIUS-"]:
        text = values["-RADIUS-"]
        try:
            value = int(text)
            print(f'Integer: {value}')
        except:
            print("Not Integer")
            sg.popup('buffer must be an integer value')
            continue

    if values["-ENQNO-"] == '' and event == "-PROCEED-":
        sg.popup('enquiry number required')
        continue

    if values["-SITENAME-"] == '' and event == "-PROCEED-":
        sg.popup('site name required')
        continue

    if values["-OUTFOLDER-"] == '' and event == "-PROCEED-":
        sg.popup('output location required')
        continue

    # First produce map plot and map furniture if the user clicks proceed
    if event == "-PROCEED-":  # Only call map when proceed has been pressed
        # create empy axis
        cm = 1/2.54  # convert inches to cm to create A4 plot size
        fig, ax = plt.subplots(1, 1, figsize=(21*cm, 29.7*cm), subplot_kw=dict(projection=myCRS))
        ax.imshow(basemap, **basemap_kwargs, cmap='gray')
        ax.add_artist(ScaleBar(1))  # Add scalebar
        # Add gridlines - NOTE: currently epsg projections not supported in cartopy 0.18.
        gridlines = ax.gridlines(draw_labels=True)
        gridlines.right_labels = False
        gridlines.bottom_labels = False

        # Create north arrow
        # (source: https://stackoverflow.com/questions/58088841/how-to-add-a-north-arrow-on-a-geopandas-map)
        x, y, arrow_length = 0.03, 0.98, 0.05
        ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
                    arrowprops=dict(facecolor='black', width=5, headwidth=15),
                    ha='center', va='center', fontsize=15,
                    xycoords=ax.transAxes)
        plt.tight_layout()

# TODO: Add basemap to axis

    # Create buffer from user specified point
    if values["-EASTING-"] and values["-NORTHING-"] and values["-RADIUS-"]:
        window["-DIALOGUE-"].update('Point and buffer selected', text_color='green')
        buffer_radius = float(values["-RADIUS-"])
        easting = float(values["-EASTING-"])
        northing = float(values["-NORTHING-"])

        if event == "-PROCEED-":
            point, userbuffer, buffer_feature, input_handles = searcharea_frompoint(easting, northing, buffer_radius)
            xmin, ymin, xmax, ymax = buffer_feature.bounds
            # set the extent of the frame, give a 200m buffer to avoid being tight to edge of buffer feature
            ax.set_extent([(xmin-200), (xmax+200), (ymin-200), (ymax+200)], crs=myCRS)

    # Create buffer from BNG grid reference
    elif values["-GRIDREF-"] and values["-RADIUS-"]:
        window["-DIALOGUE-"].update('Point and buffer selected', text_color='green')
        buffer_radius = float(values["-RADIUS-"])
        gridref = str(values["-GRIDREF-"])
        if len(gridref) % 2 == 1:  # Handle errors with invalid grid reference lengths
            sg.popup('not a valid grid reference length')
            continue
        else:
            gridref = bng.to_osgb36(gridref)  # convert the grid ref to easting & northing values
            easting = gridref[0]  # get easting from grid ref
            northing = gridref[1]  # get northing from grid ref

        if event == "-PROCEED-":
            point, userbuffer, buffer_feature, input_handles = searcharea_frompoint(easting, northing, buffer_radius)
            xmin, ymin, xmax, ymax = buffer_feature.bounds
            # set the extent of the frame, give a 200m buffer to avoid being tight to edge of buffer feature
            ax.set_extent([(xmin-200), (xmax+200), (ymin-200), (ymax+200)], crs=myCRS)

    # Create buffer from user specified polygon
    elif values["-BDYFILE-"] and values["-RADIUS-"]:
        window["-DIALOGUE-"].update('polygon and buffer selected', text_color='green')
        buffer_radius = float(values["-RADIUS-"])

        if event == "-PROCEED-":
            userpoly, userbuffer, buffer_feature, input_handles = \
                    searcharea_frompoly(values["-BDYFILE-"], buffer_radius)
            xmin, ymin, xmax, ymax = buffer_feature.bounds
            # set the extent of the frame, give a 200m buffer to avoid being tight to edge of buffer feature
            ax.set_extent([(xmin-200), (xmax+200), (ymin-200), (ymax+200)], crs=myCRS)

    else:  # Reset prompt to ask user for search area
        window["-DIALOGUE-"].update('Please specify a search area', text_color='red')

    # Search for all protected species in user created buffer
    if values["-SPP-"] and event == "-PROCEED-":
        sppSearch, sppConcat, sppOutput = searchSpecies()
        spptypes, spplabels = sppstyle()
        handles = input_handles + spplabels
        leg = fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, 0),
                         title='Legend', title_fontsize=14, ncol=4, fontsize=10, frameon=True, framealpha=1)
        plt.suptitle(values["-SITENAME-"] + ' species map', fontsize=16)
        # Save output to excel file in user specified folder
        sppOutput.to_excel(values["-OUTFOLDER-"] + '/' + values["-ENQNO-"] + '_SpeciesSearchResults.xlsx')
        # Update window to tell user search was completed
        window["-SEARCHSTATUS-"].update('Species search completed')

    elif values["-SPP-"]:
        window["-SEARCHSTATUS-"].update('Species search selected', text_color='green')

    # Search for GCN only
    if values["-GCN-"] and event == "-PROCEED-":
        gcnSearch, gcnOutput, gcn_labels = searchGCNs()
        handles = input_handles + gcn_labels
        gcnSearch.plot(ax=ax, marker='o', color='yellow', edgecolor='black')
        leg = fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.05), title='Legend',
                         title_fontsize=14, ncol=3, fontsize=10, frameon=True, framealpha=1)
        plt.suptitle(values["-SITENAME-"] + ' Great Crested Newt map')
        # Save output to excel file in user specified folder
        gcnOutput.to_excel(values["-OUTFOLDER-"] + '/' + values["-ENQNO-"] + '_GCNSearchResults.xlsx')
        # Update window to tell user search was completed
        window["-SEARCHSTATUS-"].update('Species search completed', text_color='green')

    elif values["-GCN-"]:
        window["-SEARCHSTATUS-"].update('GCN search selected', text_color='green')

    # Search for Bats only
    if values["-BATS-"] and event == "-PROCEED-":
        batSearch, batOutput, bat_labels = searchBats()
        handles = input_handles + bat_labels
        batSearch.plot(ax=ax, marker='^', color='deepskyblue', edgecolor='black')
        leg = fig.legend(handles=bat_labels, title='Legend', title_fontsize=14, ncol=3,
                         fontsize=10, loc='lower center', frameon=True, framealpha=1)
        plt.suptitle(values["-SITENAME-"] + ' bats map')
        # Save output to excel file in user specified folder
        batOutput.to_excel(values["-OUTFOLDER-"] + '/' + values["-ENQNO-"] + '_BatsSearchResults.xlsx')
        # Update window to tell user search was completed
        window["-SEARCHSTATUS-"].update('Species search completed', text_color='green')

    elif values["-BATS-"]:
        window["-SEARCHSTATUS-"].update('Bat search selected', text_color='green')

    # Search for invasive species only - note these are not supposed to plot to map
    if values["-INV-"] and event == "-PROCEED-":
        invSearch, invOutput = searchInvasive()
        # invSearch.plot(ax=ax, marker='.', color='black')
        # Save output to excel file in user specified folder
        invOutput.to_excel(values["-OUTFOLDER-"] + '/' + values["-ENQNO-"] + '_InvasiveSearchResults.xlsx')
        # Update window to tell user search was completed
        window["-SEARCHSTATUS-"].update('Species search completed', text_color='green')

    elif values["-INV-"]:
        window["-SEARCHSTATUS-"].update('Bat search selected', text_color='green')

    # Search for sites only
    if values["-SITES-"] and event == "-PROCEED-":
        sbiIntersect, basIntersect, site_labels, sitesOutput = searchSites()
        handles = input_handles + site_labels
        leg = fig.legend(handles=handles, title='Legend', title_fontsize=14, ncol=3,
                         fontsize=10, loc='lower center', frameon=True, framealpha=1)
        plt.suptitle(values["-SITENAME-"] + ' nature conservation sites map')
        # Save output to excel file in user specified folder
        sitesOutput.to_excel(values["-OUTFOLDER-"] + '/' + values["-ENQNO-"] + '_SitesSearchResults.xlsx')
        # Update window to tell user search was completed
        window["-SEARCHSTATUS-"].update('Species search completed', text_color='green')

    elif values["-SITES-"]:
        window["-SEARCHSTATUS-"].update('Sites only search selected', text_color='green')

    # Search for sites and species
    if values["-SITESSPP-"] and event == "-PROCEED-":
        sppSearch, sppConcat, sppOutput = searchSpecies()  # run spp search
        spptypes, spplabels = sppstyle()  # plot spp, style and return labels
        sbiIntersect, basIntersect, sites_labels, sitesOutput = searchSites()  # sites search, plot, return handles
        handles = input_handles + sites_labels + spplabels  # Create list of spp and sites handles
        # Create legend
        leg = fig.legend(handles=handles, title='Legend', title_fontsize=14, ncol=3,
                         fontsize=10, loc='lower center', frameon=True, framealpha=1)
        plt.suptitle(values["-SITENAME-"] + ' protected species and nature conservation sites map')

        # Save output to excel file in user specified folder
        sppOutput.to_excel(values["-OUTFOLDER-"] + '/' + values["-ENQNO-"] + '_SpeciesSearchResults.xlsx')
        # Save output to excel file in user specified folder
        sitesOutput.to_excel(values["-OUTFOLDER-"] + '/' + values["-ENQNO-"] + '_SitesSearchResults.xlsx')
        # Update window to tell user search was completed
        window["-SEARCHSTATUS-"].update('Sites and species search completed', text_color='green')

    elif values["-SITESSPP-"]:
        window["-SEARCHSTATUS-"].update('Sites and species search selected', text_color='green')

    valuelist = [values]

    if valuelist == [None]:
        window["-SEARCHSTATUS-"].update('Please specify search parameters', text_color='red')

    # Save the map to user specified folder
    if event == "-PROCEED-":
        fig.savefig(values["-OUTFOLDER-"] + '/' + values["-ENQNO-"] + 'map.jpeg', bbox_inches='tight', dpi=300)
