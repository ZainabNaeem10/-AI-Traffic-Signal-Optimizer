# AI Signal Time Optimizer

This project optimizes traffic signal timings for a two-phase intersection (North-South and East-West).
It integrates optimization algorithms with a machine learning model to reduce average vehicle waiting time.

The system includes:

* Simulated Annealing (SA) — primary optimization method
* Hill Climbing (HC) — baseline comparison
* Genetic Algorithm (GA) — evolutionary optimization
* Machine Learning — predicts traffic demand based on time and day

A time-stepped traffic simulation model calculates delay, and a Streamlit application provides an interactive interface.

---

# Execution Instructions and Dependencies

## Required Packages

Install all dependencies using:

pip install -r requirements.txt

---

## How to Run

### Step 1 — Generate Dataset (one-time)

python generate_data.py

### Step 2 — Train ML Model (one-time)

python train_model.py

### Step 3 — Run Application

streamlit run app.py

---

## Application Usage

1. Open the app in browser (localhost:8501)
2. Select Mode:

   * Manual Input → use sliders
   * ML Prediction → automatic traffic prediction
3. Choose optimization algorithm
4. Click "Run AI Optimization"
5. View results and comparison

---

# System Workflow

## Manual Mode

User Input (Sliders) → Traffic Demand → Optimization → Results

## ML Mode

Time + Day → ML Model → Predicted Traffic → Optimization → Results

---

# Sample Input / Output

## Sample Input (Manual Mode)

* Cycle Length: 60 seconds
* Clearance Time: 6 seconds
* Traffic Demand:

  * North: 15
  * South: 12
  * East: 10
  * West: 8

## Sample Input (ML Mode)

* Time of Day: 8 (morning peak)
* Day Type: Weekday

---

## Sample Output

* Optimized NS Green Time: 16 seconds
* Optimized EW Green Time: 38 seconds
* Delay Reduction: approximately 10–15%

Check:
NS(16) + EW(38) + Clearance(6) = 60 seconds

Bar chart shows:

* Equal Split (higher delay)
* AI Optimized (lower delay)

---

# Machine Learning Component

A Random Forest Regressor is trained on simulated data.

## Features:

* Time of Day (0–23)
* Day Type (Weekday / Weekend)

## Outputs:

* Predicted traffic (cars per minute) for:

  * North, South, East, West

The model is trained using synthetic data generated from the simulation engine.

---

# Technical Implementation

## Simulation (traffic_engine.py)

* 600-second time-step simulation
* FIFO queue model
* Per-second vehicle arrival and departure
* Calculates total delay and congestion penalty

---

## Optimization (optimizer.py)

### Simulated Annealing (SA)

* Starts with equal split
* Generates neighboring solutions
* Uses probabilistic acceptance (Metropolis criterion)
* Runs for up to 2000 iterations

### Hill Climbing (HC)

* Greedy local search
* Stops at local optimum

### Genetic Algorithm (GA)

* Population-based optimization
* Uses selection, crossover, and mutation
* Evolves better solutions over generations

---

## ML Integration

* Dataset generated using simulation
* Model trained using scikit-learn
* Integrated into Streamlit application
* Predicts traffic demand dynamically

---

# Project Files

* app.py — Streamlit interface
* traffic_engine.py — traffic simulation model
* optimizer.py — SA, HC, GA algorithms
* generate_data.py — dataset generation
* train_model.py — ML training script
* traffic_model.pkl — trained model
* traffic_data.csv — generated dataset

---

# Performance

* Data generation: a few seconds to minutes (depending on parameters)
* Model training: less than 1 second
* Application runtime: real-time

---

# Notes

* The system uses simulated data (no real-world sensors)
* Designed for academic and experimental purposes
* Demonstrates integration of optimization and machine learning
