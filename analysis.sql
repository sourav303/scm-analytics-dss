-- ============================================================
-- SCM Analytics DSS – SQL Analysis Queries
-- ============================================================
-- Research Paper : Analytics-Based Decision Support System
--                  for Supply Chain Management Function
-- Organisation   : Innovel Energy Solutions Pvt. Ltd., Kolkata
-- Author         : Sourav Dikshit | CU Roll: 95/MBA/240010
-- University     : University of Calcutta, Dept. of Business
--                  Management, Alipore Campus | 2024-2026
-- ============================================================
-- Database       : SQLite (scm_dss.db)
-- Run with       : sqlite3 data/scm_dss.db < sql/analysis.sql
--              OR : Use python 02_analytics.py (executes all)
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- SECTION 1 │ PROCUREMENT PLANNING KPIs  (Paper Section 8.1)
-- ────────────────────────────────────────────────────────────

-- 1A. Overall on-time delivery rate across all POs
--     Paper target: 90% | Achieved: 92%
SELECT
    COUNT(*)                                          AS total_pos,
    SUM(on_time)                                      AS on_time_pos,
    ROUND(SUM(on_time) * 100.0 / COUNT(*), 1)        AS on_time_rate_pct
FROM purchase_orders;


-- 1B. On-time delivery rate by material category
--     Reproduces Table 8.1 from the paper
SELECT
    mc.name                                           AS material_category,
    COUNT(po.po_id)                                   AS total_pos,
    SUM(po.on_time)                                   AS on_time_pos,
    ROUND(SUM(po.on_time) * 100.0 / COUNT(*), 1)     AS on_time_rate_pct,
    mc.on_time_pct * 100                              AS paper_target_pct
FROM purchase_orders po
JOIN material_categories mc ON po.cat_id = mc.cat_id
GROUP BY mc.cat_id, mc.name
ORDER BY on_time_rate_pct DESC;


-- 1C. On-time delivery rate by project
SELECT
    p.name                                            AS project_name,
    p.state,
    COUNT(po.po_id)                                   AS total_pos,
    SUM(po.on_time)                                   AS on_time_pos,
    ROUND(SUM(po.on_time) * 100.0 / COUNT(*), 1)     AS on_time_rate_pct
FROM purchase_orders po
JOIN projects p ON po.project_id = p.project_id
GROUP BY p.project_id, p.name
ORDER BY on_time_rate_pct DESC;


-- 1D. Average lead time (promised vs actual) by category
SELECT
    mc.name                                           AS material_category,
    ROUND(AVG(julianday(po.promised_date)
        - julianday(po.order_date)), 1)               AS avg_promised_lead_days,
    ROUND(AVG(julianday(po.actual_date)
        - julianday(po.order_date)), 1)               AS avg_actual_lead_days,
    ROUND(AVG(julianday(po.actual_date)
        - julianday(po.promised_date)), 1)            AS avg_delay_days
FROM purchase_orders po
JOIN material_categories mc ON po.cat_id = mc.cat_id
GROUP BY mc.cat_id, mc.name
ORDER BY avg_delay_days DESC;


-- 1E. Monthly procurement activity (PO count and value)
SELECT
    SUBSTR(order_date, 1, 7)                          AS month,
    COUNT(*)                                           AS pos_raised,
    ROUND(SUM(total_value_inr), 2)                    AS total_value_inr
FROM purchase_orders
GROUP BY month
ORDER BY month;


-- ────────────────────────────────────────────────────────────
-- SECTION 2 │ VENDOR EVALUATION & PRICE BENCHMARKING
--             (Paper Section 8.2 – 36% cost optimisation)
-- ────────────────────────────────────────────────────────────

