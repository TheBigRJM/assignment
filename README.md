# egm722 programming for GIS and remote sensing
Script and data submission for assignment

## 1. What is the program for?
The purpose of this program is to provide a tool to automate spatial ecological data searches for use in environmental impact assessments. Ecological data searches are systematic but the required input and output information will vary between each search. Data searches are conducted using an input feature consisting of either a polygon, point or line and a specified distance buffer. The output requirements data searches also differ depending on the impacts which are being measured, for example some may require protectec species information OR nature connservation sites information OR both, or in some cases a subset of certain protected species groups.

The tool allows the user to input a grid reference, shapefile or mapinfo TAB file as the target location, specify a buffer radius (in metres) to generate their area of interest and select the output data required for the search.

## 2. Requirements and setup
Two methods have been provided to run the tool:

### 2.1 The standalone installer
This has been developed for users who simply wish to run the tool and do not wish to use git, conda or an IDE.

Download the 'standalone' zip folder to your desktop, unzip the folder and run the assignment.exe file. This should load a user interface with which the user can interact with the tool.

An instruction manual of how to use the tool provided in the download folder, detailing the requirements of each field and what to avoid to prevent errors.

### 2.2 Using git, conda and an Integrated Development Environment (IDE) of your choice. 

For users who wish to have access to the back-end script for debugging or adaptating, the program can also be run using the terminal in an IDE of your choice. This will load the GUI in the same way as the standalone installation but run through your IDE terminal rather than from an .exe file.

If you wish to use the tool in this way you will first need to install `git` and `conda, along with an IDE (if you don't already have these installed. The program was written using [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/#section=windows), I would recommend using this IDE.

Advice on [downloading](https://git-scm.com/downloads) and [installing git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [conda](https://docs.anaconda.com/anaconda/install/index.html) on your operating system. You may also wish to install [GitHub Desktop](https://desktop.github.com/) which will allow you to save your changes locally before commiiting them to your remote repository should you wish to adapt the script.
 
Once git and conda are installed you will need to fork the repository to your own git and clone this repository to locally to your computer. 

To fork the repository to your own git account you will need to login to github and click fork in the top right of the window which will copy the files to a new repository on your account for you to work with.

To clone Open github desktop on your pc and go to **File > Clone Repository** select **URL** and copy/paste the URL of **your** repository into the box. Alternatively, if you don't wish to install github desktop you can do this through gitbash (which should have been installed using the info above if you didn't already have this installed). Open gitbash using the start menu, navigate to the folder where you want to create a local repository for the files and enter `git clone https://github.com/TheBigRJM/assignment.git` to get the files.
 
Once you hhave the files locally you can now create the working environment using Anaconda using the environment.yml file provided in the repository. Open Anaconda Navigator and head to the environments tab and click on the import button at the bottom, click on the foler icon and navigate to the environment.yml file in your recently cloned folder. This should automatically populate the environment name. Click import, Anaconda should now begin installing the dependencies which the program needs to run. Alternatively you can use Anaconda cmd prompt to create the environment using: `C:\your\folder\path> conda env create -f environment.yml`.
 

## 3. Guidance and geographic use limitations based on sample data provided for demonstration.
As the size of the master datasets the program is designed to work with would be prohibitively large to supply for use, a sample of data has been provided to demonstrate the programs capabilities to the user. A copy of the sample data can be found in the SampleData folder. The dataset is restricted to a specific geographic area in Staffordshire. See the diagram below which details the extent of the datastes provided, the coordinates specified are in BNG (EPSG:27700) easting/northing format.


When using the tool with the example data the user must restrict input searches to this geographic area

image

By default 


## 3. Running the tool

The tool  has its own GUI and is intended to run as a standalone program using the .exe in the , but can also be run directly through the python terminal.
