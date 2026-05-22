# ═══════════════════════════════════════════════════════════════
# AIRLINE MRO PREDICTIVE MAINTENANCE - COMPLETE PYTHON CODE
# Stage 2: EDA + Feature Engineering + ML Model
# ═══════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────
# SECTION 1: IMPORT LIBRARIES
# ───────────────────────────────────────────────────────────────

import pandas as pd
# pandas = the most important data analysis library in Python
# we give it a short name 'pd' so we dont have to type 'pandas' every time
# pd is used for reading CSV files, creating tables, cleaning data

import numpy as np
# numpy = numerical Python library
# used for mathematical operations like mean, standard deviation
# we call it 'np' for short

import matplotlib.pyplot as plt
# matplotlib = the base chart drawing library in Python
# pyplot is the sub-module that actually draws charts
# we call it 'plt' for short

import seaborn as sns
# seaborn = a prettier chart library built on top of matplotlib
# makes professional looking charts with less code

from sklearn.model_selection import train_test_split
# sklearn = scikit-learn, the main ML library in Python
# train_test_split = a function that splits data into training and testing sets

from sklearn.preprocessing import LabelEncoder
# LabelEncoder = converts text categories to numbers
# ML models only understand numbers, not text like "Boeing" or "Airbus"

from sklearn.metrics import classification_report, roc_auc_score
# classification_report = shows precision, recall, f1-score of our model
# roc_auc_score = gives overall model quality score between 0 and 1

from xgboost import XGBClassifier
# XGBoost = Extreme Gradient Boosting
# one of the most powerful and popular ML algorithms
# used in most winning Kaggle competitions and industry projects

from sklearn.cluster import KMeans
# KMeans = clustering algorithm
# groups similar aircraft together based on their behaviour

import warnings
warnings.filterwarnings("ignore")
# suppresses unnecessary warning messages so output is clean

print("✅ All libraries imported successfully!")


# ───────────────────────────────────────────────────────────────
# SECTION 2: LOAD DATA
# ───────────────────────────────────────────────────────────────

aircraft   = pd.read_csv(r"C:\Users\HP\Desktop\airline_mro\aircraft_master.csv")
# pd.read_csv() = reads a CSV file and converts it into a DataFrame
# DataFrame = a table with rows and columns, like an Excel sheet in Python
# r"..." = raw string, the r prefix means treat backslashes as literal characters
# without r, Python would interpret \n as newline, \t as tab etc.

parts      = pd.read_csv(r"C:\Users\HP\Desktop\airline_mro\parts_inventory.csv")
techs      = pd.read_csv(r"C:\Users\HP\Desktop\airline_mro\technicians.csv")
workorders = pd.read_csv(r"C:\Users\HP\Desktop\airline_mro\work_orders.csv")
sensor     = pd.read_csv(r"C:\Users\HP\Desktop\airline_mro\sensor_flight_data.csv")

print("✅ All datasets loaded!")
print(f"Aircraft:    {aircraft.shape}")
# .shape = returns (rows, columns) of the DataFrame
# f"..." = f-string, allows putting variables inside strings using {}
# aircraft.shape will print something like (40, 12)

print(f"Parts:       {parts.shape}")
print(f"Technicians: {techs.shape}")
print(f"Work Orders: {workorders.shape}")
print(f"Sensor Data: {sensor.shape}")


# ───────────────────────────────────────────────────────────────
# SECTION 3: EXPLORATORY DATA ANALYSIS (EDA)
# ───────────────────────────────────────────────────────────────

print("\n========== WORK ORDERS INFO ==========")
# \n = newline character, adds an empty line before the heading

print(workorders.info())
# .info() = shows column names, data types, and count of non-null values
# helps us understand the structure of the data
# object = text column, int64 = whole number, float64 = decimal number

print("\n========== MISSING VALUES ==========")
print(workorders.isnull().sum())
# .isnull() = returns True for every cell that is empty/missing
# .sum() = counts how many True values exist per column
# result shows how many missing values each column has

print("\n========== BASIC STATISTICS ==========")
print(workorders[['labour_cost_inr','overhead_cost_inr','delay_days']].describe())
# .describe() = shows count, mean, min, max, 25%, 50%, 75% for numeric columns
# workorders[[...]] = selecting multiple columns using double brackets
# this gives us a quick statistical summary of our cost and delay columns

print("\n========== WO TYPE DISTRIBUTION ==========")
print(workorders['wo_type'].value_counts())
# .value_counts() = counts how many times each unique value appears
# tells us which type of work order is most common

print("\n========== STATUS DISTRIBUTION ==========")
print(workorders['status'].value_counts())


