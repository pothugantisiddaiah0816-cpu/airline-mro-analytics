-- ═══════════════════════════════════════════════════════
-- AIRLINE MRO ANALYTICS PROJECT
-- File: create_views.sql
-- Purpose: Create KPI views joining all tables
-- ═══════════════════════════════════════════════════════

USE airline_mro;

-- ───────────────────────────────────────────────────────
-- VIEW 1: WORK ORDER KPI VIEW
-- Purpose: Main analytical view joining 3 tables
-- Used by: Python, Power BI
-- ───────────────────────────────────────────────────────
DROP VIEW IF EXISTS vw_work_order_kpi;

CREATE VIEW vw_work_order_kpi AS
SELECT
    -- Work Order Details
    wo.work_order_id,
    wo.wo_type,
    wo.status,
    wo.open_date,
    wo.close_date,
    wo.planned_duration_days,
    wo.actual_duration_days,
    wo.delay_days,
    wo.delay_reason,
    wo.labour_hours,
    wo.nrc_raised,
    wo.defect_code,
    wo.ata_chapter,

    -- Cost Calculations
    wo.labour_cost_inr,
    CAST(wo.parts_cost_inr AS DECIMAL(15,2)) AS parts_cost_inr,
    wo.overhead_cost_inr,

    -- KPI 1: Total Cost per Work Order
    ROUND(
        wo.labour_cost_inr +
        CAST(wo.parts_cost_inr AS DECIMAL(15,2)) +
        wo.overhead_cost_inr,
    2) AS total_cost_inr,

    -- KPI 2: Cost Overrun Percentage
    ROUND(
        ((wo.actual_duration_days - wo.planned_duration_days)
        / wo.planned_duration_days) * 100,
    2) AS cost_overrun_pct,

    -- Aircraft Details (from aircraft_master)
    ac.tail_number,
    ac.aircraft_type,
    ac.airline,
    ac.mro_base,
    ac.manufacture_year,
    ac.total_flight_hours,
    ac.engine_health_score,
    ac.airframe_condition,

    -- Technician Details (from technicians)
    t.name            AS technician_name,
    t.grade           AS technician_grade,
    t.license_type,
    t.years_experience

FROM airline_mro.work_orders wo
JOIN airline_mro.aircraft_master ac
    ON wo.aircraft_id = ac.aircraft_id
JOIN airline_mro.technicians t
    ON wo.lead_technician_id = t.technician_id;

-- ───────────────────────────────────────────────────────
-- VIEW 2: AIRCRAFT RISK SUMMARY VIEW
-- Purpose: Summarise risk per aircraft for Power BI
-- ───────────────────────────────────────────────────────
DROP VIEW IF EXISTS vw_aircraft_risk_summary;

CREATE VIEW vw_aircraft_risk_summary AS
SELECT
    ac.aircraft_id,
    ac.tail_number,
    ac.aircraft_type,
    ac.airline,
    ac.mro_base,
    ac.engine_health_score,

    -- Work Order Statistics
    COUNT(wo.work_order_id)                    AS total_work_orders,
    SUM(CASE WHEN wo.wo_type = 'Unscheduled AOG'
        THEN 1 ELSE 0 END)                     AS aog_count,
    AVG(wo.delay_days)                         AS avg_delay_days,

    -- Cost Statistics
    SUM(wo.labour_cost_inr)                    AS total_labour_cost,
    AVG(wo.labour_cost_inr)                    AS avg_labour_cost,

    -- Performance Flag
    CASE
        WHEN AVG(wo.delay_days) > 5 THEN 'High Risk'
        WHEN AVG(wo.delay_days) > 2 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS performance_category

FROM airline_mro.aircraft_master ac
LEFT JOIN airline_mro.work_orders wo
    ON ac.aircraft_id = wo.aircraft_id
GROUP BY
    ac.aircraft_id,
    ac.tail_number,
    ac.aircraft_type,
    ac.airline,
    ac.mro_base,
    ac.engine_health_score;

-- ───────────────────────────────────────────────────────
-- VIEW 3: DELAY ANALYSIS VIEW
-- Purpose: Analyse delay patterns by reason and WO type
-- ───────────────────────────────────────────────────────
DROP VIEW IF EXISTS vw_delay_analysis;

CREATE VIEW vw_delay_analysis AS
SELECT
    wo_type,
    delay_reason,
    COUNT(*)                AS total_occurrences,
    AVG(delay_days)         AS avg_delay_days,
    MAX(delay_days)         AS max_delay_days,
    SUM(delay_days)         AS total_delay_days,
    AVG(labour_cost_inr)    AS avg_labour_cost
FROM airline_mro.work_orders
WHERE delay_reason != 'No Delay'
GROUP BY wo_type, delay_reason
ORDER BY avg_delay_days DESC;

-- ───────────────────────────────────────────────────────
-- VERIFY: Test all views
-- ───────────────────────────────────────────────────────
SELECT COUNT(*) AS kpi_view_rows        FROM vw_work_order_kpi;
SELECT COUNT(*) AS risk_summary_rows    FROM vw_aircraft_risk_summary;
SELECT COUNT(*) AS delay_analysis_rows  FROM vw_delay_analysis;

-- Sample output from main KPI view
SELECT
    work_order_id,
    wo_type,
    airline,
    total_cost_inr,
    cost_overrun_pct,
    technician_name,
    technician_grade
FROM vw_work_order_kpi
LIMIT 10;
