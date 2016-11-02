# Top, Bottom, Left, Right
from tile_tools import TileSet
import providers

# extents = (Top, Bottom, Left, Right)
#yogya_extents = (-7.74042, -7.84275, 110.31925, 110.41628)
#rio_extents = (-22.744461, -23.092303, -43.836728, -43.089037)
#monash_extents = (-37.90932, -37.91144, 145.12877, 145.13168)


tdc1 = TileSet(
    name='Tristan de Chuna - Main Island',
    version='1',
    description='Tristan de Chuna - Main Island aerial imagery',
    folder="TDC1_GOOGLE",
    extents=(-37.037891, -37.217790, -12.370015, -12.202239),
    zoom_min=13,
    zoom_max=19,
    provider=providers.google
)

tdc2 = TileSet(
    name='Tristan de Chuna - Inaccessible Island',
    version='1',
    folder="TDC2_GOOGLE",
    description='Tristan de Chuna - Inaccessible Island aerial imagery',
    extents=(-37.274763, -37.331535, -12.716661, -12.625830),
    zoom_min=13,
    zoom_max=19,
    provider=providers.google
)

tdc3 = TileSet(
    name='Tristan de Chuna - Nightingale Islands',
    version='1',
    folder="TDC3_GOOGLE",
    description='Tristan de Chuna - Nightingale Islands aerial imagery',
    extents=(-37.391934, -37.445445, -12.505140, -12.460771),
    zoom_min=13,
    zoom_max=19,
    provider=providers.google
)