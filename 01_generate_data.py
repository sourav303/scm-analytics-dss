"""
SCM Analytics DSS - Data Generator
====================================
Generates synthetic but realistic operational data based on the research paper:
"Analytics-Based Decision Support System for Supply Chain Management Function"
Innovel Energy Solutions Pvt. Ltd. | University of Calcutta MBA Research, 2024-2026

Data is modelled to reflect actual KPIs reported in the paper:
  - 95% on-time material availability
  - 36% cost optimisation vs initial estimates
  - 50 purchase orders across 5 projects
  - 15-20 vendor quotations per category
  - 96.8% inventory accuracy
  - 94% three-way match success rate

Author  : Sourav Dikshit
Program : MBA (Operations Research & System Analytics), University of Calcutta
"""

import random
import sqlite3
import os
from datetime import date, timedelta

# ── Reproducibility ──────────────────────────────────────────────────────────
random.seed(42)

# ── Output path ──────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "scm_dss.db")

# ═══════════════════════════════════════════════════════════════════════════
# REFERENCE DATA  (grounded in the paper)
# ═══════════════════════════════════════════════════════════════════════════

PROJECTS = [
    {"project_id": "PRJ001", "name": "Solar Farm – Bankura",      "state": "West Bengal",   "capacity_kw": 500},
    {"project_id": "PRJ002", "name": "Grid Infra – Purulia",      "state": "West Bengal",   "capacity_kw": 0},
    {"project_id": "PRJ003", "name": "Solar Rooftop – Siliguri",  "state": "West Bengal",   "capacity_kw": 150},
    {"project_id": "PRJ004", "name": "Solar Farm – Jharkhand",    "state": "Jharkhand",     "capacity_kw": 300},
    {"project_id": "PRJ005", "name": "Civil Works – Odisha",      "state": "Odisha",        "capacity_kw": 0},
]

# Material categories with lead-time range and on-time % from Table 8.1
MATERIAL_CATEGORIES = [
    {"cat_id": "CAT01", "name": "Solar PV Modules",             "unit": "piece",  "lead_min": 18, "lead_max": 25, "on_time_pct": 0.97},
    {"cat_id": "CAT02", "name": "Mounting Structures (Al)",     "unit": "MT",     "lead_min": 12, "lead_max": 18, "on_time_pct": 0.95},
    {"cat_id": "CAT03", "name": "Inverters / PCUs",             "unit": "piece",  "lead_min": 20, "lead_max": 30, "on_time_pct": 0.93},
    {"cat_id": "CAT04", "name": "HT/LT Cables",                 "unit": "meter",  "lead_min":  8, "lead_max": 14, "on_time_pct": 0.96},
    {"cat_id": "CAT05", "name": "Civil Materials",              "unit": "MT",     "lead_min":  5, "lead_max": 10, "on_time_pct": 0.98},
    {"cat_id": "CAT06", "name": "Switchgear / Protection Equip","unit": "piece",  "lead_min": 22, "lead_max": 35, "on_time_pct": 0.90},
    {"cat_id": "CAT07", "name": "Earthing Materials",           "unit": "piece",  "lead_min":  6, "lead_max": 10, "on_time_pct": 0.99},
]

