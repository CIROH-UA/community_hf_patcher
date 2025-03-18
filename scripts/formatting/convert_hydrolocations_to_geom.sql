-- First, alter the table to add the geometry column
ALTER TABLE hydrolocations ADD COLUMN geom POINT;

-- Then update gpkg_contents to change it to a spatial table
UPDATE gpkg_contents 
SET 
    data_type = 'features',
    srs_id = (SELECT srs_id FROM gpkg_geometry_columns WHERE table_name = 'divides')
WHERE table_name = 'hydrolocations';

-- Also register the geometry column in gpkg_geometry_columns
INSERT INTO gpkg_geometry_columns (
    table_name,
    column_name,
    geometry_type_name,
    srs_id,
    z,
    m
)
SELECT 
    'hydrolocations',
    'geom',
    'POINT',
    srs_id,
    0,
    0
FROM gpkg_geometry_columns 
WHERE table_name = 'divides';

