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
    for table in gpkg.tables:
        # print(f"Processing table: {table}")
        columns = gpkg.get_columns(table)
        for column in columns:
            # print(f"Processing column: {column}")
            if column == "mean.slope_Time=":
                new_name = column.replace("_Time=", "_1km")
            else:
                new_name = column.replace("_Time=", "")

            if new_name.startswith("dksat"):
                new_name = "geom_mean." + new_name
            if new_name.startswith("psisat"):
                new_name = "geom_mean." + new_name

            gpkg.rename_column(table, column, new_name)

    gpkg.rename_column("divide-attributes", "X", "centroid_x")
    gpkg.rename_column("divide-attributes", "Y", "centroid_y")
    # update the layer statistics
    gpkg.update_layer_statistics()

    # drop the spatialite history
    gpkg.drop_spatialite_history()
