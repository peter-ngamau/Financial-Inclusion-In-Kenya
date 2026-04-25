# Kenya Financial Inclusion & Mobile Money Analytics

> An end-to-end data analytics project exploring M-Pesa adoption, financial inclusion trends, and unbanked population segments across Kenya's 47 counties — built using **Python · SQL Server · Power BI**.

---

##  Project Overview

Kenya is one of the world's most remarkable mobile money success stories. Since M-Pesa launched in 2007, the country has gone from 67.5% of its population being financially excluded to just 9.9% today. Yet millions of Kenyans — particularly in rural counties, older age groups, and lower income segments — still lack access to formal financial services.

This project analyses **10 years of CBK (Central Bank of Kenya) mobile money data** and **7 waves of the FinAccess Household Survey (2006–2024)** to answer four core questions:

1. How has M-Pesa transaction value and adoption grown from 2015 to 2024?
2. Which counties are the most and least financially included — and why?
3. Which demographic groups (by age, gender, income, education) are most at risk of exclusion?
4. Is there a measurable relationship between agent network density and financial inclusion?

---

##  Key Findings

- **M-Pesa transaction value grew 7× in 10 years** — from KES 1,238 Billion in 2015 to KES 8,700 Billion in 2024
- **Mobile money now represents 57.6% of Kenya's GDP** — among the highest ratios in the world
- **Tana River County has the highest exclusion rate at 37.6%** — compared to Nyandarua at just 2.6%
- **People with no formal education are 4.6× more likely to be excluded** than the national average
- **Agent density and inclusion are positively correlated (r = 0.55)** — counties with more agents per 1,000 people consistently show higher inclusion rates
- **The 2020 COVID-19 pandemic accelerated digital adoption by 41% in a single year** — the largest single-year jump in the dataset

---

## 🗂️ Project Structure

```
Financial_Inclusion_Kenya/
│
├── Data/
│   ├── Raw/                          # Original .xlsx files from CBK & FinAccess
│   └── Clean/                        # 6 analysis-ready CSV files
│       ├── c_Mobile_Money_Monthly_Transactions_2015_2024.csv
│       ├── c_County_Financial_Inclusion_2024.csv
│       ├── c_FinAccess_Historical_Survey_2006_2024.csv
│       ├── c_Agent_Network_by_County.csv
│       ├── c_Demographic_Exclusion_Analysis.csv
│       └── c_Annual_KPIs_Summary.csv
│
├── Scripts/
│   ├── 01_clean.py                   # Data cleaning pipeline
│   ├── 02_eda.py                     # Exploratory data analysis + 11 charts
│   ├── 03_load_sql.py                # Load data into SQL Server
│   └── fix_failed_tables.py          # Targeted SQL load fix script
│
├── Charts/                           # 11 EDA charts exported as PNG
│
├── SQL/
│   └── create_tables.sql             # All CREATE TABLE statements (star schema)
│
├── Dashboard/
│   └── Financial_Inclusion_Ke_Dashboard.pbix   # Power BI report
│
└── README.md
```

---

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| **Python (pandas, matplotlib, seaborn, scipy)** | Data cleaning, EDA, and SQL loading |
| **SQL Server + SSMS** | Data warehouse — star schema with 4 dim tables and 5 fact tables |
| **Power BI Desktop** | Interactive 4-page dashboard |
| **CBK Open Data** | Primary data source — mobile money statistics |
| **FinAccess Household Survey** | Financial inclusion survey data (2006–2024) |

---

## The 6 Datasets

| File | Rows | What it contains |
|------|------|-----------------|
| Monthly transactions | 120 | M-Pesa transaction volume, value, agents and accounts — every month 2015–2024 |
| County inclusion | 47 | Formal inclusion rate, exclusion rate, mobile money usage and agent density for all 47 counties |
| FinAccess historical | 7 | National inclusion figures from each of the 7 survey waves between 2006 and 2024 |
| Agent network | 47 | Active agent counts and density per 1,000 population for every county |
| Demographic exclusion | 20 | Exclusion rates broken down by gender, age group, location, income quintile, education level and disability |
| Annual KPIs | 10 | One row per year summarising national transaction totals, account registrations and GDP share |

---

## How the Project Was Built

### Phase 1 — Data Cleaning (Python)

The raw data came from CBK annual reports and FinAccess survey publications as Excel files. The cleaning script (`01_clean.py`) does the following for each file:

- Standardises all column names to lowercase with underscores (no spaces or special characters)
- Validates that all 47 counties are present and correctly spelled
- Checks that percentage columns are in the 0–1 decimal range, not 0–100
- Removes duplicate rows
- Adds derived columns such as `period` (YYYY-MM), `quarter`, `exclusion_tier`, and `urban_rural_gap_pct`
- Adds a `relative_exclusion_index` to the demographics file — showing how many times worse each demographic segment is compared to the national average
- Outputs a cleaning report to `data/clean/cleaning_report.txt` documenting every check and fix

### Phase 2 — Exploratory Data Analysis (Python)

