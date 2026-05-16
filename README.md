# SCM Analytics DSS — Supply Chain Decision Support System

**Analytics-Based Decision Support System for Supply Chain Management**  
*Based on MBA Research: University of Calcutta | Department of Business Management, Alipore Campus*  
*Industry Partner: Innovel Energy Solutions Pvt. Ltd., Kolkata*  
*Author: Sourav Dikshit | CU Roll No: 95/MBA/240010 | Academic Year: 2024–2026*

---

## What This Project Is

This project operationalises the research paper *"Analytics-Based Decision Support System for SCM Function"* into a working, end-to-end data pipeline using **Python**, **SQL (SQLite)**, and **Tableau-ready CSV exports**.

It demonstrates how analytics transforms raw supply chain data into actionable decisions — covering procurement planning, vendor evaluation, inventory control, and real-time dashboard visibility — based on a real-world case study at a renewable energy company in Kolkata.

---

## Key Results (from the Research Paper)

| KPI | Target | Achieved |
|-----|--------|----------|
| On-Time Material Availability | 90% | **95%** |
| Procurement Cost Optimisation | 20% | **36%** |
| Purchase Orders Processed | 40 | **50** |
| Inventory Accuracy (SAP vs Physical) | 92% | **96.8%** |
| Three-Way Match Success Rate | 90% | **94%** |
| Stock-Out Incidents | < 5 | **3** |
| Vendor Dashboard Coverage | 80% | **100%** |

---

## Project Structure

```
scm_dss_project/
│
├── python/
│   ├── 01_generate_data.py        # Generates all synthetic SCM data → SQLite DB
│   ├── 02_analytics.py            # Runs all KPI analysis + saves 7 charts (PNG)
│   └── 03_export_for_tableau.py   # Exports 6 analysis-ready CSVs for Tableau
│
├── sql/
│   └── analysis.sql               # 20+ analytical SQL queries (6 sections)
│
├── data/
│   └── scm_dss.db                 # SQLite database (auto-generated)
│
├── tableau_exports/
│   ├── 01_procurement_status.csv
│   ├── 02_vendor_performance.csv
│   ├── 03_inventory_flow.csv
│   ├── 04_price_benchmarking.csv
│   ├── 05_kpi_summary.csv
│   ├── 06_monthly_trend.csv
│   └── charts/                    # 7 matplotlib charts (auto-generated)
│       ├── 01_on_time_by_category.png
│       ├── 02_monthly_po_activity.png
│       ├── 03_cost_saving_by_category.png
│       ├── 04_po_kpi_dashboard.png
│       ├── 05_inventory_accuracy.png
│       ├── 06_vendor_composite_scores.png
│       └── 07_executive_kpi_summary.png
│
└── README.md
```

---

## Database Schema

Six relational tables — all grounded in real operational data from the paper:

```
projects              → 5 renewable energy projects (West Bengal, Jharkhand, Odisha)
material_categories   → 7 categories (Solar PV, Inverters, Cables, Civil, etc.)
vendors               → 22 vendors across all categories
purchase_orders       → 49 POs across all projects (study period Oct 2024–Apr 2025)
vendor_quotations     → 82 quotation records (price benchmarking)
inventory             → 49 GRN records with stock levels and DoC
vendor_scorecards     → Weighted multi-criteria scores for all 22 vendors
```

**Entity Relationship:**
```
projects ──< purchase_orders >── vendors
                   │
          material_categories
                   │
              inventory
                   │
          vendor_quotations
                   │
          vendor_scorecards
```

---

## How to Run

### Prerequisites
```bash
pip install matplotlib
# Python standard library only (sqlite3, csv, os, random) — no other dependencies
```

### Step 1 — Generate the Database
```bash
python python/01_generate_data.py
```
Creates `data/scm_dss.db` with all 6 tables populated.

### Step 2 — Run Analytics & Generate Charts
```bash
python python/02_analytics.py
```
Prints KPI analysis to terminal and saves 7 PNG charts to `tableau_exports/charts/`.

### Step 3 — Export CSVs for Tableau
```bash
python python/03_export_for_tableau.py
```
Saves 6 CSV files to `tableau_exports/` ready to load into Tableau Public or Tableau Desktop.

### Step 4 — Run SQL Queries Directly (optional)
```bash
sqlite3 data/scm_dss.db < sql/analysis.sql
```
Or open `data/scm_dss.db` in any SQLite browser (e.g. DB Browser for SQLite).

---

## SQL Analytics Coverage

The `sql/analysis.sql` file contains 20+ queries organised in 6 sections:

| Section | What It Answers |
|---------|----------------|
| **1. Procurement Planning** | On-time rate overall, by category, by project; monthly PO trend |
| **2. Vendor Benchmarking** | Price spread (high/low/selected), saving vs avg, vendor selection rate |
| **3. PO Management** | Three-way match rate, amendment rate, high-value POs, open vs closed |
| **4. Inventory Analytics** | Accuracy rate, Days of Cover, replenishment alerts, project-wise flow |
| **5. Vendor Scorecard** | Composite scores, preferred/approved/under-review classification |
| **6. Executive Summary** | All KPIs in one view vs target vs paper benchmark |

