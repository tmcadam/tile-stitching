import sys
import tilesets
import tile_tools

# python tile.py "/home/tmcadam/Desktop/Tiles" download

sys.stdout.write("\n##### Tile Utilities ####\n\n")

OUT_DIR = sys.argv[1]

t = tile_tools.TileDownloadJob(OUT_DIR, tilesets.sample1)

if sys.argv[2] == "download":
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
    sys.stdout.write("Converting to MBTiles format....")
    t.write_mbtiles()
else:
    print("ERROR: Command not found\n")

sys.stdout.write("\n##### Finished ####\n\n")

# s = TileStitchJob(t, 16)
# s.stitch()
# s.convert_tif()