# Vendors – 3-5 per category as stated in paper
VENDORS = [
    # Solar PV Modules
    {"vendor_id": "VND01", "name": "Vikram Solar Ltd",        "cat_id": "CAT01", "city": "Kolkata",    "gstin": "19AABCV1234A1Z5", "certified": True},
    {"vendor_id": "VND02", "name": "Waaree Energies Ltd",     "cat_id": "CAT01", "city": "Mumbai",     "gstin": "27AABCW5678B2Z1", "certified": True},
    {"vendor_id": "VND03", "name": "Adani Solar",             "cat_id": "CAT01", "city": "Ahmedabad",  "gstin": "24AABCA9012C3Z8", "certified": True},
    {"vendor_id": "VND04", "name": "Renewsys India",          "cat_id": "CAT01", "city": "Hyderabad",  "gstin": "36AABCR3456D4Z2", "certified": True},
    # Mounting Structures
    {"vendor_id": "VND05", "name": "Arctech Solar India",     "cat_id": "CAT02", "city": "Pune",       "gstin": "27AABCA7890E5Z9", "certified": True},
    {"vendor_id": "VND06", "name": "K2 Systems India",        "cat_id": "CAT02", "city": "Bangalore",  "gstin": "29AABCK2345F6Z3", "certified": True},
    {"vendor_id": "VND07", "name": "Hollaender India",        "cat_id": "CAT02", "city": "Delhi",      "gstin": "07AABCH6789G7Z6", "certified": False},
    # Inverters
    {"vendor_id": "VND08", "name": "SMA Solar Technology",   "cat_id": "CAT03", "city": "Kolkata",    "gstin": "19AABCS1122H8Z4", "certified": True},
    {"vendor_id": "VND09", "name": "Sungrow India",           "cat_id": "CAT03", "city": "Gurugram",   "gstin": "06AABCS3344I9Z7", "certified": True},
    {"vendor_id": "VND10", "name": "ABB Power Grids India",  "cat_id": "CAT03", "city": "Vadodara",   "gstin": "24AABCA5566J0Z1", "certified": True},
    # HT/LT Cables
    {"vendor_id": "VND11", "name": "Polycab India Ltd",      "cat_id": "CAT04", "city": "Halol",      "gstin": "24AABCP7788K1Z5", "certified": True},
    {"vendor_id": "VND12", "name": "KEI Industries",          "cat_id": "CAT04", "city": "Delhi",      "gstin": "07AABCK9900L2Z8", "certified": True},
    {"vendor_id": "VND13", "name": "Havells India Ltd",       "cat_id": "CAT04", "city": "Noida",      "gstin": "09AABCH1122M3Z2", "certified": True},
    # Civil Materials
    {"vendor_id": "VND14", "name": "UltraTech Cement Ltd",   "cat_id": "CAT05", "city": "Mumbai",     "gstin": "27AABCU3344N4Z6", "certified": True},
    {"vendor_id": "VND15", "name": "SAIL (Steel Auth India)","cat_id": "CAT05", "city": "Kolkata",    "gstin": "19AABCS5566O5Z9", "certified": True},
    {"vendor_id": "VND16", "name": "ACC Cement Ltd",          "cat_id": "CAT05", "city": "Kolkata",    "gstin": "19AABCA7788P6Z3", "certified": True},
    # Switchgear
    {"vendor_id": "VND17", "name": "Schneider Electric India","cat_id": "CAT06", "city": "Bangalore",  "gstin": "29AABCS9900Q7Z7", "certified": True},
    {"vendor_id": "VND18", "name": "Siemens India Ltd",       "cat_id": "CAT06", "city": "Mumbai",     "gstin": "27AABCS1234R8Z0", "certified": True},
    {"vendor_id": "VND19", "name": "L&T Electrical Ltd",      "cat_id": "CAT06", "city": "Mumbai",     "gstin": "27AABCL5678S9Z4", "certified": True},
    # Earthing
    {"vendor_id": "VND20", "name": "Apar Industries Ltd",     "cat_id": "CAT07", "city": "Silvassa",   "gstin": "26AABCA9012T0Z8", "certified": True},
    {"vendor_id": "VND21", "name": "Galvin Electric India",   "cat_id": "CAT07", "city": "Chennai",    "gstin": "33AABCG3456U1Z1", "certified": False},
    {"vendor_id": "VND22", "name": "Ravin Cables Ltd",        "cat_id": "CAT07", "city": "Mumbai",     "gstin": "27AABCR7890V2Z5", "certified": True},
]

