This is a set of Python tools to download tiles and convert them into an offline format compatible with QGIS or ArcMap. This isn't very user friendly and some knowledge of Python is required. 

**NB.** The use of this script may breach the terms and conditions of some web mapping services and may lead to you being 
blocked from accessing their services. You've been warned, use at your own risk.

**Installation**
For the tool itself no installation is required, just download or clone.

**Installing dependencies**
+ Install eventlet (essential) `sudo pip install eventlet`
+ Install mb-util (needed to exported MBTiles format)
+ Install Python Imaging Library (PIL) and GDAL (needed for GeoTiff export)



    + https://github.com/mapbox/mbutil
    + NB. Make sure to complete the step that makes mb-util avilable system-wide
    + Ubuntu
        + `sudo pip install PIL`
        + http://www.sarasafavi.com/installing-gdalogr-on-ubuntu.html
    + Windows
        + Install PIL through OSGEO4W
        + https://www.aubrett.com/article/information-technology/geospatial/gdal/install-osgeo4w


**Usage**
You will need to setup some job parameters before you start in the file **tilesets.py**. There are some examples in there already that should give you an idea of what is needed. Bounds can be found from Google Earth/Maps etc. You will also need to choose a provider. These are defined in **providers.py** and it is easy to add your own or update them as the details change over time.

There are 5 basic command options and all take the format: 
`python tile.py <tile-set-name> <output-folder> <command-option>`.
The tool will create a subfolder within this folder for each individual job.
    
+ `count_tiles` This will analyse the specified <tile-set-name> and output the number of tiles that need to be downloaded. Useful for check this is a sensible number before proceeding to download.
+ `download` This will attempt to download all the tiles in the specified <tile-set-name> into the output folder. It will output how many were successful. If a tile already exists it will be ignored, so it can safely be run again with the same paraeters if necessary. This process can take a while.
+ `clean_download` Looks for any malformed files in the downloaded tiles and delete them. If files are deleted, running `download` (manually) again will replace them (hopefully with better versions). This is dependent on the GNU `find` command so may need CYGWIN to run on Windows. It is checking for PNG files under 1kb in the file structure, so it may be possible to do this manually in Windows.  
+ `create_viewer` Creates a simple HTML page to view downloaded tiles in a web browser. Useful for checking if dowloads completed successfully and tiles are in the correct location. The HTML file is saved into the <output-folder-path>.
+ `mbtiles` Outputs an MBTiles file containing the downloaded tiles to the <output-folder-path>. This is the best option for viewing QGIS, giving original tile quality and very fast rendering performance at all zoom levels. This command has dependency on mb-util (see Installing dependencies). This process can take a while.
+ `geotiff` This is a fairly universal format that works well in QGIS and ArcMap. It is slow to generate and will create a very large temporary PNG during output. It has overview generation included so you should render with good performance, however sthere is a small loss in quality due to compression. This process can take a while.



**System resources & tile numbers**
The number of tiles can be huge. Size of area and zoom levels effect the number. Each zoom level has 4 times the number of tiles as the previous so things can get out of hand quickly! The generation of the GeoTiff will require a lot of system memory(RAM) if you are doing large areas at high zooms. Use the `count_tiles` tool.


**Windows Users**
This hasn't been tested on Windows, but I imagine everything should run if installed in an environment like OSGEO4W.




 
