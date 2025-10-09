DROP TABLE "error";
DROP TABLE "rtree_error_geom";
-- Removing the top two tables seems to automatically remove the triggers as well.
-- DROP TRIGGER "rtree_error_geom_delete";
-- DROP TRIGGER "rtree_error_geom_insert";
-- DROP TRIGGER "rtree_error_geom_update1";
-- DROP TRIGGER "rtree_error_geom_update2";
-- DROP TRIGGER "rtree_error_geom_update3";
-- DROP TRIGGER "rtree_error_geom_update4";
-- DROP TRIGGER "trigger_insert_feature_count_error";
-- DROP TRIGGER "trigger_delete_feature_count_error";
DELETE FROM gpkg_ogr_contents WHERE table_name="error";
DELETE FROM gpkg_geometry_columns WHERE table_name="error";
DELETE FROM gpkg_extensions WHERE table_name="error";
DELETE FROM gpkg_contents WHERE table_name="error";
DELETE FROM sqlite_sequence WHERE name="error";
