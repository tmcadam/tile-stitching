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
import os
import urllib
#import urllib2
import math
from datetime import datetime
import threading

#import wx
#import wx.html
import eventlet
from eventlet.green import urllib2  

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
from PIL import ImageMath

SAT_URL = "http://mt0.google.com/vt/lyrs=s&x=0&y=0&z=0"
BING_URL = "http://t0.tiles.virtualearth.net/tiles/a&&&&.jpeg?g=854&mkt=en-US&token=Anz84uRE1RULeLwuJ0qKu5amcu5rugRXy1vKc27wUaKVyIv1SVZrUjqaOfXJJoI0"
#grabPool = Queue.Queue( 0 )

class StitchedMap:
    
    def __init__(self, lat, lon, zoom, maptype, filename = None):
        self.start_time = datetime.now()
        self.lat = lat
        self.lon = lon
        self.latVal = (float(lat[0]), float(lat[1]))
        self.lonVal = (float(lon[0]), float(lon[1]))

        if (self.latVal[0] >= self.latVal[1]):
            print 'Invalid latitude range. Aborting.'
            return

        if (self.lonVal[0] >= self.lonVal[1]):
            print 'Invalid longitude range. Aborting.'
            return
        
        self.zoom = zoom  # understood to be -1 if resolution specified
        self.maptype = maptype
        self.filename = filename
        self.SAT_MODE_PREFIX = self.makeDummyUrl(SAT_URL.split('&')[0])
        self.tileSize = 256
        self.initialResolution = 2 * math.pi * 6378137 / self.tileSize
        self.originShift = 2 * math.pi * 6378137 / 2.0
        
        if os.path.exists("./tiles") != True:
             os.mkdir("./tiles")
    
    def makeDummyUrl(self, url):

        # Some string hacking to replace e.g. "http://mt0.google.com..." with "http://mt%s.google.com..."
        # so that later we can replace %s with an integer 0-4 for load balancing
        server_url = url.split(".google")
        server_name = server_url[0][0:len(server_url[0])-1]
        dummy_url = server_name + "%s.google" + server_url[1]
        return dummy_url
    
    def gen_SAT_URL(self, tile):
        x = str(tile[0])
        y = str(tile[1])
        #url = self.SAT_MODE_PREFIX + '&t=' + code==
        url = self.SAT_MODE_PREFIX + '&x=' + x + '&y=' + y + '&z=' + str(self.zoom)
        return url
        
    def gen_BING_URL(self, tile):
        x = str(tile[0])
        y = str(tile[1])
        #url = self.SAT_MODE_PREFIX + '&t=' + code==
        url = BING_URL.replace('&&&&', self.tileXYZToQuadKey(int(x), int(y), int(self.zoom)))
        return url
        
    def generate(self):
   
        c0 = "(" + self.lat[0] + ", " + self.lon[0] + ")"
        c1 = "(" + self.lat[1] + ", " + self.lon[1] + ")"

        print '\n######################################################################'
        print "Making " + self.maptype + " map defined by (lat, lon) corners " + c0 + " and " + c1

        EX = math.fabs(float(self.lon[1]) - float(self.lon[0]))
        EY = math.fabs(float(self.lat[1]) - float(self.lat[0]))
        print 'Requested map (lng, lat) size in degrees is: ', str(EX), str(EY)

        # compute which 256x256 tiles we need to download
        self.computeTileMatrix()
        if (self.zoom<0) or (self.zoom>19):
            print 'Invalid zoom level (' + str(self.zoom) + '). Aborting.'
            return
        print 'Zoom level: ', str(self.zoom)
 
        # Connect to Google maps and download tiles
        n = self.download(1)
        if n != 0 :
            n = self.download(2)
            if n != 0:
                n = self.download(3)
        # Finally stitch the downloaded maps together into the final big map
        self.stitch()
        self.convertTif()
    
    def stitch(self):
        print '\nStitching tiles......'
        self.pX = 256 * self.nX
        self.pY = 256 * self.nY

        mode = "RGBA"
        Map = Image.new(mode, (self.pX, self.pY))
        total = (self.nX * self.nY)
        c = 0
        for i in range(0, self.nX):
            for j in range(0, self.nY):
                c += 1
                tile = self.tiles[i][j]
                path = './tiles/tile_' + self.makeIdentifier(tile) + '.jpg'
                # pixel coords of top left corner of this tile
                cX = 256 * i
                cY = self.pY - 256 * (j+1)
                try:
                    im = Image.open(path)
                except:
                    im = Image.open('./blank.png')
                try:
                    Map.paste(im, (cX, cY))
                except:
                    print 'ERROR:%s' % path
                    break
                sys.stdout.write( "Stitching: %s/%s   \r" % (c,total) )
                sys.stdout.flush()
        sys.stdout.flush()
        # give the map file a semi-unique name, derived from the lower-left tile coords
        # mappath = './stitched_' + self.makeIdentifier(self.tiles[0][0]) + '.png'
        mappath = '%s.png' % self.filename
        wld = self.genWorld()
        wldpath = '%s.pngw' % self.filename
        f=open(wldpath,'w')
        for item in wld:
            f.write("%s\n" % item)
        f.close()
        print '\nSaving......'
        Map.save(mappath)
        print 'Save Complete'
    
    def convertTif(self):
        print 'Converting......'
        mappath = '%s.png' % self.filename
        try:
            os.remove(mappath.replace('.png','.tif'))
        except: pass
        try:
            os.remove(mappath.replace('.png','.tif.ovr'))
        except: pass   
        
        cmd = 'gdal_translate -co COMPRESS=JPEG -co PHOTOMETRIC=RGB -co BIGTIFF=YES -co ALPHA=YES -co INTERLEAVE=BAND -co JPEG_QUALITY=75 -co TFW=NO %s %s' % ( mappath , mappath.replace('.png','.tif') )
        os.system(cmd)
        cmd = 'gdal_edit.py -a_srs EPSG:3857 %s' %( mappath.replace('.png','.tif') )  
        os.system(cmd)
        cmd = 'gdaladdo -ro -r average --config COMPRESS_OVERVIEW JPEG --config JPEG_QUALITY_OVERVIEW 75 --config BIGTIFF_OVERVIEW YES %s 2 4 8 16 32 64 128 256' % ( mappath.replace('.png','.tif') )
        os.system(cmd)
        os.remove(mappath)
        os.remove(mappath.replace('.png','.pngw'))
        
        print 'Saved stitched map ' + mappath.replace('.png','.tif')
        print 'Finished.'     
        
    def genWorld(self):

        # Crop off the excess space.
        # Get (lat, lon) in degrees of corners of image
        tileA = self.tiles[0][0]
        coordsA = self.getCoordsOfTile(tileA)
        
        tileB = self.tiles[self.nX-1][self.nY-1]
        coordsB = self.getCoordsOfTile(tileB)
        
        LL = (coordsA[0], abs(coordsA[3]))
        UR = (coordsB[2], abs(coordsB[1]))
        
        pixel_x = (UR[0] - LL[0]) / self.pX
        pixel_y = (LL[1] - UR[1]) / self.pY
        
        wld = [ pixel_x,0,0, pixel_y,LL[0],UR[1]]
        return wld
        
    def Resolution(self, zoom ):
        "Resolution (meters/pixel) for given zoom level (measured at Equator)"
        
        # return (2 * math.pi * 6378137) / (self.tileSize * 2**zoom)
        return self.initialResolution / (2**zoom)
    
    def PixelsToMeters(self, px, py, zoom):
        "Converts pixel coordinates in given zoom level of pyramid to EPSG:900913"

        res = self.Resolution( zoom )
        mx = px * res - self.originShift
        my = py * res - self.originShift
        return mx, my        
        
    def getCoordsOfTile(self, tile):

        minx, miny = self.PixelsToMeters( tile[0]*self.tileSize, tile[1]*self.tileSize, self.zoom )
        maxx, maxy = self.PixelsToMeters( (tile[0]+1)*self.tileSize, (tile[1]+1)*self.tileSize, self.zoom )
        return ( minx, miny, maxx, maxy )
    
        nTile = 1 << self.zoom
        print tile
        width  = 360.0/float(nTile)
        height = 180.0/float(nTile)

        tiley = tile[1]
        #if self.maptype != 'satellite':
        tiley = nTile - 1 - tiley
        
        print tiley
        X = -180.0 + float(tile[0]) * width
        Y = -90.0  + float(tiley) * height

        # coords of corners of tile
        LL = (X,       Y)
        UR = (X+width, Y+height)
        return [LL, UR]     
        
    def checkTiles(self, pass_count): 
        total = (self.nX * self.nY)
        n = 0
        c = 1
        # Test if the tile exists or if it is blank. 
        for i in range(0, self.nX):
            for j in range(0, self.nY):
                c+=1
                tile = self.tiles[i][j]
                tilePath = './tiles/tile_' + self.makeIdentifier(tile) + '.jpg'
                ## Checks if the tile exists and if it can be opened.
                delete = False
                try:
                    with open(str(tilePath), 'rb') as f:
                        im = Image.open(f)
                        tile[3] = False
                        Map = Image.new("RGBA", (256, 256))
                        try:
                            Map.paste(im, (0, 0))
                        except:
                            n += 1
                            tile[3] = True
                            delete = True
                            #print 'Failed to merge: %s' % tilePath     
                        del Map, im
                except:
                    #print 'Tile Fail - %s' % tilePath
                    tile[3] = True
                    n += 1
                    delete = True
                    if pass_count > 3 or (self.checkSurrounding(i,j) == True and pass_count > 1) :
                        delete = False
                        tile[3] = False
                        n -= 1  
                if delete == True: 
                    try: os.remove(tilePath)
                    except: pass
                sys.stdout.write( "Testing: %s/%s   \r" % (c,total) )
                sys.stdout.flush()     
        self.download_total = n
        print "Total number of tiles to download: %s" % n             
        return n
    
    def checkSurrounding(self,i,j):
        tile = self.tiles[i][j]
        surrounds = []
        edge = 0
        try: surrounds.append(self.tiles[i+1][j]) 
        except: edge +=1
        try: surrounds.append(self.tiles[i-1][j]) 
        except: edge +=1
        try: surrounds.append(self.tiles[i][j+1])
        except: edge +=1
        try: surrounds.append(self.tiles[i][j-1]) 
        except: edge +=1
        try: surrounds.append(self.tiles[i+1][j+1]) 
        except: edge +=1
        try: surrounds.append(self.tiles[i-1][j-1]) 
        except: edge +=1
        try: surrounds.append(self.tiles[i+1][j-1]) 
        except: edge +=1
        try: surrounds.append(self.tiles[i-1][j+1]) 
        except: edge +=1
        fails = 0
        for surround_tile in surrounds:
            tilePath = './tiles/tile_' + self.makeIdentifier(surround_tile) + '.jpg'
            try: 
                im = Image.open(tilePath)
                del im
            except:
                fails += 1
        #print '%s:%s' %( fails, edge)
        if fails >= 2 and edge == 0 : 
            return True 
        elif fails >= 1 and edge == 3 :
            return True
        else:    
            return False
    
    def download(self, pass_count):
        print '\nDownload tiles: Pass %s' % pass_count
        self.download_count = 0
        n = self.checkTiles(pass_count)
        if n == 0:
            return 0
        downloads = []
        for column in self.tiles:
            for tile in column:
                tilePath = './tiles/tile_' + self.makeIdentifier(tile) + '.jpg'
                if tile[3] == True:   
                    mapurl = ''
                    if self.maptype == 'map':              mapurl = self.gen_MAP_URL(tile)
                    elif self.maptype == 'satellite':      mapurl = self.gen_SAT_URL(tile)
                    elif self.maptype == 'terrain':        mapurl = self.gen_PHY_URL(tile)
                    elif self.maptype == 'sky':            mapurl = self.gen_SKY_URL(tile)
                    elif self.maptype == 'bing_satellite': mapurl = self.gen_BING_URL(tile)    
                    else: 
                        print 'Unknown map type! Quitting. Humph'
                        sys.exit()
                    if mapurl:
                        downloads.append([ mapurl, self.makeIdentifier(tile) ])           
                    print self.gen_BING_URL(tile) 
        serverSelectCounter = 0
        for tile in downloads:
            url = tile[0]
            output = './tiles/tile_' + tile[1] + '.jpg'
            if( url.find( "%s" ) != -1 ):
                url = url % serverSelectCounter
                serverSelectCounter += 1
                if serverSelectCounter > 3:
                    serverSelectCounter = 0
            tile[0] = url  
            tile[1] = output
        pool = eventlet.GreenPool(10)
        sys.stdout.write( "Downloading........" )
        self.down_time = datetime.now()
        print downloads
        for url, body in pool.imap(self.fetch, downloads):
            pass
            #sys.stdout.write( "Downloading %s" url )
            #sys.stdout.flush() 
        return 1

    def fetch(self, url):
        
        delta = datetime.now() - self.down_time
        self.down_time = datetime.now()
        try:
            time_diff = round(60 / ( float( delta.seconds ) + ( float( delta.microseconds ) / 1000000 ) ))
        except:
            time_diff = '----'
        self.download_count += 1
        sys.stdout.write( "\nDownloading: %s/%s Rate: %s/min\r" % (self.download_count, self.download_total, time_diff) )
        sys.stdout.flush()  
        

        try:
            file  = urllib2.urlopen(url[0])
            output = open(url[1],'wb')
            output.write(file.read())
            output.close()
            return url[0], True
        except:
            return url[0], False             
    
    def tileXYZToQuadKey(self, x, y, z):
        quadKey = ''
        for i in range(z, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if(x & mask) != 0:
                digit += 1
            if(y & mask) != 0:
                digit += 2
            quadKey += str(digit)
        return quadKey
    
    def computeTileRange(self):
        
        self.zoom = long(self.zoom)
        
        # In satellite mode, the zoom level in the html query goes from 0 to 14 inclusive,
        # 0 being the lowest res (i.e. the map of the world).
        # In the other modes, the zoom level goes from -2 to 17 inclusive, 17 being the map of the world.
        if (self.maptype != 'satellite'):
            self.htmlzoom = 17 - self.zoom
        
        # Google maps uses the Mercator projection, so we need to convert the given latitudes 
        # into Mercator y-coordinates. Google takes the vertical edges of the map to be at
        # y = +/-pi, corresponding to latitude +/-85.051128.
        # It is convenient therefore to compute y/2 for each latitude. We can then
        # just use the y coord as if it were a latitude, with the top edges at +/-90.0 "degrees".
        l0 = self.latVal[0]
        l1 = self.latVal[1]
        self.yVal = (self.latitudeToMercator(l0), self.latitudeToMercator(l1))
            
        # get the corner tile 
        tileA = self.getTile(self.lonVal[0], self.yVal[0])
        tileB = self.getTile(self.lonVal[1], self.yVal[1])

        return [tileA, tileB]
        
        
        # Allow phi in range [-90.0, 90.0], return in same range
    
    def getTile(self, lng, lat):

        nTile = 1 << self.zoom

        # note, assume ranges are lng = (-180,180), lat = (-90,90)
        tilex = long(nTile * (float(lng) + 180.0)/360.0)
        tiley = long(nTile * (float(lat) + 90.0 )/180.0)

        if tilex == nTile: tilex -= 1
        if tilex<0: tilex = 0

        if tiley == nTile: tiley -= 1
        if tiley<0: tiley = 0  

        # the hybrid and terrain modes index the tiles descending with latitude 
        #if self.maptype != 'satellite':
        tiley = nTile - 1 - tiley
            
        tile = (tilex, tiley)
        return tile       
        
    def makeIdentifier(self, tile):

        identifier = self.maptype + '_' + str(self.zoom) + '_'
        #if self.maptype == 'satellite':
        #    identifier += tile[2]
        #else:
        identifier += str(tile[0]) + '_' + str(tile[1])
        return identifier
    
    def latitudeToMercator(self, phi):

         # If the given latitude falls outside of the +/-85.051128 range, we clamp it back into range.
        phimax = 85.05112
        if   phi>phimax: phi = phimax
        elif phi<-phimax: phi = -phimax
     
        # find sign    
        sign = 0.0
        if phi>=0.0: sign = 1.0
        else:        sign = -1.0
        
        # convert to rad
        phi *= math.pi/180.0

        # make positive for Mercator formula
        phi = math.fabs(phi)
        
        # find [0,pi] range Mercator coords
        y = math.log( math.tan(phi) + 1.0/math.cos(phi) )
        
        # put back sign and scale by factor of 2
        y *= 0.5*sign

        # convert to degrees
        y *= 180.0/math.pi

        # clamp to [-90.0, 90.0]
        if   y>90.0: y = 90.0
        elif y<-90.0: y = -90.0
        
        return y
        
    def computeTileMatrix(self):

        tileRange = self.computeTileRange()

        tileA = tileRange[0]
        tileB = tileRange[1]

        tileAstr = '(' + str(tileA[0]) + ',' + str(tileA[1]) + ')'
        tileBstr = '(' + str(tileB[0]) + ',' + str(tileB[1]) + ')'
        print 'Corner tile indices: ' + tileAstr + ', ' + tileBstr
        
        self.nX = abs(tileB[0] - tileA[0]) + 1
        self.nY = abs(tileB[1] - tileA[1]) + 1

        print 'Total number of tiles in map: ' + str(self.nX*self.nY)

        # Make a nX*nY matrix of the tiles (i,j) we need, with (0,0) in the lower-left.
        # The google tile indices (lng, lat) corresponding to (i,j) (at the given zoom level) are stored
        # in each tile.
        
        # We need the fact that in satellite mode, the lng, lat tile indices increase with both longitude
        # and latitude, but in the other modes, the lat index decreases with latitude
        self.tiles = []
        for i in range(0, self.nX):

            lng = tileA[0] + i
            column = []

            for j in range(0, self.nY):

                lat = 0
                #if self.maptype == 'satellite':
                #    lat = tileA[1] + j
                #    code = self.genSatelliteTileCode(lng, lat)
                #else:
                lat = tileA[1] - j 
                code = ''
                download_status = True
                pass_count = 0
                tile = [lng, lat, code, download_status, pass_count]
                column.append(tile)

            self.tiles.append(column) 