# Price benchmarks from Table 8.2.1 (paper)
PRICE_BENCHMARKS = {
    "CAT01": {"high": 22500, "low": 17800, "selected": 18200, "unit": "INR/piece"},
    "CAT02": {"high": 78000, "low": 58500, "selected": 61000, "unit": "INR/MT"},
    "CAT03": {"high": 485000,"low": 392000,"selected": 405000,"unit": "INR/piece"},
    "CAT04": {"high": 485,   "low": 320,   "selected": 340,   "unit": "INR/meter"},
    "CAT05": {"high": 8500,  "low": 5800,  "selected": 6200,  "unit": "INR/MT"},
    "CAT06": {"high": 185000,"low": 120000,"selected": 128000,"unit": "INR/piece"},
    "CAT07": {"high": 1850,  "low": 1200,  "selected": 1280,  "unit": "INR/piece"},
}

# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def fmt(d: date) -> str:
    return d.strftime("%Y-%m-%d")

# ═══════════════════════════════════════════════════════════════════════════
# GENERATE PURCHASE ORDERS  (50 POs as stated in the paper)
# ═══════════════════════════════════════════════════════════════════════════

def generate_pos(vendors, material_cats):
    pos = []
    po_num = 1000
    study_start = date(2024, 10, 1)
    study_end   = date(2025,  4, 30)

    # Map cat_id -> category info
    cat_map = {c["cat_id"]: c for c in material_cats}
    # Map cat_id -> vendors
    vendor_by_cat = {}
    for v in vendors:
        vendor_by_cat.setdefault(v["cat_id"], []).append(v)

    project_ids = [p["project_id"] for p in PROJECTS]

    target = 50
    generated = 0

    for cat in material_cats:
        # Spread POs across categories roughly proportional
        n_pos = max(2, round(target * (1 / len(material_cats))))
        if generated + n_pos > target:
            n_pos = target - generated
        if n_pos <= 0:
            break

        cat_vendors = vendor_by_cat.get(cat["cat_id"], [])
        pb = PRICE_BENCHMARKS[cat["cat_id"]]
        selected_price = pb["selected"]

        for _ in range(n_pos):
            po_num += 1
            project = random.choice(project_ids)
            vendor  = random.choice(cat_vendors)

            order_date    = rand_date(study_start, study_end - timedelta(days=35))
            promised_lead = random.randint(cat["lead_min"], cat["lead_max"])
            promised_date = order_date + timedelta(days=promised_lead)

            # 92% on-time (paper: 92% of POs had on-time delivery)
            on_time = random.random() < 0.92
            actual_days_variance = 0 if on_time else random.randint(3, 12)
            actual_date = promised_date + timedelta(days=actual_days_variance)
            if actual_date > date(2025, 5, 31):
                actual_date = date(2025, 5, 31)

            qty = random.randint(5, 200)
            unit_price = round(selected_price * random.uniform(0.95, 1.08), 2)
            total_value = round(qty * unit_price, 2)

            # 94% three-way match success (paper)
            three_way_match = "Pass" if random.random() < 0.94 else "Fail"

            # 16% POs needed amendments (paper)
            amended = random.random() < 0.16

            pos.append({
                "po_id":            f"PO{po_num}",
                "project_id":       project,
                "vendor_id":        vendor["vendor_id"],
                "cat_id":           cat["cat_id"],
                "order_date":       fmt(order_date),
                "promised_date":    fmt(promised_date),
                "actual_date":      fmt(actual_date),
                "on_time":          1 if on_time else 0,
                "quantity":         qty,
                "unit":             cat["unit"],
                "unit_price_inr":   unit_price,
                "total_value_inr":  total_value,
                "three_way_match":  three_way_match,
                "amended":          1 if amended else 0,
                "status":           "Closed" if actual_date <= date(2025, 4, 30) else "Open",
            })
            generated += 1

    return pos

# ═══════════════════════════════════════════════════════════════════════════
# GENERATE VENDOR QUOTATIONS  (15-20 per category, paper section 8.2)
# ═══════════════════════════════════════════════════════════════════════════