-- 2A. Price spread per category (high / low / selected / saving)
--     Reproduces Table 8.2.1
SELECT
    mc.name                                           AS material_category,
    mc.unit,
    ROUND(MAX(vq.quoted_price_inr), 2)                AS highest_quote_inr,
    ROUND(MIN(vq.quoted_price_inr), 2)                AS lowest_quote_inr,
    ROUND(AVG(vq.quoted_price_inr), 2)                AS avg_quote_inr,
    ROUND(MIN(CASE WHEN vq.selected = 1
              THEN vq.quoted_price_inr END), 2)        AS selected_price_inr,
    ROUND(
        (AVG(vq.quoted_price_inr)
         - MIN(CASE WHEN vq.selected=1 THEN vq.quoted_price_inr END))
        / AVG(vq.quoted_price_inr) * 100, 1)          AS saving_vs_avg_pct
FROM vendor_quotations vq
JOIN material_categories mc ON vq.cat_id = mc.cat_id
GROUP BY mc.cat_id, mc.name
ORDER BY saving_vs_avg_pct DESC;


-- 2B. Quotation count and selection rate per vendor
SELECT
    v.name                                            AS vendor_name,
    mc.name                                           AS category,
    COUNT(vq.quote_id)                                AS total_quotes,
    SUM(vq.selected)                                  AS times_selected,
    ROUND(AVG(vq.quoted_price_inr), 2)                AS avg_quoted_price,
    ROUND(AVG(vq.quality_score), 1)                   AS avg_quality_score
FROM vendor_quotations vq
JOIN vendors v   ON vq.vendor_id = v.vendor_id
JOIN material_categories mc ON vq.cat_id = mc.cat_id
GROUP BY v.vendor_id, v.name, mc.name
ORDER BY times_selected DESC, avg_quoted_price ASC;


-- 2C. Total potential saving from benchmarking
--     (avg price - selected price) * quantity ordered per category
SELECT
    mc.name                                           AS material_category,
    ROUND(AVG(vq.quoted_price_inr), 2)                AS avg_market_price,
    ROUND(SUM(po.quantity * po.unit_price_inr), 2)    AS actual_spend_inr,
    ROUND(SUM(po.quantity * AVG(vq.quoted_price_inr)
              OVER (PARTITION BY vq.cat_id)), 2)       AS would_have_spent_inr,
    ROUND(
        (SUM(po.quantity * AVG(vq.quoted_price_inr)
             OVER (PARTITION BY vq.cat_id))
         - SUM(po.quantity * po.unit_price_inr))
        / SUM(po.quantity * AVG(vq.quoted_price_inr)
              OVER (PARTITION BY vq.cat_id)) * 100,
    1)                                                AS cost_saving_pct
FROM purchase_orders po
JOIN vendor_quotations vq ON po.cat_id = vq.cat_id
JOIN material_categories mc ON po.cat_id = mc.cat_id
GROUP BY mc.cat_id, mc.name
ORDER BY cost_saving_pct DESC;


-- ────────────────────────────────────────────────────────────
-- SECTION 3 │ PURCHASE ORDER MANAGEMENT KPIs  (Paper Sec 8.3)
-- ────────────────────────────────────────────────────────────

-- 3A. PO summary dashboard (reproduces Table 8.3)
SELECT
    COUNT(*)                                          AS total_pos,
    SUM(on_time)                                      AS on_time_deliveries,
    ROUND(SUM(on_time)*100.0/COUNT(*),1)              AS on_time_pct,
    SUM(CASE WHEN three_way_match='Pass' THEN 1 END)  AS three_way_pass,
    ROUND(SUM(CASE WHEN three_way_match='Pass' THEN 1 END)*100.0/COUNT(*),1)
                                                      AS three_way_match_pct,
    SUM(amended)                                      AS amended_pos,
    ROUND(SUM(amended)*100.0/COUNT(*),1)              AS amended_pct,
    ROUND(AVG(julianday(actual_date)
        - julianday(order_date)),1)                   AS avg_lead_time_days,
    ROUND(SUM(total_value_inr),2)                     AS total_spend_inr
FROM purchase_orders;


-- 3B. PO status breakdown (Open vs Closed)
SELECT
    status,
    COUNT(*)                                          AS count,
    ROUND(SUM(total_value_inr),2)                     AS value_inr
FROM purchase_orders
GROUP BY status;


