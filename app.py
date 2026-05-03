import streamlit as st
import pandas as pd
import joblib

from traffic_engine import TrafficEnvironment
from optimizer import (
    SimulatedAnnealing,
    HillClimbing,
    GeneticAlgorithm
)

st.set_page_config(page_title="AI Signal (Cross Section) Optimizer", layout="wide")

st.title("🚦 AI Signal (Cross Section) Optimizer")

# Load ML model
model = joblib.load("traffic_model.pkl")

# Sidebar controls
st.sidebar.header("Intersection Settings")

cycle_time = st.sidebar.slider("Cycle Length (seconds)", 40, 120, 60)

total_clearance_time = st.sidebar.slider(
    "Total Clearance (Yellow + All-Red)",
    4, 12, 6
)

# 🔥 NEW: Mode selection
mode = st.sidebar.radio(
    "Select Mode",
    ["Manual Input", "ML Prediction"]
)

# 🔥 TRAFFIC INPUT HANDLING
if mode == "Manual Input":
    st.sidebar.header("Traffic Demand (Cars Per Minute)")

    north_rate = st.sidebar.slider("North", 0, 50, 12)
    south_rate = st.sidebar.slider("South", 0, 50, 13)
    east_rate = st.sidebar.slider("East", 0, 50, 15)
    west_rate = st.sidebar.slider("West", 0, 50, 29)

    cars_per_minute = {
        'N': north_rate,
        'S': south_rate,
        'E': east_rate,
        'W': west_rate
    }

else:
    st.sidebar.header("ML Traffic Prediction")

    time_of_day = st.sidebar.slider("Time of Day", 0, 23, 8)

    day_type = st.sidebar.selectbox(
        "Day Type",
        ["Weekday", "Weekend"]
    )

    day_val = 0 if day_type == "Weekday" else 1

    # ML prediction
    input_data = pd.DataFrame({
    "time": [time_of_day],
    "day": [day_val]
    })

    prediction = model.predict(input_data)[0]

    cars_per_minute = {
        'N': int(prediction[0]),
        'S': int(prediction[1]),
        'E': int(prediction[2]),
        'W': int(prediction[3])
    }

    st.sidebar.success(f"Predicted Traffic: {cars_per_minute}")

# Algorithm selection
st.sidebar.header("Optimization Algorithm")

selected_algorithm = st.sidebar.selectbox(
    "Choose Algorithm",
    ["Simulated Annealing", "Hill Climbing", "Genetic Algorithm"]
)

# Run button
if st.button("Run AI Optimization", type="primary"):

    # Initialize environment with 4-phase clearance
    environment = TrafficEnvironment(
        cycle_time,
        t_total_clearance=total_clearance_time
    )

    if selected_algorithm == "Simulated Annealing":
        optimizer = SimulatedAnnealing(environment, cars_per_minute)
    elif selected_algorithm == "Hill Climbing":
        optimizer = HillClimbing(environment, cars_per_minute)
    else:
        optimizer = GeneticAlgorithm(environment, cars_per_minute)

    with st.spinner(f"Running {selected_algorithm}..."):
        # Optimizer now returns (gn, gs, ge, gw, delay)
        gn, gs, ge, gw, optimized_delay = optimizer.optimize()

    st.success(f"Algorithm Used: {selected_algorithm}")

    # Baseline (4-phase equal split)
    total_green_time = cycle_time - total_clearance_time
    base_val = total_green_time // 4
    baseline_timings = [base_val] * 4
    baseline_timings[0] += total_green_time - sum(baseline_timings)

    baseline_delay = environment.get_total_delay(
        *baseline_timings,
        cars_per_minute
    )

    st.subheader("4-Phase Optimization Results (LHD Split-Phasing)")

    # Display 4 metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("North Green", f"{gn}s")
    m2.metric("South Green", f"{gs}s")
    m3.metric("East Green", f"{ge}s")
    m4.metric("West Green", f"{gw}s")

    # Reduction metric
    improvement_percent = (
        (baseline_delay - optimized_delay) /
        max(0.01, baseline_delay)
    ) * 100
    
    st.metric("Total Delay Reduction", f"{improvement_percent:.1f}%")

    results_table = pd.DataFrame({
        "Scenario": ["Equal Split (25% each)", "AI Optimized (Split-Phasing)"],
        "Average Waiting Time (seconds)": [baseline_delay, optimized_delay]
    })

    st.bar_chart(results_table.set_index("Scenario"))

    st.info(
        f"**Verification Check:** N({gn}s) + S({gs}s) + E({ge}s) + W({gw}s) + "
        f"Clearance({total_clearance_time}s) = "
        f"{gn + gs + ge + gw + total_clearance_time}s "
        f"(Target Cycle: {cycle_time}s)"
    )