def generate_quotations(vendors, material_cats):
    quotes = []
    q_num  = 1
    vendor_by_cat = {}
    for v in vendors:
        vendor_by_cat.setdefault(v["cat_id"], []).append(v)

    for cat in material_cats:
        pb = PRICE_BENCHMARKS[cat["cat_id"]]
        cat_vendors = vendor_by_cat.get(cat["cat_id"], [])
        # Generate 3-5 quotes per vendor to reach 15-20 total
        for vendor in cat_vendors:
            n_quotes = random.randint(3, 5)
            for _ in range(n_quotes):
                # Price spread: low to high (paper shows ~25% spread)
                quoted_price = round(random.uniform(pb["low"] * 0.98, pb["high"] * 1.02), 2)
                delivery_days = random.randint(cat["lead_min"] - 2, cat["lead_max"] + 5)
                payment_terms = random.choice(["30 days", "45 days", "60 days", "Advance 30%"])
                quality_score = round(random.uniform(6.0, 10.0), 1)  # out of 10
                gst_compliant = 1 if vendor["certified"] else random.choice([0, 1])

                avg_price = (pb["high"] + pb["low"]) / 2
                saving_vs_avg = round((avg_price - quoted_price) / avg_price * 100, 2)

                quotes.append({
                    "quote_id":        f"QT{q_num:04d}",
                    "cat_id":          cat["cat_id"],
                    "vendor_id":       vendor["vendor_id"],
                    "quoted_price_inr":quoted_price,
                    "delivery_days":   delivery_days,
                    "payment_terms":   payment_terms,
                    "quality_score":   quality_score,
                    "gst_compliant":   gst_compliant,
                    "saving_vs_avg_pct": saving_vs_avg,
                    "selected":        1 if quoted_price <= pb["selected"] * 1.02 and gst_compliant else 0,
                })
                q_num += 1

    return quotes

# ═══════════════════════════════════════════════════════════════════════════
# GENERATE INVENTORY RECORDS
# ═══════════════════════════════════════════════════════════════════════════

def generate_inventory(pos, material_cats):
    cat_map = {c["cat_id"]: c for c in material_cats}
    inventory = []
    inv_num = 1

    for po in pos:
        if po["status"] == "Closed":
            cat = cat_map[po["cat_id"]]
            received_qty = po["quantity"]
            # 96.8% inventory accuracy (paper)
            system_qty = received_qty if random.random() < 0.968 else received_qty + random.choice([-1, 1, 2])
            issued_qty = round(received_qty * random.uniform(0.6, 1.0))
            balance_qty = system_qty - issued_qty

            # Days of Cover (DoC)
            avg_daily_usage = max(1, round(issued_qty / 30))
            doc = round(balance_qty / avg_daily_usage) if avg_daily_usage > 0 else 0

            inventory.append({
                "inv_id":         f"INV{inv_num:04d}",
                "po_id":          po["po_id"],
                "cat_id":         po["cat_id"],
                "project_id":     po["project_id"],
                "grn_date":       po["actual_date"],
                "received_qty":   received_qty,
                "system_qty":     system_qty,
                "issued_qty":     issued_qty,
                "balance_qty":    max(0, balance_qty),
                "unit":           po["unit"],
                "days_of_cover":  max(0, doc),
                "accuracy_flag":  1 if received_qty == system_qty else 0,
                "replenish_alert":1 if doc < 7 else 0,
            })
            inv_num += 1

    return inventory

# ═══════════════════════════════════════════════════════════════════════════
# GENERATE VENDOR SCORECARD  (Tableau vendor performance dashboard)
# ═══════════════════════════════════════════════════════════════════════════