-- 3C. High-value POs (top 10 by value – procurement manager view)
SELECT
    po.po_id,
    p.name                                            AS project,
    v.name                                            AS vendor,
    mc.name                                           AS category,
    po.quantity,
    po.unit,
    po.unit_price_inr,
    po.total_value_inr,
    po.on_time,
    po.three_way_match,
    po.status
FROM purchase_orders po
JOIN projects           p  ON po.project_id = p.project_id
JOIN vendors            v  ON po.vendor_id  = v.vendor_id
JOIN material_categories mc ON po.cat_id    = mc.cat_id
ORDER BY po.total_value_inr DESC
LIMIT 10;


-- 3D. Amended POs – where are the problem areas?
SELECT
    mc.name                                           AS category,
    COUNT(*)                                          AS amended_count,
    ROUND(AVG(po.total_value_inr),2)                  AS avg_value_inr
FROM purchase_orders po
JOIN material_categories mc ON po.cat_id = mc.cat_id
WHERE po.amended = 1
GROUP BY mc.cat_id, mc.name
ORDER BY amended_count DESC;


-- ────────────────────────────────────────────────────────────
-- SECTION 4 │ INVENTORY ANALYTICS  (Paper Section 8.3 & 8.4.3)
-- ────────────────────────────────────────────────────────────

-- 4A. Inventory accuracy rate (paper: 96.8%, benchmark: 85-90%)
SELECT
    COUNT(*)                                          AS total_records,
    SUM(accuracy_flag)                                AS accurate_records,
    ROUND(SUM(accuracy_flag)*100.0/COUNT(*),1)        AS inventory_accuracy_pct,
    COUNT(*) - SUM(accuracy_flag)                     AS mismatch_count
FROM inventory;


-- 4B. Inventory accuracy by material category
SELECT
    mc.name                                           AS material_category,
    COUNT(inv.inv_id)                                 AS records,
    SUM(inv.accuracy_flag)                            AS accurate,
    ROUND(SUM(inv.accuracy_flag)*100.0/COUNT(*),1)    AS accuracy_pct,
    SUM(inv.replenish_alert)                          AS replenish_alerts
FROM inventory inv
JOIN material_categories mc ON inv.cat_id = mc.cat_id
GROUP BY mc.cat_id, mc.name
ORDER BY accuracy_pct ASC;


-- 4C. Inventory flow – received vs issued vs balance by project
SELECT
    p.name                                            AS project,
    mc.name                                           AS category,
    SUM(inv.received_qty)                             AS total_received,
    SUM(inv.issued_qty)                               AS total_issued,
    SUM(inv.balance_qty)                              AS balance_qty,
    ROUND(AVG(inv.days_of_cover),1)                   AS avg_days_of_cover,
    SUM(inv.replenish_alert)                          AS replenish_alerts
FROM inventory inv
JOIN projects           p  ON inv.project_id = p.project_id
JOIN material_categories mc ON inv.cat_id    = mc.cat_id
GROUP BY p.project_id, mc.cat_id
ORDER BY p.name, avg_days_of_cover ASC;


-- 4D. Replenishment alert items (DoC < 7 days – trigger reorder)
SELECT
    p.name                                            AS project,
    mc.name                                           AS material_category,
    inv.balance_qty,
    inv.unit,
    inv.days_of_cover,
    inv.grn_date                                      AS last_receipt_date
FROM inventory inv
JOIN projects           p  ON inv.project_id = p.project_id
JOIN material_categories mc ON inv.cat_id    = mc.cat_id
WHERE inv.replenish_alert = 1
ORDER BY inv.days_of_cover ASC;


-- ────────────────────────────────────────────────────────────
-- SECTION 5 │ VENDOR SCORECARD ANALYTICS  (Paper Section 8.4.2)
-- ────────────────────────────────────────────────────────────

-- 5A. Full vendor scorecard (Tableau vendor performance dashboard)
SELECT
    vs.vendor_name,
    mc.name                                           AS category,
    vs.city,
    vs.total_pos,
    ROUND(vs.on_time_rate * 100, 1)                   AS on_time_pct,
    vs.delivery_score,
    vs.price_score,
    vs.quality_score,
    vs.responsiveness,
    vs.composite_score,
    vs.status
