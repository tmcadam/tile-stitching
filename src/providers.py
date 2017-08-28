from tile_tools import Provider

rio_outline = Provider(
                name="ESRI Rio Outline",
                tile_system="SLIPPY",
                url="http://tiles{balancer}.arcgis.com/tiles/nGt4QxSblgDfeJn9/arcgis/rest/services/Rio_de_Janeiro_Footprint/MapServer/tile/{zoom}/{y}/{x}",
                tile_format="PNG",
                balancers=["1", "2", "3", "4"],
                attribution="ESRI"
                )

osm = Provider(
                name="OSM",
                tile_system="SLIPPY",
                url="http://{balancer}.tile.openstreetmap.org/{zoom}/{x}/{y}.png",
                tile_format="PNG",
                balancers=['a', 'b', 'c'],
                attribution="Open Street Map"
               )

google = Provider(
                name="GOOGLE",
                tile_system="SLIPPY",
                url="http://mt{balancer}.google.com/vt/lyrs=s&x={x}&y={y}&z={zoom}",
                tile_format="JPG",
                balancers=['0', '1', '2', '3'],
                attribution="Google Maps"
               )

here = Provider(
                name="HERE",
                tile_system="SLIPPY",
                url="https://{balancer}.aerial.maps.api.here.com/maptile/2.1/maptile/newest/satellite.day/{zoom}/{x}/{y}/256/png8?app_id=laGAr6nRKF9kgw3Wj_cA&token=JK2oJ1CPsvhfZWX-KpbrWw&xnlp=CL_MH5v2.1.1%2CSID_279695d5849645adb906c9582245bf14&",
                tile_format="PNG",
                balancers=['4', '1', '2', '3'],
                attribution="HERE Maps"
                )
