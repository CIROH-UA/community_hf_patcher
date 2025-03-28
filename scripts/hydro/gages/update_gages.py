import csv
import sqlite3

GAGE_CSV = '/workspace/gages/gages.csv'
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


def main():
    with sqlite3.connect(HYDROFABRIC_PATH,autocommit=True) as conn:
        with open(GAGE_CSV, 'r') as csvfile:
            # drop the header 
            _ = csvfile.readline()
            for gage, wb_id in csv.reader(csvfile):
                update_gage(conn, gage, wb_id)



if __name__ == "__main__":
    main()
