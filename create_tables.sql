-- ═══════════════════════════════════════════════════════
-- AIRLINE MRO ANALYTICS PROJECT
-- File: create_tables.sql
-- Purpose: Create database and all 5 tables
-- ═══════════════════════════════════════════════════════

-- Create Database
CREATE DATABASE IF NOT EXISTS airline_mro;
USE airline_mro;

-- ───────────────────────────────────────────────────────
-- TABLE 1: AIRCRAFT MASTER
-- Source: Fleet Management System
-- ───────────────────────────────────────────────────────
CREATE TABLE aircraft_master (
    aircraft_id           VARCHAR(10) PRIMARY KEY,
    tail_number           VARCHAR(10),
    msn                   VARCHAR(15),
    aircraft_type         VARCHAR(30),
    airline               VARCHAR(40),
    mro_base              VARCHAR(40),
    manufacture_year      INT,
    total_flight_hours    INT,
    total_cycles          INT,
    last_c_check_date     VARCHAR(20),
    engine_health_score   FLOAT,
    airframe_condition    VARCHAR(20)
);

-- ───────────────────────────────────────────────────────
-- TABLE 2: PARTS INVENTORY
-- Source: Warehouse ERP System
-- ───────────────────────────────────────────────────────
CREATE TABLE parts_inventory (
    part_id            VARCHAR(10) PRIMARY KEY,
    part_number        VARCHAR(20),
    description        VARCHAR(100),
    category           VARCHAR(30),
    unit_cost_usd      FLOAT,
    qty_on_hand        INT,
    reorder_level      INT,
    supplier           VARCHAR(50),
    lead_time_days     INT,
    is_rotable         BOOLEAN,
    shelf_life_months  FLOAT
);

-- ───────────────────────────────────────────────────────
-- TABLE 3: TECHNICIANS
-- Source: HR System
-- ───────────────────────────────────────────────────────
CREATE TABLE technicians (
    technician_id      VARCHAR(10) PRIMARY KEY,
    name               VARCHAR(50),
    grade              VARCHAR(20),
    mro_base           VARCHAR(40),
    annual_salary_inr  FLOAT,
    license_type       VARCHAR(20),
    years_experience   INT,
    is_active          BOOLEAN
);

-- ───────────────────────────────────────────────────────
-- TABLE 4: WORK ORDERS (Main Fact Table)
-- Source: MRO Operations System
-- ───────────────────────────────────────────────────────
CREATE TABLE work_orders (
    work_order_id          VARCHAR(15),
    aircraft_id            VARCHAR(10),
    primary_part_id        VARCHAR(10),
    lead_technician_id     VARCHAR(10),
    wo_type                VARCHAR(30),
    status                 VARCHAR(20),
    open_date              DATE,
    close_date             DATE,
    planned_duration_days  INT,
    actual_duration_days   INT,
    delay_days             FLOAT,
    delay_reason           VARCHAR(50),
    labour_hours           FLOAT,
    labour_cost_inr        FLOAT,
    parts_cost_inr         VARCHAR(30),
    overhead_cost_inr      FLOAT,
    defect_code            VARCHAR(15),
    ata_chapter            INT,
    findings_summary       VARCHAR(200),
    nrc_raised             BOOLEAN
);

-- ───────────────────────────────────────────────────────
-- TABLE 5: SENSOR FLIGHT DATA
-- Source: Aircraft Engine Sensors
-- ───────────────────────────────────────────────────────
CREATE TABLE sensor_flight_data (
    sensor_record_id          VARCHAR(15) PRIMARY KEY,
    aircraft_id               VARCHAR(10),
    reading_date              DATE,
    flight_hours_at_reading   FLOAT,
    egt_celsius               FLOAT,
    oil_pressure_psi          FLOAT,
    vibration_ips             FLOAT,
    fuel_flow_kgh             FLOAT,
    bleed_air_temp_c          FLOAT,
    anomaly_flag              INT
);
