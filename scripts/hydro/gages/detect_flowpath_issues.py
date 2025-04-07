import sqlite3
import csv
import os
import sys
from pathlib import Path

# Ignore any entries where the absolute difference in area is below this value
MIN_ABSOLUTE_DIFFERENCE = 10

# The percentage difference between the USGS area data and hydrofabric data required to call entry incorrect
INCORRECT_FILTER = 90

# The minimum percentage difference between the suggested corrected hydrofabric data and the USGS data
REPLACEMENT_THRESHOLD = 15

#e.g. if the hydrofabric data for a gage is more than 90% different from the USGS data 
# AND there is a possible correction that is within 15% of the USGS value, then update the hydrofabric with the correction

def compare_areas(csv_file_path, sqlite_db_path):
    """
    Compare areas from CSV file with areas in SQLite database.
    Identifies gages where the area differs by more than INCORRECT_FILTER.
    For each discrepancy, checks if a better match exists among flowpaths with the same to_id.
    
    Args:
        csv_file_path (str): Path to the CSV file containing gage and area_sqkm
        sqlite_db_path (str): Path to the SQLite database
    """
    # Load the CSV data into a dictionary
    csv_areas = {}
    try:
        with open(csv_file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Check if the required columns exist
            if 'gage' not in reader.fieldnames or 'area_sqkm' not in reader.fieldnames:
                print(f"Error: CSV file must contain 'gage' and 'area_sqkm' columns.")
                return
                
            for row in reader:
                try:
                    gage_id = row['gage']
                    area = float(row['area_sqkm'])
                    csv_areas[gage_id] = area
                except (ValueError, KeyError) as e:
                    print(f"Warning: Could not process row {row}: {e}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    print(f"Loaded {len(csv_areas)} gages from CSV file.")
    
    # Connect to the SQLite database
    try:
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()
        
        # Check if the required tables and columns exist
        cursor.execute("PRAGMA table_info('flowpath-attributes')")
        flowpath_attrs_cols = [col[1] for col in cursor.fetchall()]
        
        if 'gage' not in flowpath_attrs_cols or 'id' not in flowpath_attrs_cols:
            print("Error: 'flowpath-attributes' table must contain 'gage' and 'id' columns.")
            conn.close()
            return
            
        cursor.execute("PRAGMA table_info(flowpaths)")
        flowpaths_cols = [col[1] for col in cursor.fetchall()]
        
        required_cols = ['id', 'tot_drainage_areasqkm', 'toid']
        missing_cols = [col for col in required_cols if col not in flowpaths_cols]
        if missing_cols:
            print(f"Error: flowpaths table must contain {', '.join(required_cols)} columns.")
            conn.close()
            return
        
        # Create an index on the toid column to speed up queries
        print("Creating index on flowpaths.toid to improve query performance...")
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_flowpaths_toid ON flowpaths (toid)")
            conn.commit()
            print("Index created successfully.")
        except sqlite3.Error as e:
            print(f"Warning: Could not create index: {e}")
        
        # Query to get the database areas for each gage along with toid
        query = """
        SELECT fa.gage, fp.tot_drainage_areasqkm, fp.id, fp.toid
        FROM 'flowpath-attributes' fa
        JOIN flowpaths fp ON fa.id = fp.id
        WHERE fa.gage IS NOT NULL
        """
        
        cursor.execute(query)
        db_info = {}
        for row in cursor.fetchall():
            gage, area, fp_id, toid = row
            try:
                db_info[gage] = {
                    'area': float(area),
                    'id': fp_id,
                    'toid': toid
                }
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not process database row for gage {gage}: {e}")
        
        print(f"Retrieved {len(db_info)} gages from database.")
        
        # Find discrepancies
        discrepancies = []
        for gage_id, csv_area in csv_areas.items():
            if gage_id in db_info:
                db_area = db_info[gage_id]['area']
                
                # Calculate percentage difference
                if csv_area == 0 and db_area == 0:
                    continue  # Skip if both areas are zero
                    
                if csv_area == 0:
                    pct_diff = float('inf')  # Infinite difference if CSV area is zero
                else:
                    pct_diff = abs(csv_area - db_area) / csv_area * 100

                if abs(csv_area - db_area) < MIN_ABSOLUTE_DIFFERENCE:
                    continue
                    
                # Check if difference is more than 50%
                if pct_diff > INCORRECT_FILTER:
                    discrepancies.append({
                        'gage_id': gage_id,
                        'csv_area_sqkm': csv_area,
                        'db_area_sqkm': db_area,
                        'pct_diff': pct_diff,
                        'fp_id': db_info[gage_id]['id'],
                        'toid': db_info[gage_id]['toid']
                    })
            else:
                print(f"Warning: Gage {gage_id} from CSV not found in database.")
        
        print(f"Initial discrepancies found: {len(discrepancies)}")
        
        # Check for better matches for each discrepancy
        final_discrepancies = []
        replacements = []
        
        for disc in discrepancies:
            gage_id = disc['gage_id']
            csv_area = disc['csv_area_sqkm']
            toid = disc['toid']
            
            if toid is None:
                print(f"Warning: Gage {gage_id} has NULL toid, cannot find replacement")
                final_discrepancies.append(disc)
                continue
            
            # Find all flowpaths with the same toid
            # Using the index created earlier should make this query much faster
            cursor.execute("""
                SELECT fp.id, fp.tot_drainage_areasqkm
                FROM flowpaths fp
                LEFT JOIN 'flowpath-attributes' fa ON fp.id = fa.id
                WHERE fp.toid = ? AND fp.id != ?
            """, (toid, disc['fp_id']))
            
            potential_matches = []
            for row in cursor.fetchall():
                fp_id, area = row
                try:
                    potential_matches.append({
                        'fp_id': fp_id,
                        'area': float(area) if area is not None else 0,
                    })
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not process potential match {fp_id}: {e}")
            
            # Calculate differences for potential matches
            better_match = None
            for match in potential_matches:
                match_area = match['area']
                
                if csv_area == 0:
                    if match_area == 0:
                        match_pct_diff = 0
                    else:
                        match_pct_diff = float('inf')
                else:
                    match_pct_diff = abs(csv_area - match_area) / csv_area * 100
                
                # If this match has a smaller percentage difference, it's better
                if match_pct_diff < disc['pct_diff'] and match_pct_diff < REPLACEMENT_THRESHOLD:
                    if better_match is None or match_pct_diff < better_match['pct_diff']:
                        better_match = {
                            'fp_id': match['fp_id'],
                            'area': match_area,
                            'pct_diff': match_pct_diff
                        }
            
            if better_match:
                # We found a better match
                replacements.append({
                    'gage_id': gage_id,
                    'csv_area_sqkm': csv_area,
                    'original_fp_id': disc['fp_id'],
                    'original_db_area_sqkm': disc['db_area_sqkm'],
                    'original_pct_diff': disc['pct_diff'],
                    'replacement_fp_id': better_match['fp_id'],
                    'replacement_db_area_sqkm': better_match['area'],
                    'replacement_pct_diff': better_match['pct_diff']
                })
            else:
                # No better match found, keep this as a discrepancy
                final_discrepancies.append(disc)
        
        # Close the database connection
        conn.close()
        
    except Exception as e:
        print(f"Error accessing SQLite database: {e}")
        if 'conn' in locals():
            conn.close()
        return
    
    # Output the results for discrepancies
    print(f"\nFinal discrepancies (no better match found): {len(final_discrepancies)}")
    
    # Sort by percentage difference (largest first)
    final_discrepancies.sort(key=lambda x: x['pct_diff'], reverse=True)
    
    # Write discrepancies to a CSV file
    discrepancies_file = 'area_discrepancies.csv'
    with open(discrepancies_file, 'w', newline='') as csvfile:
        fieldnames = ['gage_id', 'csv_area_sqkm', 'db_area_sqkm', 'pct_diff', 'fp_id', 'toid']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for disc in final_discrepancies:
            writer.writerow(disc)
            print(f"Gage {disc['gage_id']}: CSV area = {disc['csv_area_sqkm']:.2f} km², "
                  f"DB area = {disc['db_area_sqkm']:.2f} km², "
                  f"Difference = {disc['pct_diff']:.2f}%, "
                  f"No better match found")
    
    print(f"Discrepancies without suitable replacements written to {discrepancies_file}")
    
    # Output the results for replacements
    print(f"\nPotential replacements found: {len(replacements)}")
    
    # Sort by improvement in percentage difference (largest first)
    replacements.sort(key=lambda x: x['original_pct_diff'] - x['replacement_pct_diff'], reverse=True)
    
    # Write replacements to a CSV file
    replacements_file = 'area_replacements.csv'
    with open(replacements_file, 'w', newline='') as csvfile:
        fieldnames = [
            'gage_id', 'csv_area_sqkm', 
            'original_fp_id', 'original_db_area_sqkm', 'original_pct_diff',
            'replacement_fp_id', 'replacement_db_area_sqkm', 'replacement_pct_diff'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for repl in replacements:
            writer.writerow(repl)
            print(f"Gage {repl['gage_id']}: CSV area = {repl['csv_area_sqkm']:.2f} km², "
                  f"Original DB area = {repl['original_db_area_sqkm']:.2f} km² (diff = {repl['original_pct_diff']:.2f}%), "
                  f"Replacement DB area = {repl['replacement_db_area_sqkm']:.2f} km² (diff = {repl['replacement_pct_diff']:.2f}%)")
    
    print(f"Potential replacements written to {replacements_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_areas.py <csv_file_path> <sqlite_db_path>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    sqlite_db = sys.argv[2]
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found.")
        sys.exit(1)
        
    if not os.path.exists(sqlite_db):
        print(f"Error: SQLite database '{sqlite_db}' not found.")
        sys.exit(1)
    
    compare_areas(csv_file, sqlite_db)