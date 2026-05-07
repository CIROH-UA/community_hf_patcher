import sqlite3

gpkg_path = "/raw_hf/conus_nextgen.gpkg"
con = sqlite3.connect(gpkg_path)

# SNOW17 attributes
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "scf" REAL DEFAULT 1.100')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "si" REAL DEFAULT 500.00')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "pxtemp" REAL DEFAULT 1.000')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "nmf" REAL DEFAULT 0.150')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "tipm" REAL DEFAULT 0.100')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "mbase" REAL DEFAULT 0.000')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "plwhc" REAL DEFAULT 0.030')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "daygm" REAL DEFAULT 0.000')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc1" REAL DEFAULT 0.050')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc2" REAL DEFAULT 0.100')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc3" REAL DEFAULT 0.200')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc4" REAL DEFAULT 0.300')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc5" REAL DEFAULT 0.400')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc6" REAL DEFAULT 0.500')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc7" REAL DEFAULT 0.600')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc8" REAL DEFAULT 0.700')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc9" REAL DEFAULT 0.800')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc10" REAL DEFAULT 0.900')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adc11" REAL DEFAULT 1.000')

con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "mfmax" REAL DEFAULT 1.25')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "mfmin" REAL DEFAULT 0.55')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "uadj" REAL DEFAULT 0.11')

# SAC-SMA attributes

con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "adimp" REAL DEFAULT 0.0000')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "pctim" REAL DEFAULT 0.0000')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "riva" REAL DEFAULT 0.000')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "side" REAL DEFAULT 0.000')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "rserv" REAL DEFAULT 0.3000')

con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "uztwm" REAL DEFAULT 75.5')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "uzfwm" REAL DEFAULT 75.5')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "lztwm" REAL DEFAULT 500.5')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "lzfpm" REAL DEFAULT 500.5')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "lzfsm" REAL DEFAULT 500.5')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "uzk" REAL DEFAULT 0.3')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "lzpk" REAL DEFAULT 0.01255')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "lzsk" REAL DEFAULT 0.13')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "zperc" REAL DEFAULT 125.5')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "rexp REAL DEFAULT 3.0')
con.execute('ALTER TABLE "divide-attributes" ADD COLUMN "pfree" REAL DEFAULT 0.3')

con.commit()
con.close()