def generate_vendor_scorecards(vendors, pos):
    scorecards = []
    for vendor in vendors:
        vendor_pos = [p for p in pos if p["vendor_id"] == vendor["vendor_id"]]
        if not vendor_pos:
            # Vendor exists but no PO – assign average-ish scores
            delivery_score  = round(random.uniform(6.5, 9.5), 1)
            price_score     = round(random.uniform(6.0, 9.5), 1)
            quality_score   = round(random.uniform(7.0, 9.5), 1)
            response_score  = round(random.uniform(6.0, 9.0), 1)
            total_pos       = 0
            on_time_rate    = round(random.uniform(0.80, 0.99), 3)
        else:
            on_time_count = sum(p["on_time"] for p in vendor_pos)
            on_time_rate  = round(on_time_count / len(vendor_pos), 3)
            total_pos     = len(vendor_pos)

            delivery_score = round(on_time_rate * 10, 1)
            price_score    = round(random.uniform(6.5, 9.5), 1)
            quality_score  = round(random.uniform(7.0, 9.8), 1)
            response_score = round(random.uniform(6.0, 9.5), 1)

        # Weighted composite (weights from paper Table 8.2)
        # Price 30%, Delivery 25%, Quality 20%, Payment 10%, Past Perf 10%, GST 5%
        gst_score = 10.0 if vendor["certified"] else 5.0
        composite = round(
            price_score    * 0.30 +
            delivery_score * 0.25 +
            quality_score  * 0.20 +
            response_score * 0.10 +
            delivery_score * 0.10 +
            gst_score      * 0.05,
            2
        )
        status = "Preferred" if composite >= 8.0 else ("Approved" if composite >= 6.5 else "Under Review")

        scorecards.append({
            "vendor_id":       vendor["vendor_id"],
            "vendor_name":     vendor["name"],
            "cat_id":          vendor["cat_id"],
            "city":            vendor["city"],
            "gstin_verified":  1 if vendor["certified"] else 0,
            "total_pos":       total_pos,
            "on_time_rate":    on_time_rate,
            "delivery_score":  delivery_score,
            "price_score":     price_score,
            "quality_score":   quality_score,
            "responsiveness":  response_score,
            "composite_score": composite,
            "status":          status,
        })

    return scorecards

# ═══════════════════════════════════════════════════════════════════════════
# WRITE TO SQLITE DATABASE
# ═══════════════════════════════════════════════════════════════════════════