# ───────────────────────────────────────────────────────────────
# SECTION 4: VISUALISATION - 4 CHARTS
# ───────────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
# plt.subplots(2, 2) = creates a grid of 2 rows and 2 columns = 4 charts
# figsize=(14, 10) = total figure size in inches (width=14, height=10)
# fig = the entire figure/canvas
# axes = a 2x2 array of individual chart areas
# axes[0,0] = top left, axes[0,1] = top right
# axes[1,0] = bottom left, axes[1,1] = bottom right

fig.suptitle('MRO Work Order Analysis', fontsize=16, fontweight='bold')
# suptitle = super title, a main heading for the entire figure
# fontsize=16 = text size
# fontweight='bold' = makes it bold

# CHART 1: Work Order Type Distribution (Bar Chart)
workorders['wo_type'].value_counts().plot(
    kind='bar',         # type of chart = vertical bar chart
    ax=axes[0,0],       # which chart area to draw in = top left
    color='steelblue',  # bar colour
    edgecolor='black'   # border colour of each bar
)
axes[0,0].set_title('Work Order Type Distribution')
# set_title = adds a title to this specific chart

axes[0,0].set_xlabel('WO Type')
# set_xlabel = label for the x axis (horizontal)

axes[0,0].set_ylabel('Count')
# set_ylabel = label for the y axis (vertical)

axes[0,0].tick_params(axis='x', rotation=45)
# tick_params = controls the axis labels
# rotation=45 = rotates x axis labels by 45 degrees so they dont overlap

# CHART 2: Average Delay by WO Type (Horizontal Bar Chart)
workorders.groupby('wo_type')['delay_days'].mean().sort_values().plot(
    kind='barh',       # barh = horizontal bar chart
    ax=axes[0,1],      # top right chart area
    color='coral',
    edgecolor='black'
)
# .groupby('wo_type') = groups all rows by work order type
# ['delay_days'].mean() = calculates average delay for each group
# .sort_values() = sorts from smallest to largest delay

axes[0,1].set_title('Average Delay Days by WO Type')
axes[0,1].set_xlabel('Average Delay Days')

# CHART 3: Labour Cost Distribution (Histogram)
axes[1,0].hist(
    workorders['labour_cost_inr'],  # which column to plot
    bins=30,                         # divide data into 30 equal groups
    color='green',
    edgecolor='black',
    alpha=0.7                        # transparency 0=invisible, 1=solid
)
# histogram shows how data is distributed
# tall bars = many work orders with that cost range
# short bars = few work orders with that cost range

axes[1,0].set_title('Labour Cost Distribution')
axes[1,0].set_xlabel('Labour Cost (INR)')
axes[1,0].set_ylabel('Frequency')

# CHART 4: Status Distribution (Pie Chart)
workorders['status'].value_counts().plot(
    kind='pie',          # pie chart
    ax=axes[1,1],        # bottom right chart area
    autopct='%1.1f%%',   # show percentage with 1 decimal place on each slice
    colors=['#2ecc71','#3498db','#e74c3c','#f39c12']
    # custom colours for each slice using hex colour codes
)
axes[1,1].set_title('Work Order Status Distribution')
axes[1,1].set_ylabel('')
# set_ylabel('') = removes the default 'status' label from pie chart

plt.tight_layout()
# tight_layout = automatically adjusts spacing so charts dont overlap

plt.savefig(r'C:\Users\HP\Desktop\airline_mro\Python_Analysis\eda_charts.png',
            dpi=150,           # dpi = dots per inch, higher = sharper image
            bbox_inches='tight' # crops extra whitespace around the figure
            )
plt.show()
print("✅ EDA Charts saved!")


# ───────────────────────────────────────────────────────────────
# SECTION 5: FEATURE ENGINEERING
# ───────────────────────────────────────────────────────────────
# Feature Engineering = creating new meaningful columns from existing ones
# These new columns help the ML model learn better patterns

print("\n========== BUILDING ML MODEL ==========")

sensor['reading_date'] = pd.to_datetime(sensor['reading_date'])
# pd.to_datetime() = converts text dates like "2023-05-21" into proper date objects
# needed so Python understands the date order for sorting

sensor = sensor.sort_values(['aircraft_id', 'reading_date'])
# .sort_values() = sorts the rows
# we sort by aircraft first, then by date
# this ensures rolling calculations are done in correct time order

sensor['rolling_avg_egt'] = sensor.groupby('aircraft_id')['egt_celsius'].transform(
    lambda x: x.rolling(window=5, min_periods=1).mean()
)
# .groupby('aircraft_id') = do the following operation separately for each aircraft
# ['egt_celsius'] = work on the engine temperature column
# .transform() = apply a function and return result in same shape as original
# lambda x: = defines a small anonymous function where x is the group data
# .rolling(window=5) = look at last 5 readings at a time
# .mean() = calculate average of those 5 readings
# Result: for each reading, what was the average temperature over last 5 readings?
# This smooths out random spikes and shows the trend

