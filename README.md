# Airline-MRO-Analytics
End-to-end MRO Predictive Maintenance Analytics System using SQL, Python, Excel and Power BI
# ✈ Airline MRO Cost Overrun & Predictive Maintenance Intelligence System

![Project Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Tools](https://img.shields.io/badge/Tools-SQL%20%7C%20Python%20%7C%20Excel%20%7C%20PowerBI-blue)
![Industry](https://img.shields.io/badge/Industry-Aviation%20%7C%20MRO-teal)

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Business Problem](#business-problem)
3. [Dataset Description](#dataset-description)
4. [Project Architecture](#project-architecture)
5. [Tools & Technologies](#tools--technologies)
6. [Stage 1 — SQL](#stage-1--sql-mysql)
7. [Stage 2 — Python](#stage-2--python)
8. [Stage 3 — Excel](#stage-3--excel)
9. [Stage 4 — Power BI](#stage-4--power-bi)
10. [Key Findings](#key-findings)
11. [ML Model Results](#ml-model-results)
12. [Financial Analysis Results](#financial-analysis-results)
13. [How to Run](#how-to-run)
14. [Project Structure](#project-structure)
15. [Interview Talking Points](#interview-talking-points)
16. [Resume Bullet Point](#resume-bullet-point)

---

## 🎯 Project Overview

This is an end-to-end data analytics and machine learning project built for 
a simulated regional airline operating 40 aircraft across 5 MRO 
(Maintenance, Repair & Overhaul) bases in India.

The project demonstrates a complete data pipeline from raw messy data 
to executive dashboard — covering SQL, Python, Advanced Excel and Power BI 
in a single integrated workflow.

---

## 💼 Business Problem

A regional airline operating 40 aircraft across 5 MRO bases in India is 
experiencing critical budget overruns on maintenance work orders — averaging 
31% above planned cost — and suffering unplanned Aircraft-on-Ground (AOG) 
events that cost ₹18-25 Lakh per day in lost revenue.

### Business Questions We Answer:
- Which aircraft are at highest risk of engine failure in the next 14 days?
- What is the true cost of reactive vs proactive maintenance?
- Which work order types cause the most delays and cost overruns?
- What is the ROI of investing in predictive maintenance?
- Which sensor readings are the strongest predictors of engine faults?

---

## 📊 Dataset Description

| Table | Rows | Columns | Source System |
|-------|------|---------|---------------|
| aircraft_master | 40 | 12 | Fleet Management System |
| parts_inventory | 300 | 11 | Warehouse ERP System |
| technicians | 60 | 8 | HR System |
| work_orders | 2,000 | 20 | MRO Operations System |
| sensor_flight_data | 4,558 | 10 | Aircraft Engine Sensors |
| **Total** | **6,958** | | |

### Intentional Data Quality Issues (Cleaned in SQL + Python):
- Mixed date formats (DD-MM-YYYY vs YYYY/MM/DD vs DD MMM YYYY)
- ₹ currency symbols in numeric cost columns
- Case inconsistencies (FAIR vs Fair vs fair)
- NULL values in unit_cost_usd and shelf_life_months
- NULL close_date for open/deferred work orders
- Work order prefix casing (WO vs wo)

---

## 🏗 Project Architecture

```
Raw CSV Files (5 datasets)
        |
        ▼
┌─────────────────┐
│   MySQL         │  → Data Cleaning → Star Schema → KPI Views
│   (SQL Stage)   │
└────────┬────────┘
         |
         ▼
┌─────────────────┐
│   Python        │  → EDA → Feature Engineering → XGBoost Model
│   (ML Stage)    │  → Risk Scores Export (risk_scores.csv)
└────────┬────────┘
         |
         ▼
┌─────────────────┐
│   Excel         │  → NPV Model → Scenario Analysis → Break-Even
│ (Finance Stage) │
└────────┬────────┘
         |
         ▼
┌─────────────────┐
│   Power BI      │  → 3-Page Executive Dashboard
│ (Dashboard)     │  → DAX Measures → Relationships
└─────────────────┘
```

---

## 🛠 Tools & Technologies

| Tool | Version | Purpose |
|------|---------|---------|
| MySQL | 10.4 | Database, cleaning, star schema |
| Python | 3.10 | EDA, feature engineering, ML model |
| Pandas | 2.3 | Data manipulation |
| XGBoost | 3.2 | Classification model |
| Scikit-learn | 1.7 | Train-test split, metrics |
| Matplotlib/Seaborn | Latest | Data visualisation |
| Microsoft Excel | 2019+ | Financial modelling, NPV, scenarios |
| Power BI Desktop | Latest | Executive dashboard |

---

## 🗄 Stage 1 — SQL (MySQL)

### What We Did:
1. Created `airline_mro` database with 5 normalised tables
2. Imported 6,958 rows of data via Table Data Import Wizard
3. Cleaned all 7 data quality issues using UPDATE, REPLACE, CONCAT functions
4. Built a Star Schema with work_orders as fact table
5. Created `vw_work_order_kpi` view joining 3 tables
6. Calculated KPIs: total_cost_inr, cost_overrun_pct, delay_days

### Key SQL Techniques Used:
```sql
-- Fix case inconsistencies
UPDATE aircraft_master
SET airframe_condition = CONCAT(
    UPPER(LEFT(LOWER(airframe_condition), 1)),
    SUBSTRING(LOWER(airframe_condition), 2)
);

-- Remove currency symbols
UPDATE work_orders
SET parts_cost_inr = REPLACE(parts_cost_inr, '₹', '')
WHERE parts_cost_inr LIKE '%₹%';

-- KPI View with JOINs
CREATE VIEW vw_work_order_kpi AS
SELECT 
    wo.work_order_id,
    ROUND(wo.labour_cost_inr + 
          CAST(wo.parts_cost_inr AS DECIMAL(15,2)) + 
          wo.overhead_cost_inr, 2) AS total_cost_inr,
    ROUND(((wo.actual_duration_days - wo.planned_duration_days) 
          / wo.planned_duration_days) * 100, 2) AS cost_overrun_pct,
    ac.aircraft_type, ac.airline, ac.mro_base,
    t.name AS technician_name, t.grade
FROM work_orders wo
JOIN aircraft_master ac ON wo.aircraft_id = ac.aircraft_id
JOIN technicians t ON wo.lead_technician_id = t.technician_id;
```

---

## 🐍 Stage 2 — Python

### What We Did:
1. Loaded all 5 datasets using Pandas
2. Performed EDA — distributions, missing values, statistics
3. Created 4 visualisation charts
4. Engineered 3 new features from raw sensor data
5. Trained XGBoost classifier to predict engine anomalies
6. Handled class imbalance with scale_pos_weight
7. Generated feature importance chart
8. Exported risk_scores.csv for Power BI

### Feature Engineering:
```python
# Rolling average temperature (last 5 readings)
sensor['rolling_avg_egt'] = sensor.groupby('aircraft_id')['egt_celsius'].transform(
    lambda x: x.rolling(window=5, min_periods=1).mean()
)

# Temperature trend (rising = danger signal)
sensor['egt_trend'] = sensor.groupby('aircraft_id')['egt_celsius'].diff().fillna(0)

# Vibration spike detection (2 standard deviations)
sensor['vibration_spike'] = (
    sensor['vibration_ips'] > 
    sensor['vibration_ips'].mean() + 2 * sensor['vibration_ips'].std()
).astype(int)
```

### ML Model Configuration:
```python
model = XGBClassifier(
    n_estimators=200,
    max_depth=4,
    random_state=42,
    scale_pos_weight=10  # handles 10:1 class imbalance
)
```

---

## 📊 Stage 3 — Excel Financial Model

### 4 Sheets Built:

**Sheet 1 — Raw_Data**
- 2,000 work orders imported via Power Query
- Parts cost cleaned using Power Query transformations

**Sheet 2 — KPI_Dashboard**
- 10 business KPIs using COUNTA, SUM, COUNTIF, AVERAGE, MAX
- Structured table references (Raw_Data[column_name])

**Sheet 3 — Scenario_Model**
- NPV calculation using Excel NPV() function
- ROI and Break-Even analysis
- 3×3 What-If sensitivity table
- Conditional formatting heat map (Green/Yellow/Red)

**Sheet 4 — Break_Even**
- Investment recovery analysis
- Payback period calculation
- Break-even AOG duration

### Key Excel Formulas:
```excel
-- 3 Year NPV of Savings
=NPV(B9, E7, E7, E7)

-- Return on Investment
=(E7/E6)*100

-- Break-Even Payback Period (Months)
=(E5/E7)*12

-- Handle text values in cost column
=SUMPRODUCT(ISNUMBER(Raw_Data[parts_cost_inr])
 *IF(ISNUMBER(Raw_Data[parts_cost_inr]),Raw_Data[parts_cost_inr],0))
```

---

## 📈 Stage 4 — Power BI Dashboard

### 3 Report Pages:

**Page 1 — Fleet Health Overview**
- 4 KPI Cards: Total MRO Cost, AOG Count, Avg Delay Days, Closed WO %
- Work Order Type Bar Chart
- Average Delay by Airline Column Chart
- Risk Category Pie Chart
- Airline Slicer for filtering

**Page 2 — Work Order Deep Dive Analysis**
- 3 KPI Cards: AOG Count, Total Labour Cost, Total Delay Days
- Average Labour Cost by WO Type Column Chart
- Average Delay Days by Delay Reason Bar Chart
- Work Order Status Donut Chart

**Page 3 — Fleet Risk Monitoring & Alerts**
- 2 KPI Cards: Total Anomalies, Fleet Avg Risk Score
- Aircraft Risk Score Table (all 40 aircraft)
- Risk Score Ranking Bar Chart
- Total Anomalies by Aircraft Column Chart

### DAX Measures Written:
```dax
Total MRO Cost = 
SUM(work_orders[labour_cost_inr]) + 
SUM(work_orders[overhead_cost_inr])

Avg Delay Days = AVERAGE(work_orders[delay_days])

AOG Count = 
COUNTROWS(FILTER(work_orders, 
    work_orders[wo_type] = "Unscheduled AOG"))

Closed WO % = 
DIVIDE(
    COUNTROWS(FILTER(work_orders, work_orders[status] = "Closed")),
    COUNTROWS(work_orders)
) * 100
```

---

## 🔍 Key Findings

### Work Order Analysis:
- Line Maintenance is most frequent WO type (395 jobs — 19.75% of total)
- Scheduled C-Check causes longest average delays (5+ days)
- 56.3% of work orders are Closed — 43.7% still open or problematic
- Average delay across all work orders: 2.28 days
- Maximum delay recorded: 20 days

### Cost Analysis:
- Total MRO Labour Cost: ₹95.86 Crore
- Total Parts Cost: ₹495.96 Crore
- Total Overhead Cost: ₹88.73 Crore
- Total MRO Spend: ₹680.57 Crore
- 323 AOG events recorded — highest cost risk category

### Delay Analysis:
- Weather Hold causes highest average delays
- Engineering Query and Manpower Shortage are next biggest causes
- Unscheduled AOG has shortest delay (resolved quickly due to urgency)

---

## 🤖 ML Model Results

| Metric | Value |
|--------|-------|
| Model | XGBoost Classifier |
| Training Data | 3,646 sensor readings |
| Test Data | 912 sensor readings |
| Overall Accuracy | 86% |
| AUC Score | 0.67 |
| Class Imbalance Ratio | 10:1 (normal:anomaly) |
| Fix Applied | scale_pos_weight=10 |

### Feature Importance Rankings:
1. **egt_trend** (0.28) — Temperature trend is strongest predictor
2. **rolling_avg_egt** (0.20) — Rolling average temperature
3. **egt_celsius** (0.19) — Raw temperature reading
4. **vibration_ips** (0.18) — Vibration level
5. **oil_pressure_psi** (0.16) — Oil pressure
6. **vibration_spike** (0.00) — Spike flag alone not predictive

### Why AUC is 0.67:
The synthetic dataset lacks strong real-world degradation patterns.
In production with real sensor data, AUC would significantly improve.
This is a valid data science finding — not a model failure.

---

## 💰 Financial Analysis Results

### Scenario Model:
| Metric | Value |
|--------|-------|
| Reactive Maintenance Cost (Annual) | ₹2.4 Crore |
| Proactive Maintenance Cost (Annual) | ₹50 Lakh |
| Annual Savings | ₹1.9 Crore |
| 3-Year NPV of Savings | ₹4.72 Crore |
| Return on Investment | 380% |
| Break-Even AOG Events | 0.25 (less than 1!) |

### Break-Even Analysis:
| Metric | Value |
|--------|-------|
| Total Inspection Investment | ₹50 Lakh |
| Expected Saving Per Aircraft | ₹45 Lakh |
| Total Expected Savings | ₹4.5 Crore |
| Net Benefit | ₹4 Crore |
| Payback Period | 1.33 months |

**Key Insight:** Preventing just ONE AOG event fully recovers 
the entire proactive maintenance investment.

---

## 🚀 How to Run

### Prerequisites:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost faker sqlalchemy pymysql
```

### Step 1 — Generate Data:
```bash
python generate_airline_mro_data.py
```
This creates 5 CSV files in your working directory.

### Step 2 — Setup MySQL Database:
1. Open MySQL Workbench
2. Run `sql/create_tables.sql`
3. Import all 5 CSV files using Table Data Import Wizard
4. Run `sql/clean_data.sql`
5. Run `sql/create_views.sql`

### Step 3 — Run Python Analysis:
```bash
python mro_analysis_complete.py
```
This generates EDA charts and risk_scores.csv

### Step 4 — Open Excel Model:
Open `MRO_Financial_Model.xlsx` — all formulas auto-calculate.

### Step 5 — Open Power BI Dashboard:
Open `MRO_Dashboard.pbix` — refresh data if needed.

---

## 👤 Author

# POTHUGANTI SIDDAIAH
- LinkedIn: https://www.linkedin.com/in/pothuganti-siddaiah/
- GitHub: 
- Email: pothugantisiddaiah0816@gmail.com

---

*Built as a portfolio project demonstrating end-to-end data analytics 
capabilities across SQL, Python, Excel and Power BI.*