def create_database(db_path, projects, material_cats, vendors, pos, quotes, inventory, scorecards):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    cur.executescript("""
    CREATE TABLE projects (
        project_id   TEXT PRIMARY KEY,
        name         TEXT,
        state        TEXT,
        capacity_kw  INTEGER
    );

    CREATE TABLE material_categories (
        cat_id       TEXT PRIMARY KEY,
        name         TEXT,
        unit         TEXT,
        lead_min     INTEGER,
        lead_max     INTEGER,
        on_time_pct  REAL
    );

    CREATE TABLE vendors (
        vendor_id    TEXT PRIMARY KEY,
        name         TEXT,
        cat_id       TEXT,
        city         TEXT,
        gstin        TEXT,
        certified    INTEGER,
        FOREIGN KEY (cat_id) REFERENCES material_categories(cat_id)
    );

    CREATE TABLE purchase_orders (
        po_id            TEXT PRIMARY KEY,
        project_id       TEXT,
        vendor_id        TEXT,
        cat_id           TEXT,
        order_date       TEXT,
        promised_date    TEXT,
        actual_date      TEXT,
        on_time          INTEGER,
        quantity         INTEGER,
        unit             TEXT,
        unit_price_inr   REAL,
        total_value_inr  REAL,
        three_way_match  TEXT,
        amended          INTEGER,
        status           TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(project_id),
        FOREIGN KEY (vendor_id)  REFERENCES vendors(vendor_id),
        FOREIGN KEY (cat_id)     REFERENCES material_categories(cat_id)
    );

    CREATE TABLE vendor_quotations (
        quote_id           TEXT PRIMARY KEY,
        cat_id             TEXT,
        vendor_id          TEXT,
        quoted_price_inr   REAL,
        delivery_days      INTEGER,
        payment_terms      TEXT,
        quality_score      REAL,
        gst_compliant      INTEGER,
        saving_vs_avg_pct  REAL,
        selected           INTEGER,
        FOREIGN KEY (cat_id)    REFERENCES material_categories(cat_id),
        FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
    );

    CREATE TABLE inventory (
        inv_id          TEXT PRIMARY KEY,
        po_id           TEXT,
        cat_id          TEXT,
        project_id      TEXT,
        grn_date        TEXT,
        received_qty    INTEGER,
        system_qty      INTEGER,
        issued_qty      INTEGER,
        balance_qty     INTEGER,
        unit            TEXT,
        days_of_cover   INTEGER,
        accuracy_flag   INTEGER,
        replenish_alert INTEGER,
        FOREIGN KEY (po_id)       REFERENCES purchase_orders(po_id),
        FOREIGN KEY (cat_id)      REFERENCES material_categories(cat_id),
        FOREIGN KEY (project_id)  REFERENCES projects(project_id)
    );

    CREATE TABLE vendor_scorecards (
        vendor_id        TEXT PRIMARY KEY,
        vendor_name      TEXT,
        cat_id           TEXT,
        city             TEXT,
        gstin_verified   INTEGER,
        total_pos        INTEGER,
        on_time_rate     REAL,
        delivery_score   REAL,
        price_score      REAL,
        quality_score    REAL,
        responsiveness   REAL,
        composite_score  REAL,
        status           TEXT,
        FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
    );
    """)

    cur.executemany("INSERT INTO projects VALUES (:project_id,:name,:state,:capacity_kw)", projects)
    cur.executemany("INSERT INTO material_categories VALUES (:cat_id,:name,:unit,:lead_min,:lead_max,:on_time_pct)", material_cats)
    cur.executemany("INSERT INTO vendors VALUES (:vendor_id,:name,:cat_id,:city,:gstin,:certified)", vendors)
    cur.executemany("INSERT INTO purchase_orders VALUES (:po_id,:project_id,:vendor_id,:cat_id,:order_date,:promised_date,:actual_date,:on_time,:quantity,:unit,:unit_price_inr,:total_value_inr,:three_way_match,:amended,:status)", pos)
    cur.executemany("INSERT INTO vendor_quotations VALUES (:quote_id,:cat_id,:vendor_id,:quoted_price_inr,:delivery_days,:payment_terms,:quality_score,:gst_compliant,:saving_vs_avg_pct,:selected)", quotes)
    cur.executemany("INSERT INTO inventory VALUES (:inv_id,:po_id,:cat_id,:project_id,:grn_date,:received_qty,:system_qty,:issued_qty,:balance_qty,:unit,:days_of_cover,:accuracy_flag,:replenish_alert)", inventory)
    cur.executemany("INSERT INTO vendor_scorecards VALUES (:vendor_id,:vendor_name,:cat_id,:city,:gstin_verified,:total_pos,:on_time_rate,:delivery_score,:price_score,:quality_score,:responsiveness,:composite_score,:status)", scorecards)

    conn.commit()
    conn.close()
    print(f"[OK] Database written → {db_path}")

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("Generating data …")
    pos         = generate_pos(VENDORS, MATERIAL_CATEGORIES)
    quotes      = generate_quotations(VENDORS, MATERIAL_CATEGORIES)
    inventory   = generate_inventory(pos, MATERIAL_CATEGORIES)
    scorecards  = generate_vendor_scorecards(VENDORS, pos)

    create_database(DB_PATH, PROJECTS, MATERIAL_CATEGORIES, VENDORS,
                    pos, quotes, inventory, scorecards)

    print(f"  Projects            : {len(PROJECTS)}")
    print(f"  Material categories : {len(MATERIAL_CATEGORIES)}")
    print(f"  Vendors             : {len(VENDORS)}")
    print(f"  Purchase Orders     : {len(pos)}")
    print(f"  Vendor Quotations   : {len(quotes)}")
    print(f"  Inventory records   : {len(inventory)}")
    print(f"  Vendor scorecards   : {len(scorecards)}")

if __name__ == "__main__":
    main()
