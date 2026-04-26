"""
Fix for two failed tables:
  1. dim_region          — rename column 'region' → 'region_name'
  2. fact_annual_kpis    — drop 'formal_inclusion_pct_interp' before loading
"""


import pandas as pd
from sqlalchemy import create_engine, text
 
# Connection (same as before) 
SERVER   = "PTAHMWASH"
DATABASE = "FinancialInclusionKE"
 
CONNECTION_STRING = (
    f"mssql+pyodbc://{SERVER}/{DATABASE}"
    f"?driver=ODBC+Driver+17+for+SQL+Server"
    f"&trusted_connection=yes"
)
 
engine = create_engine(CONNECTION_STRING)
 
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Connected.\n")
except Exception as e:
    print(f"Connection failed: {e}")
    exit()
 
# Load source files 
county = pd.read_csv(r"C:\MY DOCUMENTS\Financial_Inclusion_Kenya\Data\Clean Data\c_County_Financial_Inclusion_2024.csv")
kpis   = pd.read_csv(r"C:\MY DOCUMENTS\Financial_Inclusion_Kenya\Data\Clean Data\c_Annual_KPIs_Summary.csv")
 
 
# FIX 1: dim_region 
# Problem: SQL table column is 'region_name' but Python was sending 'region'
# Fix:     rename the column before loading
 
dim_region = (
    county[["region"]]
    .drop_duplicates()
    .sort_values("region")
    .reset_index(drop=True)
)
dim_region.insert(0, "region_id", range(1, len(dim_region) + 1))
 
# Rename to match what the SQL table expects
dim_region = dim_region.rename(columns={"region": "region_name"})
 
 
# FIX 2: fact_annual_kpis
# Problem: CSV has 'formal_inclusion_pct_interp' but SQL table does not
# Fix:     drop that extra column before loading
 
fact_annual_kpis = kpis.drop(columns=["formal_inclusion_pct_interp"], errors="ignore")
# errors="ignore" means no crash if column doesn't exist — safe to keep
 
print(f"fact_annual_kpis columns going to SQL:\n{list(fact_annual_kpis.columns)}\n")
 
 
# Load only the two failed tables
FIXES = {
    "dim_region"      : dim_region,
    "fact_annual_kpis": fact_annual_kpis,
}
 
for table_name, df in FIXES.items():
    try:
        df.to_sql(
            name      = table_name,
            con       = engine,
            if_exists = "append",
            index     = False,
            schema    = "dbo",
        )
        print(f"  Loaded  {table_name:<25} {len(df):>5} rows  [OK]")
    except Exception as e:
        print(f"  FAILED  {table_name:<25} Error: {e}")