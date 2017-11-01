#################################################################
#   Tom McAdam                                                  #
#   Copyright (c) 2016, Thomas McAdam. All rights reserved.     #
#################################################################

import unittest

from tile_tools import Tile, Provider, TileSet


class TileSetTest(unittest.TestCase):

    zoom_min = 10
    zoom_max = 15
    bbox = {
        "n": -22.744461,
        "w": -43.836728,
        "s": -23.092303,
        "e": -43.089037
    }
    url = "http://{balancer}.some.tile.url/{zoom}/{x}/{y}.png",
    balancers = ['a', 'b', 'c']
    provider = Provider(name="test_name", tile_system="SLIPPY", tile_format="PNG", url=url, balancers=balancers, attribution="Tests")

    def test_check_north_alters_north_over_limit(self):
        tileset = TileSet(name="", version="", description="", folder="",
                          extents=(0, 0, 0, 0), zoom_min=0, zoom_max=0, provider=None)
        self.assertAlmostEqual(tileset.check_north(90), 85.05112878, places=8)

    def test_check_north_does_not_alter_north_within_limits(self):
        tileset = TileSet(name="", version="", description="", folder="",
                          extents=(0, 0, 0, 0), zoom_min=0, zoom_max=0, provider=None)
        self.assertEquals(tileset.check_north(60.12345), 60.12345)

    def test_check_south_alters_south_over_limit(self):
        tileset = TileSet(name="", version="", description="", folder="",
                          extents=(0, 0, 0, 0), zoom_min=0, zoom_max=0, provider=None)
        self.assertAlmostEqual(tileset.check_south(-90), -85.05112878, places=8)

    def test_check_south_does_not_alter_south_within_limits(self):
        tileset = TileSet(name="", version="", description="", folder="",
                          extents=(0, 0, 0, 0), zoom_min=0, zoom_max=0, provider=None)
        self.assertEquals(tileset.check_south(-60.12345), -60.12345)





class TileTest(unittest.TestCase):

    test_tiles = [
        {
            "tile_name": "Hi Zoom",
            "tile_location": (1893794, 1288261, 21),
            "y_tms": 808890,
            "quad_tree": "311223130210112100212",
            "to_point": (145.0912857055664, -38.005496273893314),
            "to_rectangle": (145.0912857055664, -38.005496273893314, 145.09145736694336, -38.00563153464075)
        },
        {
            "tile_name": "Southern Hemisphere",
            "tile_location": (162, 143, 8),
            "y_tms": 112,
            "quad_tree": "30102232",
            "to_point": (47.81250000, -20.63278425),
            "to_rectangle": (47.81250000, -20.63278425, 49.21875000, -21.94304553)
        },
        {
            "tile_name": "Northern Hemisphere",
            "tile_location": (496, 326, 10),
            "y_tms": 697,
            "quad_tree": "0313110220",
            "to_point": (-5.62500000, 54.57206166),
            "to_rectangle": (-5.62500000, 54.57206166, -5.27343750, 54.36775852)
        },
        {
            "tile_name": "South West",
            "tile_location": (0, 1, 1),
            "y_tms": 0,
            "quad_tree": "2",
            "to_point": (-180.00000000, 0.00000000),
            "to_rectangle": (-180.00000000, 0.00000000, 0.00000000, -85.05112878)
        },
        {
            "tile_name": "North East",
            "tile_location": (1, 0, 1),
            "y_tms": 1,
            "quad_tree": "1",
            "to_point": (0.00000000, 85.05112878),
            "to_rectangle": (0.00000000, 85.05112878, 180.00000000, 0.00000000)
        },
        {
            "tile_name": "All",
            "tile_location": (0, 0, 0),
            "y_tms": 0,
            "quad_tree": "",
            "to_point": (-180.00000000, 85.05112878),
            "to_rectangle": (-180.00000000, 85.05112878, 180.00000000, -85.05112878)
        }
    ]

    def test_init_sets_correct_values(self):
        for test_tile in self.test_tiles:
            tile_location = test_tile["tile_location"]
            tile = Tile(tile_location[0], tile_location[1], tile_location[2])
            self.assertEquals(tile.x, tile_location[0])
            self.assertEquals(tile.y, tile_location[1])
            self.assertEquals(tile.z, tile_location[2])

    def test_y_tms_returns_correct_value_for_y_in_tms_tile_system(self):
        for test_tile in self.test_tiles:
            tile_location = test_tile["tile_location"]
            tile = Tile(tile_location[0], tile_location[1], tile_location[2])
            self.assertEquals(tile.y_tms(), test_tile["y_tms"])

    def test_quad_tree_returns_correct_values_in_quad_tree_tile_system(self):
        for test_tile in self.test_tiles:
            tile_location = test_tile["tile_location"]
            tile = Tile(tile_location[0], tile_location[1], tile_location[2])
            self.assertEquals(tile.quad_tree(), test_tile["quad_tree"])

    def test_to_point_returns_correct_geographical_coordinates_for_top_left_corner_of_tile(self):
        for test_tile in self.test_tiles:
            tile_location = test_tile["tile_location"]
            tile = Tile(tile_location[0], tile_location[1], tile_location[2])
            self.assertAlmostEqual(tile.to_point()[0], test_tile["to_point"][0], places=8)
            self.assertAlmostEqual(tile.to_point()[1], test_tile["to_point"][1], places=8)

    def test_to_rectangle_returns_correct_geographical_coordinates_for_corners_of_tile(self):
        for test_tile in self.test_tiles:
            tile_location = test_tile["tile_location"]
            tile = Tile(tile_location[0], tile_location[1], tile_location[2])
            rectangle = tile.to_rectangle()
            # Test top left corner
            self.assertAlmostEqual(rectangle[0][0], test_tile["to_rectangle"][0], places=8)
            self.assertAlmostEqual(rectangle[0][1], test_tile["to_rectangle"][1], places=8)
            # Test bottom right corner
            self.assertAlmostEqual(rectangle[1][0], test_tile["to_rectangle"][2], places=8)
            self.assertAlmostEqual(rectangle[1][1], test_tile["to_rectangle"][3], places=8)

    def test_lonlat_to_meters_returns_correct_values(self):
        lonlat = (145.0912857055664, -38.005496273893314)
        self.assertAlmostEqual(Tile().lonlat_to_meters(lonlat)[0], 16151488.043, places=3)
        self.assertAlmostEqual(Tile().lonlat_to_meters(lonlat)[1], -4580202.281, places=3)

        lonlat = (-180, 85.05112877980659)
        self.assertAlmostEqual(Tile().lonlat_to_meters(lonlat)[0], -20037508.343, places=3)
        self.assertAlmostEqual(Tile().lonlat_to_meters(lonlat)[1], 20037508.343, places=3)


class ProviderTest(unittest.TestCase):

    def test(self):
        self.assertEquals(1, 1)

if __name__ == '__main__':
    unittest.main()
