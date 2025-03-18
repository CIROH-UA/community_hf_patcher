from utils import GeoPackage

gpkg_paths = [
    "conus_nextgen.gpkg",
    # "ak_nextgen.gpkg", no hydrolocation geo data
    # "gl_nextgen.gpkg", already has geom column for hydrolocations
    # "hi_nextgen.gpkg", no hydrolocation geo data
    # "prvi_nextgen.gpkg", no hydrolocation geo data
]
gpkg_paths = ["/raw_hf/" + gpkg for gpkg in gpkg_paths]

geopackages = [GeoPackage(gpkg) for gpkg in gpkg_paths]

for gpkg in geopackages:
    # run the script
    gpkg.execute_script("convert_hydrolocations_to_geom.sql")

    # add the spatial index
    gpkg.add_spatial_index("hydrolocations", "geom")

    gpkg.populate_point_spatial_index("hydrolocations")

    # update the layer statistics
    gpkg.update_layer_statistics()

    # drop the spatialite history
    gpkg.drop_spatialite_history()