#################################################################
#   Tom McAdam                                                  #
#   Copyright (c) 2016, Thomas McAdam. All rights reserved.     #
#################################################################

#   Use this file to define new jobs
#   Extents in WGS84 -> (Top, Bottom, Left, Right)
#   e.g.    monash_extents = (-37.90932, -37.91144, 145.12877, 145.13168)
#           sample_extents = (-51.690410, -51.695710, -57.861578, -57.847802)


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