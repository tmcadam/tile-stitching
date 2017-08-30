#################################################################
#   Tom McAdam                                                  #
#   Copyright (c) 2016, Thomas McAdam. All rights reserved.     #
#################################################################

import sys
from tilesets import TILE_SETS
import tile_tools

# python tile.py sample3 "/home/bob/Tiles" count_tiles

sys.stdout.write("\n##### Tile Utilities ####\n\n")

t = tile_tools.TileDownloadJob(sys.argv[2], TILE_SETS[sys.argv[1]])

if sys.argv[3] == "count_tiles":
    print "Total tiles in area:\t", (t.counts["exists"] + t.counts["download"])
    print "Already downloaded:\t", t.counts["exists"]
    print "Need downloaded:\t", t.counts["download"]

elif sys.argv[3] in ["download", "proxy_download"]:
    sys.stdout.write("Tiles within extents: {}\n".format(t.counts["download"] + t.counts["exists"]))
    sys.stdout.write("Tiles already downloaded: {}\n".format(t.counts["exists"]))
    sys.stdout.write("Tiles to download: {}\n\n".format(t.counts["download"]))
    if sys.argv[3] == "proxy_download":
        from connections import CONNECTIONS
        t.init_vpn(CONNECTIONS)
        while True:
            if t.get_tiles(proxy=True):
                break
    else:
        t.get_tiles()

elif sys.argv[3] == "clean_download":
    sys.stdout.write("Checking downloaded tiles....\n")
    t.clean_download()

elif sys.argv[3] == "create_viewer":
    sys.stdout.write("Creating html viewer....")
    t.write_leaflet_viewer()

elif sys.argv[3] == "mbtiles":
    t.write_mbtiles()

elif sys.argv[3] == "geotiff":
    sys.stdout.write("Creating GeoTiff....\n")
    s = tile_tools.TileStitchJob(t)
    s.stitch()
    s.convert_tif()

else:
    print("ERROR: Command not found\n")

sys.stdout.write("\n##### Finished ####\n\n")


