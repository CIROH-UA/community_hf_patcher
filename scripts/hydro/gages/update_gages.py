import csv
import sqlite3

GAGE_CSV = "/workspace/area_replacements.csv"
HYDROFABRIC_PATH = '/raw_hf/conus_nextgen.gpkg'


def update_gage(conn: sqlite3.Connection, gage_id, wb_id):

    # remove incorrect gage assignment
    sql = "UPDATE 'flowpath-attributes' SET gage = NULL, gage_nex_id = NULL WHERE gage = ?;"
    conn.execute(sql, (gage_id,))
    sql = "UPDATE 'flowpath-attributes-ml' SET gage = NULL, gage_nex_id = NULL WHERE gage = ?;"
    conn.execute(sql, (gage_id,))

    # get downstream nexus
    # this takes a while because there are no indices on the network table yet
    nex = conn.execute("SELECT toid FROM network WHERE id = ?;", (wb_id,)).fetchone()[0]

    # add the correct gage assignment
    params = (gage_id, nex, wb_id)
    sql = "UPDATE 'flowpath-attributes' SET gage = ?, gage_nex_id = ? WHERE id = ?;"
    conn.execute(sql, params)
    sql = "UPDATE 'flowpath-attributes-ml' SET gage = ?, gage_nex_id = ? WHERE id = ?;"
    conn.execute(sql, params)

    # update hydrolocations table
    sql = "UPDATE hydrolocations SET id = ? WHERE hl_uri = ?;"
    conn.execute(sql, (wb_id, f'gages-{gage_id}'))

    # update the pois table
    sql = "UPDATE pois SET id = ? WHERE poi_id = (SELECT poi_id FROM hydrolocations WHERE hl_uri = ?);"
    conn.execute(sql, (wb_id, f'gages-{gage_id}'))


def add_index(sqlite_db_path):
    # CREATE INDEX "ntid" ON "network" ( "toid" ASC );
    # Create an index on the toid column to speed up queries
    print("Creating index on network.toid to improve query performance...")
    with sqlite3.connect(sqlite_db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_flowpaths_toid ON flowpaths (toid)")
            conn.commit()
            print("Index created successfully.")
        except sqlite3.Error as e:
            print(f"Warning: Could not create index: {e}")


def main():
    add_index(HYDROFABRIC_PATH)
    with sqlite3.connect(HYDROFABRIC_PATH,autocommit=True) as conn:
        with open(GAGE_CSV, 'r') as csvfile:
            for row in csv.DictReader(csvfile):
                # gage_id, replacement_fp_id
                gage_id = row["gage_id"]
                wb_id = row["replacement_fp_id"]
                update_gage(conn, gage_id, wb_id)


if __name__ == "__main__":
    main()
