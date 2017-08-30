#################################################################
#   Tom McAdam                                                  #
#   Copyright (c) 2016, Thomas McAdam. All rights reserved.     #
#################################################################

import json
import math
import random
import os
import subprocess
import sys
import errno
from StringIO import StringIO
from string import Template

from datetime import datetime
import eventlet
from eventlet.green import urllib2 as evUrllib2
from PIL import Image


class Provider:
    """
        This class is used to store details of a tile provider i.e. Google, Bing etc.
    """

    def __init__(self, name, tile_system, tile_format, url, attribution, balancers=None):

        self.name = name
        self.tile_system = tile_system
        self.tile_format = tile_format
        self.url = url
        self.attribution = attribution
        self.balancers = balancers

    def gen_url(self, tile):
        if self.balancers:
            return self.url.format(balancer=random.choice(self.balancers), zoom=tile.z, x=tile.x, y=tile.y)
        return self.url.format(zoom=tile.z, x=tile.x, y=tile.y)


class Tile:
    """
    A class to operate on individual tiles, convert to coordinates, swap between TMS slippy etc.
    Some of this comes from:
        http://www.maptiler.org/google-maps-coordinates-tile-bounds-projection/globalmaptiles.py
        Copyright (c) 2008 Klokan Petr Pridal. All rights reserved.
    """
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        self.image = None

    def y_tms(self):
        """
        Converts y value of tile into TMS format
        """
        return int(2.0**self.z - self.y - 1)

    def quad_tree(self):
        """
        Converts tile into Quadtree notation system (used for systems like Bing)
        """
        quad_key = ""
        for i in range(self.z, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if (self.x & mask) != 0:
                digit += 1
            if (self.y & mask) != 0:
                digit += 2
            quad_key += str(digit)
        return quad_key

    def to_point(self):
        """
        Returns geographical coordinates of the top-left corner of the tile.
        """
        n = math.pow(2, self.z)
        longitude = float(self.x) / n * 360.0 - 180.0
        latitude = math.degrees(math.atan(math.sinh(math.pi * (1.0 - 2.0 * float(self.y) / n))))
        return longitude, latitude

    def to_rectangle(self):
        """
        Returns geographical coordinates of top-left and bottom-right of tile
        """
        return self.to_point(), Tile(self.x + 1, self.y + 1, self.z).to_point()

    def to_point_meters(self):
        return self.lonlat_to_meters(self.to_point())

    def to_rectangle_meters(self):
        return self.lonlat_to_meters(self.to_rectangle()[0]), self.lonlat_to_meters(self.to_rectangle()[1])

    @staticmethod
    def lonlat_to_meters(lonlat):
        """
        Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:900913
        """
        origin_shift = 2 * math.pi * 6378137 / 2.0
        lon, lat = lonlat
        mx = lon * origin_shift / 180.0
        my = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
        my = my * origin_shift / 180.0
        return mx, my

    def url(self, provider):
        return provider.gen_url(self)

    def path(self):
        return os.path.join(str(self.z), str(self.x), '{}.png'.format(self.y))

    def full_path(self, tile_job):
        return os.path.join(tile_job.out_path, tile_job.job_name, self.path())

    def identifier(self, provider):
        identifier = provider.name.lower() + '_' + str(self.z) + '_'
        identifier += str(self.x) + '_' + str(self.y)
        return identifier


class TileSet:
    """
    A Tileset is a geographical area and the contains a bunch of tiles
    """
    def __init__(self, name, version, description, folder, extents, zoom_min, zoom_max, provider):

        self.name = name
        self.version = version
        self.description = description
        self.folder = folder
        north, south, west, east = extents
        self.bbox = {
            "n": self.check_north(north),
            "e": east,
            "s": self.check_south(south),
            "w": west
        }
        self.zoom_min = zoom_min
        self.zoom_max = zoom_max
        self.zoom_range = range(zoom_min, zoom_max + 1)
        self.provider = provider
        self.tiles = self.pop_tileset()

    @staticmethod
    def check_north(north):
        if north > 85.05112877980659:
            return 85.05112877980659
        return north

    @staticmethod
    def check_south(south):
        if south < -85.05112877980659:
            return -85.05112877980659
        return south

    def pop_tileset(self):
        tileset = dict()
        for zoom in self.zoom_range:
            tiles = []
            for x in self.cols(zoom):
                for y in self.rows(zoom):
                    tiles.append(Tile(z=zoom, x=x, y=y))
            tileset[zoom] = tiles
        return tileset

    def cols(self, zoom):
        return range(self.top_left(zoom)[0], self.bottom_right(zoom)[0] + 1)

    def rows(self, zoom):
        return range(self.top_left(zoom)[1], self.bottom_right(zoom)[1] + 1)

    def bottom_right(self, zoom):
        return self.deg2num(self.bbox['s'], self.bbox['e'], zoom)

    def top_left(self, zoom):
        return self.deg2num(self.bbox['n'], self.bbox['w'], zoom)

    def extents_meters(self, zoom):
        x1, y1 = self.top_left(zoom)
        x2, y2 = self.bottom_right(zoom)
        top_left = Tile(x1, y1, zoom).to_point_meters()
        bottom_right = Tile(x2, y2, zoom).to_rectangle_meters()[1]
        return top_left, bottom_right

    @staticmethod
    def deg2num(lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x_tile = int((lon_deg + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return x_tile, y_tile

    def center_x(self):
        return (self.bbox['w'] + self.bbox['e'])/2

    def center_y(self):
        return (self.bbox['n'] + self.bbox['s'])/2

    def avg_zoom(self):
        return (self.zoom_max + self.zoom_min) / 2


class TileDownloadJob:
    """
    A download job manages the processing of a Tileset
    """
    def __init__(self, out_path, tileset):

        self.counts = dict()
        self.set_counts()
        self.out_path = out_path
        self.job_name = tileset.folder
        self.tileset = tileset
        self.connections = None
        self.connection_name = None
        self.downloads = list()
        self.exists = list()
        self.gen_download_lists()
        self.start_time = datetime.now()

    def gen_lists(self):
        self.downloads = list()
        self.exists = list()
        self.gen_download_lists()

    def set_counts(self):
        self.counts['blocked'] = 0
        self.counts['not_found'] = 0
        self.counts['found'] = 0
        self.counts['attempted'] = 0
        self.counts['connection'] = 0

    def gen_download_lists(self):

        def test_file(filename_to_test):
            if os.path.exists(filename_to_test):
                return True
            return False

        for zoom in self.tileset.zoom_range:
            for tile in self.tileset.tiles[zoom]:
                filename = tile.full_path(self)
                if not test_file(filename):
                    self.downloads.append(tile)
                else:
                    self.exists.append(tile)
        self.counts["download"] = len(self.downloads)
        self.counts["exists"] = len(self.exists)

    def get_tiles(self, proxy=False):

        def test_path(filename_to_check):
            if not os.path.exists(os.path.dirname(filename_to_check)):
                try:
                    os.makedirs(os.path.dirname(filename_to_check))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

        def fetch(tile_to_fetch):
            try:
                self.counts['attempted'] += 1
                self.counts['connection'] += 1
                tile_to_fetch.image = evUrllib2.urlopen(tile_to_fetch.url(self.tileset.provider)).read()
                self.counts['found'] += 1
            except evUrllib2.HTTPError as e:
                if e.code == 403:
                    self.counts['blocked'] += 1
                elif e.code == 404:
                    self.counts['not_found'] += 1
                    with open("blank.png", 'rb') as f:
                        tile_to_fetch.image = f.read()
                else:
                    print(e.code)
            except evUrllib2.URLError as e:
                print(e)
            finally:
                return tile_to_fetch

        pool = eventlet.GreenPool(25)
        for tile in pool.imap(fetch, self.downloads):
            filename = tile.full_path(self)
            test_path(filename)
            if tile.image:
                im = Image.open(StringIO(tile.image))
                im.save(filename, "PNG")
                tile.image = None
                self.exists.append(tile)

            seconds_elapsed = (datetime.now() - self.start_time).total_seconds()
            tiles_per_min = int((float(self.counts["attempted"]) / seconds_elapsed) * 60)
            minutes_remaining = int((self.counts['download'] - self.counts['attempted']) / tiles_per_min)

            output = "Attempted: {0}/{1}   Found: {2}   Not found: {3}   Blocked: {4}    " \
                     "Tiles/Min: {5}({6} mins remaining)".format(self.counts["attempted"],
                                                                 self.counts["download"],
                                                                 self.counts["found"],
                                                                 self.counts['not_found'],
                                                                 self.counts['blocked'],
                                                                 tiles_per_min,
                                                                 minutes_remaining)
            sys.stdout.write("\r{}".format(output))
            sys.stdout.flush()

            if proxy and (self.counts['blocked'] > 10 or self.counts['connection'] > 100):
                self.counts['connection'] = 0
                self.counts['blocked'] = 0
                self.reset_vpn()
                self.gen_lists()
                return False

        return True

    def init_vpn(self, _connections):
        self.connections = _connections
        self.connection_name = random.choice(self.connections)
        self.open_vpn()

    def open_vpn(self):
        args = ['nmcli', 'con', 'up', 'id', '{}'.format(self.connection_name)]
        subprocess.call(args, stdout=open(os.devnull, 'wb'))

    def close_vpn(self):
        args = ['nmcli', 'con', 'down', 'id', '{}'.format(self.connection_name)]
        subprocess.call(args, stdout=open(os.devnull, 'wb'))

    def reset_vpn(self):
        self.close_vpn()
        self.connection_name = random.choice(self.connections)
        self.open_vpn()

    def write_leaflet_viewer(self):

        with open('viewer.html', 'r') as template_file:
            viewer = MyTemplate(unicode(template_file.read()))
            use_tms = 'false'
            substitutions = {'tiles_dir': self.tiles_dir(),
                             'tiles_ext': 'png',
                             'tileset_name': self.job_name,
                             'tms': use_tms,
                             'center_x': self.tileset.center_x(),
                             'center_y': self.tileset.center_y(),
                             'avg_zoom': self.tileset.avg_zoom(),
                             'max_zoom': self.tileset.zoom_max
                             }
            file_path = os.path.join(self.out_path, '{}.html'.format(self.job_name))
            with open(file_path, 'w') as fOut:
                fOut.write(viewer.substitute(substitutions))

    def tiles_dir(self):
        return os.path.join(self.out_path, self.job_name)

    def write_metadata(self):
        metadata = MetaData(self.tileset)
        metadata.write(self.tiles_dir())

    def write_mbtiles(self):
        filename = os.path.join(self.out_path, '{}.mbtiles'.format(self.job_name))
        self.write_metadata()
        try:
            os.remove(filename)
        except OSError as e:
            pass
        args = [
            'mb-util',
            self.tiles_dir(),
            filename,
            '--scheme',
            'xyz' if self.tileset.provider.tile_system == "SLIPPY" else 'tms',
            '--image_format',
            'png',
            '--silent'
        ]
        subprocess.call(args)

    def clean_download(self):
        args = ["find",
                self.tiles_dir(),
                "-type",
                "f",
                "-not",
                "-size",
                "+1k",
                "-name",
                "*.png"]
        ps = subprocess.Popen(args, stdout=subprocess.PIPE)
        number_deleted = len(ps.stdout.readlines())
        ps.wait()
        args.append("-delete")
        subprocess.Popen(args, stdout=subprocess.PIPE)
        ps.wait()
        print "Deleted files: {}".format(number_deleted)


class TileStitchJob:

    def __init__(self, tile_download_job):
        self.job = tile_download_job
        self.tileset = tile_download_job.tileset
        self.path = os.path.join(self.job.out_path, self.job.job_name)
        self.zoom = self.tileset.zoom_max
        self.px = 256 * len(self.tileset.cols(self.zoom))
        self.py = 256 * len(self.tileset.rows(self.zoom))

    def gen_world(self):
        # Crop off the excess space.
        # Get (lat, lon) in degrees of corners of image
        top_left, bottom_right = self.tileset.extents_meters(self.zoom)
        pixel_x = abs(top_left[0] - bottom_right[0]) / self.px
        pixel_y = -abs((top_left[1] - bottom_right[1]) / self.py)
        wld = [pixel_x, 0, 0, pixel_y, top_left[0], top_left[1]]
        return [str(x) + "\n" for x in wld]

    def stitch(self):
        mode = "RGBA"
        image = Image.new(mode, [self.px, self.py])
        start = self.tileset.top_left(self.zoom)
        tiles = self.tileset.tiles[self.zoom]
        c = 0
        tile_count = len(tiles)
        for tile in tiles:
            path = tile.full_path(self.job)
            cx = 256 * (tile.x - start[0])
            cy = 256 * (tile.y - start[1])
            tile_image = Image.open(path)
            image.paste(tile_image, (cx, cy))
            c += 1

            output = "Stitched: {}/{}".format(c, tile_count)
            sys.stdout.write("\r{}".format(output))
            sys.stdout.flush()

        # this should overwrite if it already exists
        image.save(self.path + '.png')
        with open(self.path + '.pngw', 'w') as f:
            f.writelines(self.gen_world())

    def convert_tif(self):
        print '\nConverting to GeoTiff......'
        try:
            os.remove(self.path + ".tif")
        except OSError as e:
            pass
        args = ['gdal_translate', '-co', 'COMPRESS=JPEG', '-co', 'PHOTOMETRIC=RGB', '-co', 'BIGTIFF=YES', '-co', 'ALPHA=YES',
                '-co', 'INTERLEAVE=BAND', '-co', 'JPEG_QUALITY=75', '-co', 'TFW=NO', self.path + ".png", self.path + ".tif"]
        subprocess.call(args)

        args = ['gdal_edit.py', '-a_srs', 'EPSG:3857', self.path + ".tif"]
        subprocess.call(args)

        # Add overviews to give better rendering performance in GIS
        print '\nAdding overviews......'
        try:
            os.remove(self.path + ".tif.ovr")
        except OSError as e:
            pass
        args = ['gdaladdo',
                '-ro',
                '-r', 'average',
                '--config', 'COMPRESS_OVERVIEW', 'JPEG',
                '--config', 'JPEG_QUALITY_OVERVIEW', '75',
                '--config', 'BIGTIFF_OVERVIEW', 'YES',
                self.path + ".tif",
                '2', '4', '8', '16', '32', '64', '128', '256']
        subprocess.call(args)

        # clean up the PNGs they are big and slow
        os.remove(self.path + ".png")
        os.remove(self.path + ".pngw")

        print 'Saved stitched map '


class MyTemplate(Template):
    delimiter = '@'

    def __init__(self, template_string):
        Template.__init__(self, template_string)


class MetaData:

    def __init__(self, tileset):

        self.META_DATA = dict()
        self.META_DATA['name'] = tileset.name
        self.META_DATA['type'] = 'baselayer'
        self.META_DATA['version'] = tileset.version
        self.META_DATA['description'] = tileset.description
        self.META_DATA['format'] = 'png'
        self.META_DATA['bounds'] = '{},{},{},{}'.format(
            tileset.bbox['w'], tileset.bbox['s'], tileset.bbox['e'], tileset.bbox['n'])
        self.META_DATA['attribution'] = tileset.provider.attribution

    def write(self, file_path):
        with open(os.path.join(file_path, 'metadata.json'), 'w') as fp:
            json.dump(self.META_DATA, fp)
