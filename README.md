# egm722 programming for GIS and remote sensing
script and data for assessment

## 1. What is the program for?
The purpose of this program is to automate spatial ecological data searches for use in environmental impact assessments. Data searches are systematic but the required input and output information will vary between each search. Generally data searches are conducted using an input feature consisting of either a polygon, point or line and a specified distance buffer. The data required as an output as part of the search also differs based on requirements for example looking for species OR nature connservation sites OR both, or possibly a subset of certain protected species for example.

This program allows the user to input a grid reference, shapefile or mapinfo TAB file as their area of interest, specify a buffer radius (in metres) and select the output data required for the search.

## 2. Guidance and geographic use limitations based on sample data provided for demonstration.
As the size of the master datasets the program is designed to work with would be prohibitively large to supply for use, a sample of data has been provided to demonstrate the programs capabilities to the user. A copy of the sample data can be found in the SampleData folder. The dataset is restricted to a specific geographic area in Staffordshire. See the diagram below which details the extent of the datastes provided, the coordinates specified are in BNG (EPSG:27700) easting/northing format.


When using the tool with the example data the user must restrict input searches to this geographic area

By default 


## 3. Running the tool

The tool  has its own GUI and is intended to run as a standalone program using the .exe in the , but can also be run directly through the python terminal.
