#################################################################
#   Tom McAdam                                                  #
#   Copyright (c) 2016, Thomas McAdam. All rights reserved.     #
#################################################################

#   Use this file to define new jobs
#   Extents in WGS84 -> (Top, Bottom, Left, Right)


from tile_tools import TileSet
import providers

TILE_SETS = {
    "sample1": TileSet(
        name="East Jetty - Stanley",
        version="1",
        description="Sample download of East Jetty - Port Stanley",
        folder="SAMPLE_1",
        extents=(-51.690410, -51.695710, -57.861578, -57.847802),
        zoom_min=13,
        zoom_max=19,
        provider=providers.google),
    "sample2": TileSet(
        name="Monash Uni = Melbourne",
        version="1",
        description="Sample download of Monash uni - Melbourne",
        folder="SAMPLE_2",
        extents=(-37.90932, -37.91144, 145.12877, 145.13168),
        zoom_min=13,
        zoom_max=19,
        provider=providers.google),
    "sample3": TileSet(
        name='Big Sample Area',
        version='1',
        description='A large sample area',
        folder="SAMPLE_3",
        extents=(-37.037891, -37.217790, -12.370015, -12.202239),
        zoom_min=13,
        zoom_max=19,
        provider=providers.google)
}
