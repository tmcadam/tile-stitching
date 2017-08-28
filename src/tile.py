import sys
import tilesets
import tile_tools

# python tile.py "/home/tmcadam/Desktop/Tiles" download

sys.stdout.write("\n##### Tile Utilities ####\n\n")

OUT_DIR = sys.argv[1]

t = tile_tools.TileDownloadJob(OUT_DIR, tilesets.sample1)

if sys.argv[2] == "count_tiles":
    print "Total tiles in area:\t", (t.counts["exists"] + t.counts["download"])
    print "Already downloaded:\t", t.counts["exists"]
    print "Need downloaded:\t", t.counts["download"]
elif sys.argv[2] == "download":
    sys.stdout.write("Tiles within extents: {}\n".format(t.counts["download"] + t.counts["exists"]))
    sys.stdout.write("Tiles already downloaded: {}\n".format(t.counts["exists"]))
    sys.stdout.write("Tiles to download: {}\n\n".format(t.counts["download"]))
    t.get_tiles()
elif sys.argv[2] == "clean_download":
    sys.stdout.write("Checking downloaded tiles....\n")
    t.clean_download()
elif sys.argv[2] == "create_viewer":
    sys.stdout.write("Creating html viewer....")
    t.write_leaflet_viewer()
elif sys.argv[2] == "mbtiles":
    t.write_mbtiles()
elif sys.argv[2] == "geotiff":
    sys.stdout.write("Creating GeoTiff....\n")
    ## This is used to create a geotiff, mainly for ArcMap users.
    s = tile_tools.TileStitchJob(t)
    s.stitch()
    s.convert_tif()
else:
    print("ERROR: Command not found\n")

sys.stdout.write("\n##### Finished ####\n\n")