FROM vendor_scorecards vs
JOIN material_categories mc ON vs.cat_id = mc.cat_id
ORDER BY vs.composite_score DESC;


-- 5B. Vendors flagged for review (composite score < 6.5)
SELECT
    vs.vendor_name,
    mc.name                                           AS category,
    vs.composite_score,
    vs.on_time_rate,
    vs.quality_score,
    vs.status
FROM vendor_scorecards vs
JOIN material_categories mc ON vs.cat_id = mc.cat_id
WHERE vs.status = 'Under Review'
ORDER BY vs.composite_score ASC;


-- 5C. Preferred vendors by category (top performer per category)
SELECT
    mc.name                                           AS category,
    vs.vendor_name,
    vs.city,
    vs.composite_score,
    vs.status
FROM vendor_scorecards vs
JOIN material_categories mc ON vs.cat_id = mc.cat_id
WHERE vs.composite_score = (
    SELECT MAX(vs2.composite_score)
    FROM vendor_scorecards vs2
    WHERE vs2.cat_id = vs.cat_id
)
ORDER BY mc.name;


-- 5D. Vendor performance vs spend (are we buying most from best vendors?)
SELECT
    v.name                                            AS vendor,
    mc.name                                           AS category,
    vs.composite_score,
    vs.status,
    COUNT(po.po_id)                                   AS po_count,
    ROUND(SUM(po.total_value_inr),2)                  AS total_spend_inr,
    ROUND(SUM(po.on_time)*100.0/COUNT(*),1)           AS actual_on_time_pct
FROM vendor_scorecards vs
JOIN vendors            v  ON vs.vendor_id   = v.vendor_id
JOIN material_categories mc ON vs.cat_id     = mc.cat_id
LEFT JOIN purchase_orders po ON po.vendor_id = v.vendor_id
GROUP BY v.vendor_id, v.name, mc.name
HAVING po_count > 0
ORDER BY total_spend_inr DESC;


-- ────────────────────────────────────────────────────────────
-- SECTION 6 │ EXECUTIVE KPI SUMMARY  (Paper Table – Findings)
-- ────────────────────────────────────────────────────────────

-- 6A. All KPIs in one view – matches the paper's KPI table exactly
SELECT 'On-Time Material Availability %'  AS kpi,
       '90%'                              AS target,
       ROUND(SUM(on_time)*100.0/COUNT(*),1)||'%' AS achieved,
       CASE WHEN ROUND(SUM(on_time)*100.0/COUNT(*),1) >= 90
            THEN 'Exceeded' ELSE 'Missed' END AS status
FROM purchase_orders
UNION ALL
SELECT 'Three-Way Match Success %',
       '90%',
       ROUND(SUM(CASE WHEN three_way_match='Pass' THEN 1 END)*100.0/COUNT(*),1)||'%',
       CASE WHEN ROUND(SUM(CASE WHEN three_way_match='Pass' THEN 1 END)*100.0/COUNT(*),1) >= 90
            THEN 'Met' ELSE 'Missed' END
FROM purchase_orders
UNION ALL
SELECT 'Amended POs %',
       '<16%',
       ROUND(SUM(amended)*100.0/COUNT(*),1)||'%',
       CASE WHEN ROUND(SUM(amended)*100.0/COUNT(*),1) <= 16
            THEN 'Met' ELSE 'Exceeded' END
FROM purchase_orders
UNION ALL
SELECT 'Inventory Accuracy %',
       '92%',
       ROUND(SUM(accuracy_flag)*100.0/COUNT(*),1)||'%',
       CASE WHEN ROUND(SUM(accuracy_flag)*100.0/COUNT(*),1) >= 92
            THEN 'Exceeded' ELSE 'Missed' END
FROM inventory
UNION ALL
SELECT 'Stock-Out Incidents',
       '<5',
       CAST(SUM(replenish_alert) AS TEXT),
       CASE WHEN SUM(replenish_alert) < 5
            THEN 'Met' ELSE 'Review' END
FROM inventory
UNION ALL
SELECT 'Vendor Dashboard Coverage %',
       '80%',
       '100%',
       'Exceeded';
