# egm722 programming for GIS and remote sensing
Script and data submission for assignment

## 1. What is the program for?
The purpose of this program is to provide a tool to automate spatial ecological data searches for use in environmental impact assessments. Ecological data searches are systematic but the required input and output information will vary between each search. Data searches are conducted using an input feature consisting of either a polygon, point or line and a specified distance buffer. The output requirements data searches also differ depending on the impacts which are being measured, for example some may require protectec species information OR nature connservation sites information OR both, or in some cases a subset of certain protected species groups.

The tool allows the user to input a grid reference, shapefile or mapinfo TAB file as the target location, specify a buffer radius (in metres) to generate their area of interest and select the output data required for the search.

## 2. Requirements and setup

### Using git, conda and an Integrated Development Environment (IDE) of your choice. 

For users who wish to have access to the back-end script for debugging or adaptating, the program can also be run using the terminal in an IDE of your choice. This will load the GUI in the same way as the standalone installation but run through your IDE terminal rather than from an .exe file.

If you wish to use the tool in this way you will first need to install `git` and `conda, along with an IDE (if you don't already have these installed. The program was written using [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/#section=windows), I would recommend using this IDE.

Advice on [downloading](https://git-scm.com/downloads) and [installing git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [conda](https://docs.anaconda.com/anaconda/install/index.html) on your operating system. You may also wish to install [GitHub Desktop](https://desktop.github.com/) which will allow you to save your changes locally before commiiting them to your remote repository should you wish to adapt the script.
 
Once git and conda are installed you will need to fork the repository to your own git and clone this repository to locally to your computer. 

To fork the repository to your own git account you will need to login to github and click fork in the top right of the window which will copy the files to a new repository on your account for you to work with.

To clone Open github desktop on your pc and go to **File > Clone Repository** select **URL** and copy/paste the URL of **your** repository into the box. Alternatively, if you don't wish to install github desktop you can do this through gitbash (which should have been installed using the info above if you didn't already have this installed). Open gitbash using the start menu, navigate to the folder where you want to create a local repository for the files and enter `git clone https://github.com/TheBigRJM/assignment.git` to get the files.
 
Once you hhave the files locally you can now create the working environment using Anaconda using the environment.yml file provided in the repository. Open Anaconda Navigator and head to the environments tab and click on the import button at the bottom, click on the foler icon and navigate to the environment.yml file in your recently cloned folder. This should automatically populate the environment name. Click import, Anaconda should now begin installing the dependencies which the program needs to run. Alternatively you can use Anaconda cmd prompt to create the environment using: `C:\your\folder\path> conda env create -f environment.yml`. 

Once you have this setup you can then use an IDE of your choice to run the program using the newly created environment.

## 3. Guidance and geographic use limitations based on sample data provided for demonstration.
As the size of the master datasets the program is designed to work with would be prohibitively large to supply to demonstrate the tools function, a sample of data has been provided to demonstrate the programs capabilities to the user. A copy of the sample data can be found in the SampleData folder. The dataset is restricted to a specific geographic area in Staffordshire. See the diagram below which details the extent of the datastes provided, the coordinates specified are in BNG (EPSG:27700) easting/northing format.

The input fields will accept either easting/northing, standard BNG grid references (e.g. SK000000) or a user input file (SHP or TAB format, either point, line or polygon). An example polygon has been provided within the sample data folder to demonstrate the capability of the search function using a user file `SampleData/example search area/ExampleBoundarySearch_region.shp`.

As the sample dataset only has a restricted geographic range please limit your data searches please limit the inputs using the grid ref, easting/northing and polygon search capabilities to within these extents (using EPSG:27700, British National Grid coordinates):

https://gridreferencefinder.com/#gr=SJ8000030000|SJ800300|1,SJ8000040000|SJ800400|1,SJ9000030000|SJ900300|1,SJ9000040000|SJ900400|1

![SampleAreaCoordinates](https://user-images.githubusercontent.com/101205549/166978597-b46de77d-4817-4037-a23e-7b861344eefd.jpg)

## 4. Running the tool

If the repository is cloned to your locally using the instructions in step 2, the tool should be able to find the sample data without making any changes to to the body of code itself. If the elements of the repository have been downloaded separately and saved in separate locations you may need to redefine the file paths on lines 526-531 of the code to find these files to their file path on your machine.

First ensure your IDE is using the interpreter environment for this project (this should have been setup in step 2) the tool can then be loaded using the terminal in your IDE, within the terminal navigate to your local repository and type: `ipython RM_AssignmentScript.py`, this should open a separate python window called 'Data Search Enquiry'. The tool has been designed so that all the user interaction is done via a GUI as it will mainly be used by people with little or no experience of programming and is therefore more user friendly.

All user interaction should be done using the GUI and not using the terminal, however the terminal should not be closed as this will also close the GUI.

A full instruction manual detailing what the tool is doing and what information is required for each of the fields has also been provided within this repository.
