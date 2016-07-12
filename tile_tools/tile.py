from tile_tools import TileStitchJob
from tile_tools import TileDownloadJob
from tile_tools import TileSet
from tile_tools import Provider

sys.stdout.write("\n##### Tile Utilities ####\n\n")


rio_outline = Provider(name="ESRI Rio Outline",
                       tile_system="SLIPPY",
                       url="http://tiles{balancer}.arcgis.com/tiles/nGt4QxSblgDfeJn9/arcgis/rest/services/Rio_de_Janeiro_Footprint/MapServer/tile/{zoom}/{y}/{x}",
                       tile_format="PNG",
                       balancers=["1", "2", "3", "4"]
                       )

osm = Provider(name="OSM",
               tile_system="SLIPPY",
               url="http://{balancer}.tile.openstreetmap.org/{zoom}/{x}/{y}.png",
               tile_format="PNG",
               balancers=['a', 'b', 'c']
               )

# # Top, Bottom, Left, Right
tileset = TileSet(-22.744461, -23.092303, -43.836728, -43.089037, 16, 16, provider=rio_outline)

out_dir = "/home/tmcadam/Desktop/Tiles"
t = TileDownloadJob(out_dir, "RIO", tileset)

sys.stdout.write("Tiles within extents: {}\n".format(t.counts["download"] + t.counts["exists"]))
sys.stdout.write("Tiles already downloaded: {}\n".format(t.counts["exists"]))
sys.stdout.write("Tiles to download: {}\n\n".format(t.counts["download"]))

t.get_tiles()
t.write_leaflet_viewer()

sys.stdout.write("\n##### Downloads Finished ####\n\n")

s = TileStitchJob(t, 16)
s.stitch()
s.convert_tif()