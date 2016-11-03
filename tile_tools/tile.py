import sys
import tilesets
import tile_tools

# check for small files
#  find .  -type f -not -size +1k -name "*.png" | wc -l
#  find .  -type f -not -size +1k -name "*.png" -delete | wc -l

sys.stdout.write("\n##### Tile Utilities ####\n\n")

OUT_DIR = "/home/tom/Desktop/Tiles"

t = tile_tools.TileDownloadJob(OUT_DIR, tilesets.tdc1)

sys.stdout.write("Tiles within extents: {}\n".format(t.counts["download"] + t.counts["exists"]))
sys.stdout.write("Tiles already downloaded: {}\n".format(t.counts["exists"]))
sys.stdout.write("Tiles to download: {}\n\n".format(t.counts["download"]))

t.get_tiles()
#t.write_leaflet_viewer()
#t.write_mbtiles()

sys.stdout.write("\n##### Downloads Finished ####\n\n")

# s = TileStitchJob(t, 16)
# s.stitch()
# s.convert_tif()
