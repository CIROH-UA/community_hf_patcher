from pyproj import CRS
import sqlite3
from typing import Optional, Any
from contextlib import contextmanager


class GeoPackage:
    def __init__(self, file_name: str, pragma_options: Optional[dict] = None):
        self.file_name = file_name
        self.conn: Optional[sqlite3.Connection] = None
        self.default_pragmas = {
            "journal_mode": "WAL",
            "synchronous": "NORMAL",
            "cache_size": -2000,
            "temp_store": "MEMORY",
            "mmap_size": 268435456,
            "page_size": 4096,
        }
        self.pragma_options = {**self.default_pragmas, **(pragma_options or {})}

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.file_name, isolation_level=None)
        self.conn.enable_load_extension(True)
        try:
            self.conn.load_extension("mod_spatialite")
        except sqlite3.OperationalError as e:
            self.conn.close()
            raise RuntimeError(f"Failed to load mod_spatialite: {e}")
        with self.conn as cursor:
            for pragma, value in self.pragma_options.items():
                cursor.execute(f"PRAGMA {pragma}={value}")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(
        self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]
    ) -> None:
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            self.conn.close()
            self.conn = None

    @contextmanager
    def transaction(self):
        if not self.conn:
            raise RuntimeError("No active connection. Use 'with' statement first.")
        try:
            self.conn.execute("BEGIN")
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def create_table(self, table_name: str, schema: dict):
        with self as conn:
            cur = conn.cursor()
            sqlformatted_schema = ", ".join([f"'{k}' {v}" for k, v in schema.items()])
            sql = f'CREATE TABLE IF NOT EXISTS {table_name} ("fid" INTEGER NOT NULL, {sqlformatted_schema}, PRIMARY KEY("fid" AUTOINCREMENT))'
            cur.execute(sql)
            conn.commit()

    def add_srs_to_db(self, unique_crs: set[CRS]):
        all_crs = list(unique_crs)
        with self as conn:
            cur = conn.cursor()
            for crs in all_crs:
                cur.execute("SELECT gpkgInsertEpsgSRID(?)", (crs.to_epsg(),))
            conn.commit()

    def add_gpkg_metadata_tables(self, script_path: str):
        with open(script_path) as f:
            gpkg_tables = f.read()
        with self as conn:
            cur = conn.cursor()
            cur.executescript(gpkg_tables)
            conn.commit()

    def add_gpkg_contents(self, table_name: str, data_type: str, srs_id: int):
        with self as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO gpkg_contents (table_name, data_type, identifier, srs_id) VALUES (?,?,?,?)",
                (table_name, data_type, table_name, srs_id),
            )
            conn.commit()

    def add_gpkg_geometry_columns(
        self, table_name: str, column_name: str, geometry_type: str, srs_id: int
    ):
        with self as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) VALUES (?,?,?,?,0,0)",
                (table_name, column_name, geometry_type, srs_id),
            )
            conn.commit()

    def add_spatial_index(self, table_name: str, column_name: str):
        with self as conn:
            cur = conn.cursor()
            cur.execute("SELECT gpkgAddSpatialIndex(?, ?)", (table_name, column_name))
            conn.commit()

    def populate_point_spatial_index(self, table_name: str):
        #  Update the geometries using existing coordinates
        sql = f"""UPDATE {table_name}
         SET geom = MakePoint(hl_x, hl_y,
         (SELECT srs_id FROM gpkg_geometry_columns WHERE table_name = '{table_name}'));"""
        with self as conn:
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()

    def convert_wkb_to_gpkg_blob(self, table_name: str, geom_column: str, srs_id: int):
        with self as conn:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE {table_name} SET {geom_column} = AsGPB(GeomFromWKB({geom_column}, {srs_id}))"
            )
            conn.commit()

    def update_layer_statistics(self):
        with self as conn:
            cur = conn.cursor()
            cur.execute("SELECT UpdateLayerStatistics()")
            conn.commit()

    def drop_spatialite_history(self):
        with self as conn:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS spatialite_history")
            cur.execute('DELETE FROM sqlite_sequence WHERE name="spatialite_history"')
            conn.commit()

    def fix_gpkg_ogr_contents(self):
        with self as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO gpkg_ogr_contents ('table_name', 'feature_count') SELECT * FROM sqlite_sequence"
            )
            conn.commit()

    def add_sqlite_index(self, table_name: str, column_name: str):
        with self as conn:
            cur = conn.cursor()
            cur.execute(
                f"CREATE INDEX IF NOT EXISTS {table_name}_{column_name}_idx ON {table_name}({column_name})"
            )
            conn.commit()

    def execute_script(self, script_path: str):
        with open(script_path, "r") as f:
            script = f.read()
        with self as conn:
            cur = conn.cursor()
            cur.executescript(script)
            conn.commit()