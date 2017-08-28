#############################################################################
#
#   Use this file to define new jobs
#   Extents in WGS84 -> (Top, Bottom, Left, Right)
#   e.g.    monash_extents = (-37.90932, -37.91144, 145.12877, 145.13168)
#           sample_extents = (-51.690410, -51.695710, -57.861578, -57.847802)
#
##############################################################################

from tile_tools import TileSet
import providers

sample1 = TileSet(
    name="East Jetty - Stanley",
    version="1",
    description="Sample download of East Jetty - Port Stanley",
    folder="SAMPLE_1",
    extents=(-51.690410, -51.695710, -57.861578, -57.847802),
    zoom_min=13,
    zoom_max=19,
    provider=providers.google
)

tdc1 = TileSet(
    name="Tristan de Chuna - Main Island",
    version="1",
    description="Tristan de Chuna - Main Island aerial imagery",
    folder="TDC1_GOOGLE",
    extents=(-37.037891, -37.217790, -12.370015, -12.202239),
    zoom_min=13,
    zoom_max=19,
    provider=providers.google
)

tdc2 = TileSet(
    name="Tristan de Chuna - Inaccessible Island",
    version="1",
    folder="TDC2_GOOGLE",
    description="Tristan de Chuna - Inaccessible Island aerial imagery",
    extents=(-37.274763, -37.331535, -12.716661, -12.625830),
    zoom_min=13,
    zoom_max=19,
    provider=providers.google
)

tdc3 = TileSet(
    name="Tristan de Chuna - Nightingale Islands",
    version="1",
    folder="TDC3_GOOGLE",
    description="Tristan de Chuna - Nightingale Islands aerial imagery",
    extents=(-37.391934, -37.445445, -12.505140, -12.460771),
    zoom_min=13,
    zoom_max=19,
    provider=providers.google
)