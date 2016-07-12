##############################################################################
#    TileStitch v0.1
#    	
#    Copyright(C) 2015 Thomas McAdam
#    Based on Stitch v3.0 by Jamie Portsmouth (jamports@mac.com)
#	and Morgan Tørvolt (morgan@torvolt.com)
#	
#    This file is part of TileStitch.
#
#    TileStitch is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TileStitch is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TileStitch.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################


import sys
from StitchedMap import StitchedMap

N = 10
print "\n\n\n\n*************** TileStitch v0.1 ***************"

	
# python tom_stitch.py <LowerLeft_Long>_<LowerLeft_Lat>_<TopRight_Long>_<TopRight_Lat> <zoom_level> <type> <out_file>

# i.e
# python tom_stitch.py 122.0350_10.7703_122.0894_10.8272 19 satellite Sibalom_4 
# python tom_stitch.py -57.9167_-51.7224_-57.7275_-51.6357 16 bing_satellite Falklands_1

extents = sys.argv[1].split('_')
lon = [ extents[0] , extents[2] ]
lat = [ extents[1] , extents[3] ]
zoom = sys.argv[2]
maptype = sys.argv[3]
mapname = sys.argv[4]
map = StitchedMap( lat, lon, zoom, maptype, mapname ).generate()        