---

## Tableau Dashboards (Baby Steps)

### Install Tableau Public (Free)
1. Go to: https://public.tableau.com/app/discover
2. Click **"Download Tableau Public"** → install
3. Sign up for a free account

### Connect Your Data
1. Open Tableau Public
2. On the start screen → **Connect → Text File**
3. Navigate to your `tableau_exports/` folder
4. Select `01_procurement_status.csv` → click Open

### Build Dashboard 1 — Procurement Status
| Step | Action |
|------|--------|
| 1 | Drag `Material Category` to **Columns** |
| 2 | Drag `On Time` to **Rows** → change aggregation to **AVG** → multiply by 100 for % |
| 3 | Drag `Delivery Status` to **Color** |
| 4 | Click **Show Me** → select **Bar Chart** |
| 5 | Add a second sheet: drag `Order Date` to Columns, `Delay Days` to Rows |
| 6 | Create a Dashboard → drag both sheets in |

### Build Dashboard 2 — Vendor Performance
1. Connect `02_vendor_performance.csv`
2. Horizontal bar: `Vendor Name` → Rows, `Composite Score` → Columns
3. Colour by `Status` (Preferred = green, Approved = blue, Under Review = red)
4. Add reference lines at 8.0 (Preferred) and 6.5 (Approved)
5. Add scatter sheet: `Price Score` vs `Delivery Score`, size = `Total Spend Lakhs`

### Build Dashboard 3 — Inventory Flow
1. Connect `03_inventory_flow.csv`
2. Stacked bar: `Project Name` → Columns; `Received Qty`, `Issued Qty`, `Balance Qty` → Rows
3. Colour-code `Stock Health` (Critical = red, Low = orange, Adequate = green, Surplus = blue)
4. Add filter: `Replenish Status = Replenish Now` for alert view

### Build Dashboard 4 — Price Benchmarking
1. Connect `04_price_benchmarking.csv`
2. Box plot: `Material Category` → Columns, `Quoted Price INR` → Rows
3. Colour by `Selection Status`
4. Add reference line = `Avg Price For Category`

### Build Dashboard 5 — Executive KPIs
1. Connect `05_kpi_summary.csv`
2. Bullet chart: `KPI Name` → Rows, `Achieved` → Columns, `Target` as reference line
3. Colour by `Status` (Exceeded = green, Met = blue, Missed = red)

---

## Python Charts Generated

| Chart | Description |
|-------|-------------|
| `01_on_time_by_category.png` | On-time delivery % vs paper target per material category |
| `02_monthly_po_activity.png` | Monthly PO count and value (Oct 2024–Apr 2025) |
| `03_cost_saving_by_category.png` | % saving vs average market quote per category |
| `04_po_kpi_dashboard.png` | On-time %, Three-way match %, Amended % vs targets |
| `05_inventory_accuracy.png` | Inventory accuracy % and replenishment alerts per category |
| `06_vendor_composite_scores.png` | All 22 vendors ranked by composite scorecard |
| `07_executive_kpi_summary.png` | All KPIs: target vs achieved side-by-side |

---

## Skills Demonstrated

| Skill | Where Used |
|-------|-----------|
| **Python** | Data generation, analytics engine, chart production, CSV export |
| **SQL (SQLite)** | Relational schema design, 20+ analytical queries, window functions, UNION |
| **Data Modelling** | 6-table normalised relational database from a real business case |
| **Analytics** | Descriptive stats, trend analysis, multi-criteria scoring, benchmarking |
| **Tableau** | 5 dashboard designs with field-level connection instructions |
| **Supply Chain Domain** | Procurement planning, vendor evaluation, inventory control, KPI design |
| **Research** | Paper-to-project translation; all data grounded in real MBA research |

---

## Data Note

All data in this project is **synthetically generated** using Python's `random` module with a fixed seed (`random.seed(42)`) for reproducibility. The data is calibrated to match the KPIs, price benchmarks, lead times, and performance ratios reported in the original research paper. No commercially sensitive or confidential data from Innovel Energy Solutions is included.

---

## References

- Gorry & Scott Morton (1971) — DSS framework
- Wang et al. (2016) — Big data analytics in SCM
- Amid et al. (2011) — Fuzzy multi-objective supplier selection
- Davenport (1998) — ERP systems
- Colicchia & Strozzi (2012) — Supply chain visibility
- IEA (2024) — Renewable energy market outlook
- MNRE (2024) — India 500 GW renewable energy target
- NASSCOM (2023) — Analytics in Indian SMEs

*Full bibliography in the original research paper.*

---

*MBA Research Project | University of Calcutta | 2024–2026*
