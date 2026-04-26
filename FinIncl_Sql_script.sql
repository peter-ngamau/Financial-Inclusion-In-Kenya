-- Create Database
CREATE DATABASE FinancialInclusionKE;

USE FinancialInclusionKE;
GO

--Create Tables
--Dim Tables
--  dim_region
-- 8 rows — one per Kenya region
CREATE TABLE dim_region (
    region_id   INT PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL
);

-- dim_county 
-- 47 rows — one per Kenya county
CREATE TABLE dim_county (
    county_id INT PRIMARY KEY,
    county_name VARCHAR(100) NOT NULL,
    region VARCHAR(50)  NOT NULL,
    population_2024 INT NOT NULL,
    high_inclusion_flag VARCHAR(5) NOT NULL    
);

-- dim_date 
-- 120 rows — one per year-month 2015 to 2024
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,    
    year INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20)  NOT NULL,
    quarter INT NOT NULL,
    period VARCHAR(7) NOT NULL        
);

-- ── dim_demographic ──────────────────────────────────────────────
-- 20 rows — one per demographic segment
CREATE TABLE dim_demographic (
    segment_id INT PRIMARY KEY,
    segment VARCHAR(100) NOT NULL,
    category VARCHAR(50)  NOT NULL,   
    primary_barrier VARCHAR(100)
);
--Create Fact Tables
-- fact_mobile_transactions
-- 120 rows — monthly M-Pesa transaction data 2015–2024
CREATE TABLE fact_mobile_transactions (
    txn_id INT IDENTITY(1,1) PRIMARY KEY,
    date_id INT NOT NULL
        REFERENCES dim_date(date_id),
    year INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20),
    period VARCHAR(7),
    active_agents INT,
    registered_accounts_m FLOAT,
    active_accounts_m FLOAT,
    txn_volume_m FLOAT,
    txn_value_kes_b FLOAT,
    avg_txn_size_kes INT,
    agent_cico_volume_m FLOAT,
    agent_cico_value_kes_b FLOAT
);

-- fact_county_inclusion 
-- 47 rows — county-level inclusion + agent data merged
CREATE TABLE fact_county_inclusion (
    inclusion_id INT IDENTITY(1,1) PRIMARY KEY,
    county_id INT NOT NULL
        REFERENCES dim_county(county_id),
    county_name VARCHAR(100),
    region VARCHAR(50),
    survey_year INT,
    formal_inclusion_pct  FLOAT,
    exclusion_pct FLOAT,
    mobile_money_usage_pct FLOAT,
    informal_only_pct FLOAT,
    rural_inclusion_pct FLOAT,
    urban_inclusion_pct FLOAT,
    urban_rural_gap_pct FLOAT,
    population_2024 INT,
    excluded_population INT,
    high_inclusion_flag VARCHAR(5),
    active_agents_2024 INT,
    agents_per_10k_pop FLOAT,
    agent_density_tier VARCHAR(10),
    settlement_type VARCHAR(20)
);

--fact_demographic_exclusion 
-- 20 rows — exclusion rates by demographic segment
CREATE TABLE fact_demographic_exclusion (
    demo_id INT   IDENTITY(1,1) PRIMARY KEY,
    segment_id INT NOT NULL
        REFERENCES dim_demographic(segment_id),
    segment VARCHAR(100),
    category VARCHAR(50),
    survey_year INT,
    formal_inclusion_pct FLOAT,
    excluded_pct FLOAT,
    mobile_money_pct FLOAT,
    bank_account_pct FLOAT,
    sacco_pct FLOAT,
    est_population_m FLOAT,
    excluded_count_m FLOAT,
    relative_exclusion_idx FLOAT,
    primary_barrier VARCHAR(100),
    data_source VARCHAR(100)
);

--fact_annual_kpis 
-- 10 rows — one per year, national-level KPIs
CREATE TABLE fact_annual_kpis (
    kpi_id INT IDENTITY(1,1) PRIMARY KEY,
    year INT NOT NULL,
    total_txn_value_kes_b INT,
    yoy_value_growth_pct FLOAT,
    total_txn_volume_m INT,
    yoy_volume_growth_pct FLOAT,
    active_agents INT,
    registered_accounts_m FLOAT,
    active_accounts_m INT,
    formal_inclusion_pct FLOAT,
    gdp_kes_t FLOAT,
    mobile_money_gdp_pct FLOAT
);

--fact_finaccess_trends
-- 7 rows — FinAccess survey waves 2006–2024
CREATE TABLE fact_finaccess_trends (
    finaccess_id INT   IDENTITY(1,1) PRIMARY KEY,
    survey_year INT NOT NULL,
    formal_access_pct FLOAT,
    formal_access_overall_pct FLOAT,
    informal_only_pct FLOAT,
    mobile_money_pct FLOAT,
    excluded_pct FLOAT,
    banked_pct FLOAT,
    sacco_pct FLOAT,
    mfi_pct FLOAT,
    insurance_pct FLOAT,
    context_note VARCHAR(200),
    inclusion_change_pp FLOAT, 
    excluded_change_pp FLOAT
);

SELECT
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

