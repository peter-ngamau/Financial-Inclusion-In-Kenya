import pandas as pd
from sqlalchemy import create_engine, text


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Set your connection details
# ─────────────────────────────────────────────────────────────────────────────

SERVER   = "PTAHMWASH"               
DATABASE = "FinancialInclusionKE"    

# Windows Authentication (uses your Windows login — most common for local SQL Server)
CONNECTION_STRING = (
    f"mssql+pyodbc://{SERVER}/{DATABASE}"
    f"?driver=ODBC+Driver+17+for+SQL+Server"
    f"&trusted_connection=yes"
)

engine = create_engine(CONNECTION_STRING)

# Quick connection test — stops here if your server or database name is wrong
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Connected to SQL Server successfully.\n")
except Exception as e:
    print(f"Connection failed: {e}")
    print("\nThings to check:")
    print("  1. Is SQL Server running? Open SSMS and try to connect manually.")
    print("  2. Is the SERVER name correct? Try 'localhost' or '.\\SQLEXPRESS'")
    print("  3. Is ODBC Driver 17 installed? Download from https://aka.ms/downloadmsodbcsql")
    exit()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Load all 6 CSV files into DataFrames
# ─────────────────────────────────────────────────────────────────────────────

monthly= pd.read_csv(r"C:\MY DOCUMENTS\Financial_Inclusion_Kenya\Data\Clean Data\c_Mobile_Money_Monthly_Transactions_2015_2024.csv")
county= pd.read_csv(r"C:\MY DOCUMENTS\Financial_Inclusion_Kenya\Data\Clean Data\c_County_Financial_Inclusion_2024.csv")
finaccess= pd.read_csv(r"C:\MY DOCUMENTS\Financial_Inclusion_Kenya\Data\Clean Data\c_FinAccess_Historical_Survey_2006_2024.csv")
agents= pd.read_csv(r"C:\MY DOCUMENTS\Financial_Inclusion_Kenya\Data\Clean Data\c_Agent_Network_by_County.csv")
demographics= pd.read_csv(r"C:\MY DOCUMENTS\Financial_Inclusion_Kenya\Data\Clean Data\c_Demographic_Exclusion_Analysis.csv")
kpis= pd.read_csv(r"C:\MY DOCUMENTS\Financial_Inclusion_Kenya\Data\Clean Data\c_Annual_KPIs_Summary.csv")


# Add a period column to monthly — useful for Power BI time axis
monthly["period"] = (
    monthly["year"].astype(str) + "-" +
    monthly["month"].astype(str).str.zfill(2)
)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Build dimension tables
# Each dim table is a small lookup table that other tables reference
# ─────────────────────────────────────────────────────────────────────────────

# dim_county — one row per county
dim_county = county[[
    "county_id", "county_name", "region",
    "population_2024", "high_inclusion_flag"
]].drop_duplicates(subset="county_id").sort_values("county_id")

# dim_date — one row per year-month combination (120 rows)
dim_date = monthly[["year", "month", "month_name", "period"]].copy()
dim_date["quarter"] = monthly["month"].apply(lambda m: (m - 1) // 3 + 1)
dim_date["date_id"] = (
    dim_date["year"].astype(str) +
    dim_date["month"].astype(str).str.zfill(2)
).astype(int)   
dim_date = dim_date.sort_values("date_id").reset_index(drop=True)

# dim_demographic — one row per demographic segment
dim_demographic = demographics[["segment", "category", "primary_barrier"]].copy()
dim_demographic.insert(0, "segment_id", range(1, len(dim_demographic) + 1))

# dim_region — one row per region
dim_region = (
    county[["region"]]
    .drop_duplicates()
    .sort_values("region")
    .reset_index(drop=True)
)
dim_region.insert(0, "region_id", range(1, len(dim_region) + 1))

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — Build fact tables
# Fact tables hold the measurable numbers
# ─────────────────────────────────────────────────────────────────────────────

# fact_mobile_transactions — monthly transaction data
fact_mobile_transactions = monthly.merge(
    dim_date[["year", "month", "date_id"]],
    on=["year", "month"],
    how="left"
)[[
    "date_id", "year", "month", "month_name", "period",
    "active_agents", "registered_accounts_m", "active_accounts_m",
    "txn_volume_m", "txn_value_kes_b", "avg_txn_size_kes",
    "agent_cico_volume_m", "agent_cico_value_kes_b"
]]

# fact_county_inclusion — county-level financial inclusion metrics
fact_county_inclusion = county.merge(
    agents[[
        "county_name", "active_agents_2024",
        "agents_per_10k_pop", "agent_density_tier", "settlement_type"
    ]],
    on="county_name", how="left"
)
fact_county_inclusion["survey_year"] = 2024
fact_county_inclusion["excluded_population"] = (
    fact_county_inclusion["population_2024"] *
    fact_county_inclusion["exclusion_pct"]
).round(0).astype(int)
fact_county_inclusion["urban_rural_gap_pct"] = (
    fact_county_inclusion["urban_inclusion_pct"] -
    fact_county_inclusion["rural_inclusion_pct"]
).round(4)

# fact_demographic_exclusion — segment-level exclusion data
fact_demographic_exclusion = demographics.merge(
    dim_demographic[["segment", "segment_id"]],
    on="segment", how="left"
)
NATIONAL_EXCL = 0.099
fact_demographic_exclusion["relative_exclusion_idx"] = (
    fact_demographic_exclusion["excluded_pct"] / NATIONAL_EXCL
).round(3)
fact_demographic_exclusion["survey_year"] = 2024

# fact_annual_kpis — one row per year, national-level KPIs
fact_annual_kpis = kpis.copy()

# fact_finaccess_trends — historical survey data (7 survey waves)
fact_finaccess_trends = finaccess.copy()
fact_finaccess_trends["inclusion_change_pp"] = (
    finaccess["formal_access_pct"].diff().round(4)
)
fact_finaccess_trends["excluded_change_pp"] = (
    finaccess["excluded_pct"].diff().round(4)
)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — Write to SQL Server
# if_exists="append"  → adds rows to your existing tables
# if_exists="replace" → drops and recreates the table (careful!)
# index=False         → don't write the pandas row numbers as a column
# ─────────────────────────────────────────────────────────────────────────────

TABLES = {
    # Dimension tables
    "dim_county"              : dim_county,
    "dim_date"                : dim_date,
    "dim_demographic"         : dim_demographic,
    "dim_region"              : dim_region,
    # Fact tables
    "fact_mobile_transactions"  : fact_mobile_transactions,
    "fact_county_inclusion"     : fact_county_inclusion,
    "fact_demographic_exclusion": fact_demographic_exclusion,
    "fact_annual_kpis"          : fact_annual_kpis,
    "fact_finaccess_trends"     : fact_finaccess_trends,
}

for table_name, df in TABLES.items():
    try:
        df.to_sql(
            name      = table_name,
            con       = engine,
            if_exists = "append",   # change to "replace" to wipe and reload
            index     = False,
            schema    = "dbo",
        )
        print(f"  Loaded  {table_name:<35} {len(df):>5} rows")
    except Exception as e:
        print(f"  FAILED  {table_name:<35} Error: {e}")