sensor['rolling_avg_vibration'] = sensor.groupby('aircraft_id')['vibration_ips'].transform(
    lambda x: x.rolling(window=5, min_periods=1).mean()
)
# Same concept but for vibration data

sensor['rolling_avg_oil'] = sensor.groupby('aircraft_id')['oil_pressure_psi'].transform(
    lambda x: x.rolling(window=5, min_periods=1).mean()
)
# Same concept but for oil pressure

sensor['egt_trend'] = sensor.groupby('aircraft_id')['egt_celsius'].diff().fillna(0)
# .diff() = calculates difference between current and previous reading
# Example: if yesterday temp was 920 and today is 935, diff = +15 (rising!)
# If diff is negative, temperature is falling (good sign)
# If diff is large positive consistently, engine is overheating (bad sign)
# .fillna(0) = first reading has no previous value, so fill it with 0

sensor['vibration_spike'] = (sensor['vibration_ips'] >
                              sensor['vibration_ips'].mean() +
                              2 * sensor['vibration_ips'].std()).astype(int)
# sensor['vibration_ips'].mean() = average vibration across all readings
# sensor['vibration_ips'].std() = standard deviation (how spread out values are)
# mean + 2*std = upper threshold (statistically, 95% of normal readings are below this)
# any reading ABOVE this threshold is a vibration spike
# (sensor['vibration_ips'] > threshold) = gives True or False for each row
# .astype(int) = converts True to 1 and False to 0

print("✅ Features engineered!")
print(sensor[['aircraft_id','egt_celsius','rolling_avg_egt',
              'egt_trend','vibration_spike','anomaly_flag']].head(10))
# .head(10) = show only the first 10 rows


# ───────────────────────────────────────────────────────────────
# SECTION 6: PREPARE DATA FOR ML MODEL
# ───────────────────────────────────────────────────────────────

features = ['egt_celsius', 'rolling_avg_egt',
            'egt_trend', 'vibration_ips',
            'oil_pressure_psi', 'vibration_spike']
# features = list of INPUT columns we give to the model
# These are like symptoms we describe to a doctor

target = 'anomaly_flag'
# target = the OUTPUT column we want to predict
# 0 = engine is fine, 1 = engine has a problem

X = sensor[features]
# X = input table (all feature columns)
# Convention in ML: inputs are always called X (capital X)
# X has shape (4558, 6) = 4558 readings, 6 features each

y = sensor[target]
# y = output column (just the anomaly_flag)
# Convention in ML: output is always called y (lowercase y)
# Comes from mathematics: y = f(x), output y depends on input x

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,    # 20% of data goes to testing, 80% for training
    random_state=42   # fixes the random split so results are same every run
                      # 42 is a popular choice (from Hitchhiker's Guide to the Galaxy!)
)
# train_test_split splits our data into 4 parts:
# X_train = 80% of input data used to TEACH the model
# X_test  = 20% of input data used to TEST the model (model never saw this before)
# y_train = 80% of correct answers used during teaching
# y_test  = 20% of correct answers used to check if model learned correctly


# ───────────────────────────────────────────────────────────────
# SECTION 7: TRAIN THE ML MODEL
# ───────────────────────────────────────────────────────────────

model = XGBClassifier(n_estimators=100, max_depth=4, random_state=42)
# XGBClassifier = XGBoost Classification model
# n_estimators=100 = build 100 decision trees
#   each tree makes a prediction, final answer is majority vote of all 100
#   more trees = more accurate but slower to train
# max_depth=4 = each tree can ask maximum 4 yes/no questions
#   Example tree: Is temp > 930? -> Is vibration > 0.5? -> Is trend > 5? -> Anomaly!
# random_state=42 = ensures same results every time we run

model.fit(X_train, y_train)
# .fit() = this is the actual TRAINING step
# model looks at X_train (sensor readings) and y_train (correct answers)
# it learns the pattern: which sensor combinations lead to anomalies?
# this is like showing thousands of exam questions WITH answers to a student

y_pred = model.predict(X_test)
# .predict() = model makes predictions on test data it never saw before
# returns 0 or 1 for each row in X_test
# this is like giving the student an exam WITHOUT the answers

y_prob = model.predict_proba(X_test)[:,1]
# .predict_proba() = instead of just 0 or 1, gives probability
# returns two columns: [probability of 0, probability of 1]
# [:,1] = take only the second column (probability of anomaly = 1)
# Example: 0.87 means 87% confident this is an engine fault

print("========== MODEL RESULTS ==========")
print(classification_report(y_test, y_pred))
# classification_report compares y_test (real answers) with y_pred (model answers)
# Precision = when model says anomaly, how often is it right?
# Recall = of all actual anomalies, how many did model find?
# F1-Score = balance between precision and recall
# Support = how many actual cases of each class exist

