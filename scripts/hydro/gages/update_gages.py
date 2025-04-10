import csv
import sqlite3

GAGE_CSV = "/workspace/gage_replacements.csv"
HYDROFABRIC_PATH = '/raw_hf/conus_nextgen.gpkg'


def update_gages_in_bulk(conn: sqlite3.Connection, updates):
    # Prepare batched updates
    gages_to_remove = []
    flowpath_attrs_updates = []
    flowpath_attrs_ml_updates = []
    hydrolocations_updates = []
    pois_updates = []

    # Use a set to avoid duplicate gage_ids for removal
    gages_to_remove_set = {gage_id for gage_id, _, _ in updates}

    # Prepare batched updates
    for gage_id, wb_id, nex in updates:
        # Prepare updates for flowpath-attributes and flowpath-attributes-ml
        flowpath_attrs_updates.append((gage_id, nex, wb_id))
        flowpath_attrs_ml_updates.append((gage_id, nex, wb_id))

        # Prepare updates for hydrolocations
        hydrolocations_updates.append((wb_id, f"gages-{gage_id}"))

        # Prepare updates for pois
        pois_updates.append((wb_id, f"gages-{gage_id}"))

    # Execute batched updates for setting gage and gage_nex_id to NULL
    conn.execute(
        f"UPDATE 'flowpath-attributes' SET gage = NULL, gage_nex_id = NULL WHERE gage IN ({','.join(['?'] * len(gages_to_remove_set))});",
        list(gages_to_remove_set),
    )
    conn.execute(
        f"UPDATE 'flowpath-attributes-ml' SET gage = NULL, gage_nex_id = NULL WHERE gage IN ({','.join(['?'] * len(gages_to_remove_set))});",
        list(gages_to_remove_set),
    )
    # Execute the rest of the updates
    conn.executemany(
        "UPDATE 'flowpath-attributes' SET gage = ?, gage_nex_id = ? WHERE id = ?;",
        flowpath_attrs_updates,
    )
    conn.executemany(
        "UPDATE 'flowpath-attributes-ml' SET gage = ?, gage_nex_id = ? WHERE id = ?;",
        flowpath_attrs_ml_updates,
    )
    conn.executemany(
        "UPDATE hydrolocations SET id = ? WHERE hl_uri = ?;",
        hydrolocations_updates,
    )
    conn.executemany(
        "UPDATE pois SET id = ? WHERE poi_id = (SELECT poi_id FROM hydrolocations WHERE hl_uri = ?);",
        pois_updates,
    )


def main():
    with sqlite3.connect(HYDROFABRIC_PATH) as conn:
        conn.isolation_level = "EXCLUSIVE"  # Use a single transaction
        with open(GAGE_CSV, 'r') as csvfile:
            updates = []
            for row in csv.DictReader(csvfile):
                gage_id = row["gage_id"]
                wb_id = row["replacement_fp_id"]

                # Fetch downstream nexus (cache results if possible)
                nex = conn.execute(
                    "SELECT toid FROM flowpaths WHERE id = ?;", (wb_id,)
                ).fetchone()[0]

                updates.append((gage_id, wb_id, nex))

            # Perform batched updates
            update_gages_in_bulk(conn, updates)

        conn.commit()  # Commit all changes in one go


if __name__ == "__main__":
    main()
