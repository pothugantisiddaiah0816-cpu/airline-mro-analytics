-- ═══════════════════════════════════════════════════════
-- AIRLINE MRO ANALYTICS PROJECT
-- File: clean_data.sql
-- Purpose: Clean all data quality issues
-- ═══════════════════════════════════════════════════════

USE airline_mro;

-- Disable safe update mode to allow bulk updates
SET SQL_SAFE_UPDATES = 0;

-- ───────────────────────────────────────────────────────
-- CLEAN 1: Fix airframe_condition case inconsistencies
-- Problem: Values like "FAIR", "fair", "FAIR" exist
-- Fix: Standardise to "Fair", "Good", "Poor" etc.
-- ───────────────────────────────────────────────────────
UPDATE airline_mro.aircraft_master
SET airframe_condition = CONCAT(
    UPPER(LEFT(LOWER(airframe_condition), 1)),
    SUBSTRING(LOWER(airframe_condition), 2)
);

-- ───────────────────────────────────────────────────────
-- CLEAN 2: Fix work_order_id prefix casing
-- Problem: Some IDs are "wo000001" instead of "WO000001"
-- Fix: Standardise all to uppercase "WO" prefix
-- ───────────────────────────────────────────────────────
UPDATE airline_mro.work_orders
SET work_order_id = CONCAT('WO', SUBSTRING(work_order_id, 3))
WHERE LOWER(LEFT(work_order_id, 2)) = 'wo';

-- ───────────────────────────────────────────────────────
-- CLEAN 3: Remove rupee symbol from parts_cost_inr
-- Problem: Some values stored as "₹1,20,000" (text)
-- Fix: Remove ₹ symbol so column can be used numerically
-- ───────────────────────────────────────────────────────
UPDATE airline_mro.work_orders
SET parts_cost_inr = REPLACE(parts_cost_inr, '₹', '')
WHERE parts_cost_inr LIKE '%₹%';

-- ───────────────────────────────────────────────────────
-- CLEAN 4: Fill NULL unit_cost_usd with column average
-- Problem: Some parts have missing cost values
-- Fix: Replace NULLs with average cost of all parts
-- ───────────────────────────────────────────────────────
UPDATE airline_mro.parts_inventory
SET unit_cost_usd = (
    SELECT AVG(unit_cost_usd)
    FROM (SELECT * FROM airline_mro.parts_inventory) temp
)
WHERE unit_cost_usd IS NULL;

-- ───────────────────────────────────────────────────────
-- CLEAN 5: Fill NULL shelf_life_months with 24
-- Problem: Some parts have missing shelf life values
-- Fix: Use 24 months as aviation industry standard default
-- ───────────────────────────────────────────────────────
UPDATE airline_mro.parts_inventory
SET shelf_life_months = 24
WHERE shelf_life_months IS NULL;

-- Re-enable safe update mode
SET SQL_SAFE_UPDATES = 1;

-- ───────────────────────────────────────────────────────
-- VERIFY: Check cleaning results
-- ───────────────────────────────────────────────────────
SELECT 'aircraft_master' AS table_name, COUNT(*) AS total_rows FROM aircraft_master
UNION ALL
SELECT 'parts_inventory', COUNT(*) FROM parts_inventory
UNION ALL
SELECT 'technicians', COUNT(*) FROM technicians
UNION ALL
SELECT 'work_orders', COUNT(*) FROM work_orders
UNION ALL
SELECT 'sensor_flight_data', COUNT(*) FROM sensor_flight_data;

-- Check NULL values remaining
SELECT 
    SUM(CASE WHEN unit_cost_usd IS NULL THEN 1 ELSE 0 END) AS null_unit_cost,
    SUM(CASE WHEN shelf_life_months IS NULL THEN 1 ELSE 0 END) AS null_shelf_life
FROM parts_inventory;

-- Check airframe_condition standardisation
SELECT DISTINCT airframe_condition 
FROM aircraft_master 
ORDER BY airframe_condition;
