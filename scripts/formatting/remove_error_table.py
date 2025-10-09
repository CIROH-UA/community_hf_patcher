from utils import GeoPackage

gpkg_paths = [
    # "conus_nextgen.gpkg",
    "ak_nextgen.gpkg",
    # "gl_nextgen.gpkg",
    "hi_nextgen.gpkg",
    "prvi_nextgen.gpkg",
]
gpkg_paths = ["/raw_hf/" + gpkg for gpkg in gpkg_paths]

geopackages = [GeoPackage(gpkg) for gpkg in gpkg_paths]

for gpkg in geopackages:
    # run the script
    gpkg.execute_script("remove_error_table.sql")

    # update the layer statistics
    gpkg.update_layer_statistics()

    # drop the spatialite history
    gpkg.drop_spatialite_history()