The EDA script (`02_eda.py`) generates 8 charts answering the core project questions:

1. M-Pesa transaction value growth 2015–2024 (bar + line, dual axis)
2. Monthly transaction volume heatmap — seasonal patterns by year and month
3. Top 10 most excluded counties (horizontal bar, colour-coded by region)
4. Financial inclusion evolution 2006–2024 (stacked area across 7 survey waves)
5. Agent density vs inclusion rate by county (scatter plot)
6. Mobile money as % of GDP over time (dual-axis line)
7. County inclusion distribution by region (box)
8. Correlation matrix of county-level variables

### Phase 3 — SQL Server Data Warehouse

The clean CSV files were loaded into SQL Server using a **star schema** — a design pattern commonly used in business intelligence.

**Dimension tables** (lookup tables):
- `dim_county` — 47 rows, one per county
- `dim_date` — 120 rows, one per year-month
- `dim_demographic` — 20 rows, one per demographic segment
- `dim_region` — 8 rows, one per region

**Fact tables** (the measurable data):
- `fact_mobile_transactions` — monthly M-Pesa data
- `fact_county_inclusion` — county-level inclusion metrics
- `fact_demographic_exclusion` — segment-level exclusion data
- `fact_annual_kpis` — national annual KPIs
- `fact_finaccess_trends` — historical survey wave data

The Python script (`03_load_sql.py`) connects to SQL Server using SQLAlchemy and pyodbc, builds the tables as DataFrames, and loads them with `df.to_sql()`. A final verification step runs a `SELECT COUNT(*)` on every table to confirm row counts match.

### Phase 4 — Power BI Dashboard

The Power BI report connects directly to SQL Server and contains 4 pages:

**Page 1 — National Overview**
Four KPI cards (total transaction value, active agents, national inclusion rate, excluded population), a bar chart showing annual transaction value growth, a line chart of registered vs active accounts, a donut chart showing included vs excluded split, and a table of the top 10 most excluded counties.

**Page 2 — County Map**
A filled map of all 47 Kenyan counties coloured by inclusion tier, a scatter plot showing agent density vs inclusion rate with region colour coding and population as bubble size, a region slicer that filters all visuals simultaneously, and a full county data table with conditional formatting on agent density tier.

**Page 3 — Transaction Trends**
A full-width monthly line chart with a year range slicer, annual transaction value bars with YoY growth line, a quarterly volume matrix showing seasonal patterns, and a clustered bar chart comparing registered vs active accounts with a utilisation rate line.

**Page 4 — Demographics**
A horizontal bar chart of exclusion rates for all 20 demographic segments with a national average reference line, a 100% stacked bar showing inclusion vs exclusion by category, a segment detail table with colour-coded relative exclusion index, and a category slicer that filters all visuals by Gender, Age, Location, Income, Education or PWD.

---

## Dashboard Preview

> *Power BI report published at:* `[add your published link here]`

| Page | Description |
|------|-------------|
| National Overview | KPIs, transaction growth, account utilisation |
| County Map | Filled map + scatter + county data table |
| Transaction Trends | Monthly line chart, quarterly matrix, year slicer |
| Demographics | Exclusion by segment, inclusion evolution |

---

## How to Reproduce This Project

### Prerequisites
```bash
pip install pandas openpyxl sqlalchemy pyodbc matplotlib seaborn scipy
```
You also need:
- SQL Server (Express edition is free) with SSMS installed
- ODBC Driver 17 for SQL Server ([download here](https://aka.ms/downloadmsodbcsql))
- Power BI Desktop (free from Microsoft)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/financial-inclusion-kenya.git
cd financial-inclusion-kenya

# 2. Run the cleaning script
#    (place your raw xlsx files in data/raw/ first)
python scripts/01_clean.py

# 3. Run EDA and generate charts
python scripts/02_eda.py

# 4. Create the SQL Server tables
#    (run SQL/create_tables.sql in SSMS first)

# 5. Load data into SQL Server
#    (update SERVER name in the script first)
python scripts/03_load_sql.py

# 6. Open the Power BI file
#    Dashboard/Financial_Inclusion_Ke_Dashboard.pbix
#    Update the SQL Server connection in Transform Data → Data source settings
```

---

## Data Sources

| Source | Data |
|--------|------|
| [Central Bank of Kenya](https://www.centralbank.go.ke) | Mobile money statistics, agent network data, annual reports |
| [FinAccess Household Survey](https://www.centralbank.go.ke/financial-inclusion/finaccess/) | Financial inclusion survey data — CBK, KNBS & FSD Kenya |
| [Kenya National Bureau of Statistics](https://www.knbs.or.ke) | County population estimates 2024 |

---

## 👤 Author

**[Peter Ngamau]**
Data Analyst | Python · SQL · Power BI

- 📧 [ptahmwangi@gmail.com]
- 💼 [[LinkedIn profile](https://www.linkedin.com/in/peter-ngamau/)]
- 🐙 [[GitHub profile](https://github.com/peter-ngamau)]

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

