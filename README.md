# Affinity Solutions — DCR + ML Multi-Platform Demo

Demonstrates how Affinity Solutions' purchase-outcome data drives value across DSP (The Trade Desk), SSP (PubMatic), and Ad Server (Kargo) using Snowflake Data Clean Rooms and Snowflake ML.

## What's Inside

| Folder | Contents |
|--------|----------|
| `apps/` | 5 Streamlit in Snowflake app source files |
| `data/` | Pre-built CSV data files (compressed where >5MB) |
| `setup/` | SQL scripts and upload shell script |
| `source_info/` | Reference docs (PDFs, XLSXs) — not tracked in git |
| `DEMO_BUILD_PLAN.md` | Full technical build plan |
| `DEMO_TALK_TRACK.md` | Presenter guide with chart-by-chart narration |

## 5 Streamlit Dashboards

| # | App | Tabs | Audience |
|---|-----|------|----------|
| 1 | Pipeline End-to-End | 6 | Everyone — the full story |
| 2 | TTD Bid Explorer | 6 | TTD / DSP buyers |
| 3 | PubMatic Yield Scorer | 6 | PubMatic / SSP sellers |
| 4 | Kargo Attribution | 6 | Kargo / CTV buyers |
| 5 | Cross-Platform Comparison | 4 | Internal / exec summary |

## Prerequisites

### Snowflake Account
- **Edition:** Enterprise or Business Critical (required for Snowflake ML)
- **Role:** ACCOUNTADMIN (or a role with CREATE DATABASE, CREATE WAREHOUSE, CREATE STREAMLIT)
- **Warehouse:** Will create two warehouses (MEDIUM + LARGE)

### Local Tools
- **Snowflake CLI (`snow`)** — [Install guide](https://docs.snowflake.com/en/developer-guide/snowflake-cli/installation/installation)
- **Git** — for cloning the repo

### Snowflake CLI Connection
Configure a named connection in `~/.snowflake/connections.toml`:

```toml
[my_demo_conn]
account = "YOUR_ACCOUNT_LOCATOR"
user = "YOUR_USERNAME"
authenticator = "externalbrowser"   # or "snowflake" for password auth
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
database = "AFFINITY_DEMO"
```

Test it: `snow connection test --connection my_demo_conn`

## Setup Instructions

### Step 1: Clone the repo
```bash
git clone <repo-url>
cd DCR_Solution_demoBuild
```

### Step 2: Create Snowflake environment
Run in Snowflake (Snowsight worksheet, SnowSQL, or Snowflake CLI):
```bash
snow sql -f setup/01_environment.sql --connection my_demo_conn
```
This creates: database `AFFINITY_DEMO`, 9 schemas, 2 warehouses, file formats, and stages.

### Step 3: Upload data and app files to stages
```bash
./setup/upload_data.sh my_demo_conn
```
This uploads all CSV data files and Streamlit app source files to Snowflake internal stages.

### Step 4: Load data into tables
```bash
snow sql -f setup/02_load_data.sql --connection my_demo_conn
```
This creates all tables and loads data from the staged CSV files. Verify row counts at the end.

### Step 5: Deploy Streamlit apps
```bash
snow sql -f setup/03_streamlit_apps.sql --connection my_demo_conn
```
This creates all 5 Streamlit in Snowflake apps.

### Step 6: Verify
Open Snowsight and navigate to **Streamlit** in the left sidebar. You should see 5 apps under `AFFINITY_DEMO.APPS`. Open each one to verify it loads without errors.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `COPY INTO` fails with "file not found" | Re-run `upload_data.sh` — files may not have uploaded |
| Streamlit shows "table not found" | Ensure `02_load_data.sql` completed successfully |
| Charts show "xOffset" error | SiS runs Altair v4 — all apps are already compatible |
| `hide_index` error | SiS uses older Streamlit — all apps are already compatible |
| Warehouse suspended | Warehouses auto-resume; retry the query |

## Architecture

```
AFFINITY_DEMO (Database)
├── AFS_PROVIDER      — Affinity purchase data + predictions
├── TTD_CONSUMER      — TTD impression data + demo outputs
├── PUBMATIC_CONSUMER — PubMatic OpenRTB data + demo outputs
├── KARGO_CONSUMER    — Kargo LLD data + demo outputs
├── CLEANROOM         — Match crosswalks + rate summaries
├── ML                — ML validation, rules, delivery tables
├── AI                — Quadrant strategy
├── APPS              — Streamlit apps + stages
└── UTIL              — Enum/reference tables
```

## Security Notes
- No credentials, tokens, or connection strings are stored in this repo
- All data is synthetic (generated, not real customer data)