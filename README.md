## A Python tool to download map tiles and convert them into an offline format compatible with QGIS or ArcMap.

Created to help teams responding to natural disasters in the Philippines, giving them access to aerial imagery in tools like QGIS during during periods of disruption to internet services.

The tool is not user friendly and some knowledge of Python is required. Due to the nature of the script it is unlikely to work out of the box, as things such as provider details may change over time. So be prepared to do a little tweaking.

NB. The use of this script may breach the terms and conditions of some web mapping services and may lead to you being blocked from accessing their services. You've been warned, read the t&cs and use at your own risk.

## Installation
For the tool itself no installation is required, just download or clone.
  + https://github.com/tmcadam/tile-stitching/archive/master.zip
  + ```git clone https://github.com/tmcadam/tile-stitching.git```

## Installing dependencies
+ Install eventlet (essential) `sudo pip install eventlet`
+ Install mb-util (needed to exported MBTiles format)
    + https://github.com/mapbox/mbutil
    + NB. Make sure to complete the step that makes mb-util avilable system-wide
+ Install Python Imaging Library (PIL) and GDAL (needed for GeoTiff export)
    + Ubuntu
        + `sudo pip install PIL`
        + http://www.sarasafavi.com/installing-gdalogr-on-ubuntu.html
    + Windows
        + Install PIL through OSGEO4W
        + https://www.aubrett.com/article/information-technology/geospatial/gdal/install-osgeo4w

## Usage
The first step is to setup job parameters in the file **tilesets.py**. There are some examples in there already that should give you an idea of what is needed. Bounds can be found from Google Earth/Maps etc. A provider must be selected. These are defined in **providers.py** and it is easy to add your own or update them, as the details will likely change over time.

There are 7 commands and all take the format: `python tile.py <tileset-name> <output-directory> <command>`. The tool will create a sub-directory within this folder for each individual job.

e.g. `python tile.py sample2 "/home/bob/Tiles" download`    

+ `count_tiles` Analyses the specified <tileset-name> and output the number of tiles that need to be downloaded. Useful for check this is a sensible number before proceeding to download.
+ `download` Attempts to download all the tiles in the specified <tile-set-name> into the output folder. It will output how many were successful. If a tile already exists it will be ignored, so it can safely be run again with the same parameters if necessary. This process can take a while.
+ `proxy_download` Downloads all tiles similar to downloads, but uses proxies/VPNs. See below for more details on set up.
+ `clean_download` Looks for any malformed files in the downloaded tiles and deletes them. If files are deleted, running `download` or `proxy_download` (manually) again will replace them (hopefully with correct versions).  
+ `create_viewer` Creates a simple HTML page to view downloaded tiles in a web browser. Useful for checking if downloads completed successfully and tiles are in the correct location globally. The HTML file is saved into the `<output-directory>`.
+ `mbtiles` Outputs an MBTiles file containing the downloaded tiles to the `<output-directory>`. This is the best option for QGIS users, giving original tile quality and very fast rendering performance at all zoom levels. This command has a dependency on mb-util (see Installing dependencies).
+ `geotiff` Outputs a GeoTiff file to the `<output-directory>`, this is a fairly universal format that works well with QGIS and ArcMap. It is slow to generate and will create a very large temporary PNG during output. It includes overview generation so they should render in GIS with good performance, however there is a small loss in quality due to compression. There is a dependency on PIL and gdal (see Installing dependencies).

## Proxy downloads
Using the `proxy_download` command requires some additional setup, and will likely only work on Ubuntu, as it is calling system commands(`nmcli`) to modify network settings. The command randomly picks a proxy/VPN connection from a pool then swaps to another connection after a set number of tiles have been downloaded or blocking occurs. The pool of proxies/VPNs is defined in `connections.py`. These VPN connections must be already set up on the machine running the script and have stored passwords. There is a scripts in the `scripts` folder to help with setting the passwords on multiple VPN connections. A provider such as PIA provides multiple VPN connections for a fee ,or there could also be other free sources.


## System resources & tile numbers

The number of tiles can be huge. Size of area and zoom levels will effect the number. Each zoom level has 4 times the number of tiles as the previous so things can get out of hand quickly! Around 100,000 tiles will produce a 3GB+ MBTiles file, which QGIS seems able to cope with and is probably a reasonable figure to start off with. The generation of the GeoTiff will require a lot of system memory(RAM) for large jobs. Use the `count_tiles` tool before starting to download.


## Windows Users

This hasn't been tested on Windows, but most commands should run if installed in an environment like OSGEO4W. The `clean_downloads` command is dependent on the GNU `find` command so may need CYGWIN to run with Windows. It is checking for PNG files under 1kb in the outputted folder structure, so it may also be possible to do this manually in Windows Explorer.
