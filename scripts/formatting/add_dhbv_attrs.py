import pandas as pd
import sqlite3

dhbv_attrs = pd.read_parquet("dhbv_attrs.parquet")

gpkg_path = "conus_nextgen.gpkg"
con = sqlite3.connect(gpkg_path)

dhbv_attrs.to_sql(name="dhbv_attributes", con=con, if_exists='replace', index=False)