print(f"AUC Score: {roc_auc_score(y_test, y_prob):.4f}")
# AUC = Area Under the Curve, measures overall model quality
# 0.5 = random guessing (useless model)
# 0.7 = acceptable
# 0.8 = good
# 0.9+ = excellent
# :.4f = format number to 4 decimal places


# ───────────────────────────────────────────────────────────────
# SECTION 8: FIX IMBALANCED DATA PROBLEM
# ───────────────────────────────────────────────────────────────
# Problem: only 78 anomaly cases vs 834 normal cases
# Model is biased toward predicting normal because that gives high accuracy
# Solution: tell model that missing an anomaly is very costly

model2 = XGBClassifier(
    n_estimators=200,      # more trees than before for better learning
    max_depth=4,
    random_state=42,
    scale_pos_weight=10    # anomaly class gets 10x more importance
    # formula: scale_pos_weight = count(normal cases) / count(anomaly cases)
    # = 834 / 78 ≈ 10
    # this penalises the model more when it misses an actual anomaly
)
model2.fit(X_train, y_train)

y_pred2 = model2.predict(X_test)
y_prob2 = model2.predict_proba(X_test)[:,1]

print("========== IMPROVED MODEL RESULTS ==========")
print(classification_report(y_test, y_pred2))
print(f"AUC Score: {roc_auc_score(y_test, y_prob2):.4f}")


# ───────────────────────────────────────────────────────────────
# SECTION 9: FEATURE IMPORTANCE CHART
# ───────────────────────────────────────────────────────────────

importance_df = pd.DataFrame({
    'feature': features,                        # column names
    'importance': model2.feature_importances_   # importance scores from XGBoost
})
# pd.DataFrame({...}) = creates a new DataFrame from a dictionary
# dictionary format: {'column_name': [list of values], ...}
# model2.feature_importances_ = array of importance scores, one per feature
# scores sum to 1.0 (or close to it)

importance_df = importance_df.sort_values('importance', ascending=False)
# sort from most important to least important feature

plt.figure(figsize=(10, 6))
# creates a new figure with width=10, height=6 inches

sns.barplot(
    x='importance',      # x axis = importance score
    y='feature',         # y axis = feature name
    data=importance_df,  # which DataFrame to use
    palette='viridis'    # colour scheme (purple to yellow gradient)
)
# sns.barplot = seaborn horizontal bar chart

plt.title('Which Sensor Matters Most for Predicting Engine Faults?')
plt.xlabel('Importance Score')
plt.ylabel('Sensor Feature')
plt.tight_layout()
plt.savefig(r'C:\Users\HP\Desktop\airline_mro\Python_Analysis\feature_importance.png', dpi=150)
plt.show()


# ───────────────────────────────────────────────────────────────
# SECTION 10: EXPORT RISK SCORES FOR POWER BI
# ───────────────────────────────────────────────────────────────

sensor['risk_score'] = (model2.predict_proba(X)[:,1] * 100).round(2)
# predict_proba(X) = predict probability for ALL 4558 sensor readings (not just test)
# [:,1] = take the anomaly probability column
# * 100 = convert from 0-1 scale to 0-100 scale (easier to understand)
# .round(2) = round to 2 decimal places
# Example: 0.8734 becomes 87.34 (87.34% risk of engine fault)

risk_summary = sensor.groupby('aircraft_id').agg(
    avg_risk_score  = ('risk_score', 'mean'),   # average risk across all readings
    max_risk_score  = ('risk_score', 'max'),    # highest risk score ever recorded
    total_anomalies = ('anomaly_flag', 'sum')   # total number of anomaly events
).reset_index()
# .groupby('aircraft_id') = group all readings by aircraft
# .agg() = aggregate multiple calculations at once
# format: new_column_name = ('source_column', 'function')
# .reset_index() = converts the group keys back into regular columns

risk_summary['risk_category'] = pd.cut(
    risk_summary['avg_risk_score'],   # which column to categorise
    bins=[0, 30, 60, 100],            # boundaries: 0-30, 30-60, 60-100
    labels=['Low Risk', 'Medium Risk', 'High Risk']  # labels for each bin
)
# pd.cut() = converts a continuous number into categories
# 0 to 30 = Low Risk
# 30 to 60 = Medium Risk
# 60 to 100 = High Risk
# This makes it easy to show traffic light colours in Power BI

risk_summary.to_csv(
    r'C:\Users\HP\Desktop\airline_mro\risk_scores.csv',
    index=False  # dont save row numbers as a column
)
# .to_csv() = saves DataFrame as a CSV file
# index=False = prevents adding an extra column of row numbers (0,1,2,3...)

print("✅ Risk scores exported!")
print(risk_summary.head(10))
print("\n✅ PYTHON STAGE COMPLETE!")
