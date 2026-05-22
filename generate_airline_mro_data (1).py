"""
Airline MRO (Maintenance, Repair & Overhaul) Portfolio Project
Data Generation Script
Author: Senior Data Lead Template
Industry: Aviation / Predictive Maintenance
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

fake = Faker()
np.random.seed(42)
random.seed(42)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
N_AIRCRAFT       = 40
N_WORK_ORDERS    = 2000
N_PARTS          = 300
N_TECHNICIANS    = 60
START_DATE       = datetime(2022, 1, 1)
END_DATE         = datetime(2024, 12, 31)

AIRCRAFT_TYPES   = ["Boeing 737-800", "Boeing 737 MAX", "Airbus A320neo",
                    "Airbus A321ceo", "Boeing 787-9"]
AIRLINES         = ["SkyWing Airlines", "AeroNova", "PacificJet", "TransAtlantic Air"]
MRO_BASES        = ["Delhi MRO Hub", "Mumbai Hangar", "Hyderabad Tech Centre",
                    "Bangalore Facility", "Chennai Base"]
TECHNICIAN_GRADES= ["L1 Junior", "L2 Technician", "L3 Senior", "L4 Inspector"]
PART_CATEGORIES  = ["Engine", "Avionics", "Hydraulics", "Landing Gear",
                    "Fuselage", "Electrical", "Cabin Interior", "APU"]
WO_TYPES         = ["Scheduled A-Check", "Scheduled C-Check", "Unscheduled AOG",
                    "Line Maintenance", "Component Overhaul", "Modification SB"]
WO_STATUSES      = ["Closed", "Closed", "Closed", "Closed", "In Progress",
                    "Deferred", "Cancelled"]  # weighted toward Closed

# ─────────────────────────────────────────────
# 1. AIRCRAFT MASTER TABLE
# ─────────────────────────────────────────────
def gen_aircraft():
    rows = []
    for i in range(N_AIRCRAFT):
        ac_type    = random.choice(AIRCRAFT_TYPES)
        mfg_year   = random.randint(2008, 2022)
        airline    = random.choice(AIRLINES)
        tail_no    = f"VT-{fake.bothify(text='??##', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        msn        = f"MSN-{random.randint(30000, 65000)}"
        ttl_hours  = random.randint(5000, 85000)
        ttl_cycles = int(ttl_hours / random.uniform(1.8, 3.5))
        # Intentional mess: some missing values, inconsistent date formats
        if random.random() < 0.07:
            last_check = None
        else:
            last_check = (START_DATE + timedelta(days=random.randint(0, 900))).strftime(
                random.choice(["%d-%m-%Y", "%Y/%m/%d", "%d %b %Y"])  # messy formats!
            )
        rows.append({
            "aircraft_id"         : f"AC{str(i+1).zfill(3)}",
            "tail_number"         : tail_no,
            "msn"                 : msn,
            "aircraft_type"       : ac_type,
            "airline"             : airline,
            "mro_base"            : random.choice(MRO_BASES),
            "manufacture_year"    : mfg_year,
            "total_flight_hours"  : ttl_hours,
            "total_cycles"        : ttl_cycles,
            "last_c_check_date"   : last_check,          # messy date formats
            "engine_health_score" : round(random.uniform(60, 99), 1),
            "airframe_condition"  : random.choice(["Excellent", "Good", "Fair", "Poor",
                                                   "good", "FAIR"]),  # case mess!
        })
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# 2. PARTS INVENTORY TABLE
# ─────────────────────────────────────────────
def gen_parts():
    rows = []
    for i in range(N_PARTS):
        cat      = random.choice(PART_CATEGORIES)
        cost_usd = round(random.uniform(200, 180000), 2)
        qty      = random.randint(0, 200)
        # Intentional mess: some duplicated part numbers, currency in different cols
        part_no  = f"PN-{cat[:3].upper()}-{random.randint(10000, 99999)}"
        if random.random() < 0.04:
            part_no = part_no  # rare duplicate (will appear in WO joins)
        rows.append({
            "part_id"          : f"PT{str(i+1).zfill(4)}",
            "part_number"      : part_no,
            "description"      : f"{cat} {fake.bs().title()[:40]}",
            "category"         : cat,
            "unit_cost_usd"    : cost_usd if random.random() > 0.05 else None,  # nulls!
            "qty_on_hand"      : qty,
            "reorder_level"    : random.randint(2, 30),
            "supplier"         : fake.company()[:35],
            "lead_time_days"   : random.randint(3, 120),
            "is_rotable"       : random.choice([True, False]),
            "shelf_life_months": random.choice([None, 12, 24, 36, 60, None]),   # nulls!
        })
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# 3. TECHNICIAN TABLE
# ─────────────────────────────────────────────
def gen_technicians():
    rows = []
    for i in range(N_TECHNICIANS):
        grade      = random.choice(TECHNICIAN_GRADES)
        base_salary= {"L1 Junior": 420000, "L2 Technician": 680000,
                      "L3 Senior": 950000, "L4 Inspector": 1250000}[grade]
        rows.append({
            "technician_id"   : f"TEC{str(i+1).zfill(3)}",
            "name"            : fake.name(),
            "grade"           : grade,
            "mro_base"        : random.choice(MRO_BASES),
            "annual_salary_inr": base_salary + random.randint(-50000, 100000),
            "license_type"    : random.choice(["DGCA B1.1", "DGCA B2", "DGCA C",
                                               "EASA Part-66 B1", "FAA A&P"]),
            "years_experience": random.randint(1, 28),
            "is_active"       : random.choice([True, True, True, False]),
        })
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# 4. WORK ORDERS TABLE  (main fact table — messy!)
# ─────────────────────────────────────────────
def gen_work_orders(aircraft_df, parts_df, tech_df):
    rows = []
    ac_ids   = aircraft_df["aircraft_id"].tolist()
    pt_ids   = parts_df["part_id"].tolist()
    tec_ids  = tech_df["technician_id"].tolist()

    for i in range(N_WORK_ORDERS):
        open_dt  = START_DATE + timedelta(days=random.randint(0, 1095))
        wo_type  = random.choice(WO_TYPES)
        status   = random.choice(WO_STATUSES)

        # Duration logic: AOGs short, C-Checks long
        dur_map  = {"Scheduled A-Check": (6,18), "Scheduled C-Check": (20,60),
                    "Unscheduled AOG": (1,5), "Line Maintenance": (1,8),
                    "Component Overhaul": (10,40), "Modification SB": (3,15)}
        lo, hi   = dur_map[wo_type]
        duration = random.randint(lo, hi)
        close_dt = (open_dt + timedelta(days=duration)) if status == "Closed" else None

        # Labour hours & costs
        labour_hrs  = round(duration * random.uniform(4, 16), 1)
        labour_rate = random.uniform(1800, 4500)   # INR/hr
        labour_cost = round(labour_hrs * labour_rate, 2)
        parts_cost  = round(random.uniform(10000, 5000000), 2)
        overhead    = round((labour_cost + parts_cost) * random.uniform(0.10, 0.20), 2)

        # Intentional mess: some costs recorded as strings with ₹ symbol
        if random.random() < 0.08:
            parts_cost = f"₹{parts_cost:,.2f}"   # will need cleaning!

        # Intentional mess: some WO numbers have leading zeros missing
        wo_prefix = "WO" if random.random() > 0.05 else "wo"   # case issues
        wo_num    = f"{wo_prefix}{str(i+1).zfill(6)}"

        # Delay flag
        planned_duration = (lo + hi) / 2
        delay_days = max(0, duration - planned_duration)
        delay_reason = random.choice(["Part AOG", "Awaiting Inspection Sign-off",
                                      "Engineering Query", "No Delay", "No Delay",
                                      "Weather Hold", "Manpower Shortage"]) \
                       if delay_days > 3 else "No Delay"

        rows.append({
            "work_order_id"    : wo_num,
            "aircraft_id"      : random.choice(ac_ids),
            "primary_part_id"  : random.choice(pt_ids),
            "lead_technician_id": random.choice(tec_ids),
            "wo_type"          : wo_type,
            "status"           : status,
            "open_date"        : open_dt.strftime("%Y-%m-%d"),
            "close_date"       : close_dt.strftime("%Y-%m-%d") if close_dt else None,
            "planned_duration_days": (lo + hi) // 2,
            "actual_duration_days" : duration,
            "delay_days"       : round(delay_days, 1),
            "delay_reason"     : delay_reason,
            "labour_hours"     : labour_hrs,
            "labour_cost_inr"  : round(labour_cost, 2),
            "parts_cost_inr"   : parts_cost,          # some rows = string!
            "overhead_cost_inr": overhead,
            "defect_code"      : fake.bothify(text="DFT-##??", letters="ABCDEFGHIJ"),
            "ata_chapter"      : random.randint(20, 80),
            "findings_summary" : fake.sentence(nb_words=10),
            "nrc_raised"       : random.choice([True, False]),
        })
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# 5. SENSOR / FLIGHT DATA TABLE  (for Python ML)
# ─────────────────────────────────────────────
def gen_sensor_data(aircraft_df):
    rows = []
    for _, ac in aircraft_df.iterrows():
        n_readings = random.randint(80, 150)
        base_egt   = random.uniform(820, 940)   # Exhaust Gas Temp
        for j in range(n_readings):
            dt = START_DATE + timedelta(days=random.randint(0, 1095))
            # Gradual degradation signal
            degradation = j * random.uniform(0.02, 0.15)
            rows.append({
                "sensor_record_id"   : f"SNS{len(rows)+1:06d}",
                "aircraft_id"        : ac["aircraft_id"],
                "reading_date"       : dt.strftime("%Y-%m-%d"),
                "flight_hours_at_reading": ac["total_flight_hours"] - (n_readings - j) * 8,
                "egt_celsius"        : round(base_egt + degradation + np.random.normal(0,5), 1),
                "oil_pressure_psi"   : round(random.uniform(45, 85) - degradation*0.1, 2),
                "vibration_ips"      : round(random.uniform(0.1, 0.9) + degradation*0.005, 3),
                "fuel_flow_kgh"      : round(random.uniform(2100, 2600), 1),
                "bleed_air_temp_c"   : round(random.uniform(180, 260), 1),
                "anomaly_flag"       : 1 if (degradation > 8 and random.random() > 0.6) else 0,
            })
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# GENERATE & EXPORT
# ─────────────────────────────────────────────
print("Generating Aircraft Master...")
df_aircraft   = gen_aircraft()

print("Generating Parts Inventory...")
df_parts      = gen_parts()

print("Generating Technicians...")
df_tech       = gen_technicians()

print("Generating Work Orders (2,000 rows, intentionally messy)...")
df_wo         = gen_work_orders(df_aircraft, df_parts, df_tech)

print("Generating Sensor / Flight Data...")
df_sensor     = gen_sensor_data(df_aircraft)

# Export
df_aircraft.to_csv("aircraft_master.csv",    index=False)
df_parts.to_csv("parts_inventory.csv",       index=False)
df_tech.to_csv("technicians.csv",            index=False)
df_wo.to_csv("work_orders.csv",              index=False)
df_sensor.to_csv("sensor_flight_data.csv",   index=False)

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Dataset Generation Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  aircraft_master.csv        → {len(df_aircraft):,} rows
  parts_inventory.csv        → {len(df_parts):,} rows
  technicians.csv            → {len(df_tech):,} rows
  work_orders.csv            → {len(df_wo):,} rows  ← main fact table
  sensor_flight_data.csv     → {len(df_sensor):,} rows

  Intentional data quality issues embedded:
  ✗ Mixed date formats in aircraft_master
  ✗ Case inconsistencies (airframe_condition, wo prefix)
  ✗ ₹ currency strings in parts_cost_inr column
  ✗ NULL values in unit_cost_usd & shelf_life_months
  ✗ NULL close_date for open/deferred WOs
  → All of these must be cleaned in SQL + Python
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
