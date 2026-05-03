import streamlit as st
import pandas as pd
import joblib
import streamlit.components.v1 as components

def render_signal_animation(gn, gs, ge, gw, cycle, clr):
    """
    Renders an abstract HTML5 visualization of the 4-Phase signal cycle.
    Uses 'Light Bars' for approach lanes and includes a progress bar.
    """
    data = {
        "gn": gn, "gs": gs, "ge": ge, "gw": gw,
        "cycle": cycle, "clr": clr / 4
    }
    
    html_code = f"""
    <div style="background: #111; padding: 20px; border-radius: 15px; border: 1px solid #333; color: white; font-family: sans-serif; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        <h4 style="text-align: center; margin-bottom: 10px; margin-top: 0;">Live 4-Phase Signal Visualizer</h4>
        
        <!-- Legend -->
        <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 15px; font-size: 14px;">
            <div><span style="display:inline-block; width:15px; height:15px; background:#00ff55; margin-right:5px; vertical-align:middle;"></span> Green (Flow)</div>
            <div><span style="display:inline-block; width:15px; height:15px; background:#ffaa00; margin-right:5px; vertical-align:middle;"></span> Yellow (Clearance)</div>
            <div><span style="display:inline-block; width:15px; height:15px; background:#ff3333; margin-right:5px; vertical-align:middle;"></span> Red (Stopped)</div>
            <div><span style="display:inline-block; width:20px; height:0px; border-top:3px dashed #008833; margin-right:5px; vertical-align:middle;"></span> Free-Flow Left (LHD)</div>
        </div>

        <!-- Canvas -->
        <canvas id="signalCanvas" width="800" height="400" style="width: 100%; height: auto; background: #1a1c20; border-radius: 10px; margin-bottom: 15px;"></canvas>
        
        <!-- Progress Bar & Status -->
        <div style="text-align: center; padding: 0 20px;">
            <div id="statusText" style="font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #f2c14e;">Initializing...</div>
            <progress id="cycleProgress" value="0" max="{cycle}" style="width: 100%; height: 15px;"></progress>
        </div>
    </div>

    <script>
    const canvas = document.getElementById('signalCanvas');
    const ctx = canvas.getContext('2d');
    const pBar = document.getElementById('cycleProgress');
    const sText = document.getElementById('statusText');
    const params = {data};

    let time = 0;
    const cx = 400; const cy = 200; const lw = 30; // Lane width

    const colors = {{ green: '#00ff55', red: '#ff3333', yellow: '#ffaa00', road: '#2c2e33' }};

    function getPhaseInfo(t) {{
        const clr = params.clr;
        let sN=0, eN=params.gn;
        let sS=eN+clr, eS=sS+params.gs;
        let sE=eS+clr, eE=sE+params.ge;
        let sW=eE+clr, eW=sW+params.gw;
        
        if (t >= sN && t < eN) return {{dir: 'N', state: 'green', name: 'Phase 1: North Approach Flow'}};
        if (t >= eN && t < sS) return {{dir: 'N', state: 'yellow', name: 'Clearance (North)'}};
        
        if (t >= sS && t < eS) return {{dir: 'S', state: 'green', name: 'Phase 2: South Approach Flow'}};
        if (t >= eS && t < sE) return {{dir: 'S', state: 'yellow', name: 'Clearance (South)'}};
        
        if (t >= sE && t < eE) return {{dir: 'E', state: 'green', name: 'Phase 3: East Approach Flow'}};
        if (t >= eE && t < sW) return {{dir: 'E', state: 'yellow', name: 'Clearance (East)'}};
        
        if (t >= sW && t < eW) return {{dir: 'W', state: 'green', name: 'Phase 4: West Approach Flow'}};
        if (t >= eW && t < params.cycle) return {{dir: 'W', state: 'yellow', name: 'Clearance (West)'}};
        
        return {{dir: 'N', state: 'red', name: 'Cycle Reset'}};
    }}

    function getSignal(dir, t) {{
        let info = getPhaseInfo(t);
        if (info.dir === dir) return info.state;
        return 'red';
    }}

    function draw() {{
        ctx.clearRect(0,0,800,400);
        
        // Draw Roads (background)
        ctx.fillStyle = colors.road;
        ctx.fillRect(0, cy-lw*2, 800, lw*4);
        ctx.fillRect(cx-lw*2, 0, lw*4, 400);
        
        // Draw Approach Zones (Light Bars)
        // N Approach: Drives South on East half of NS road
        ctx.fillStyle = colors[getSignal('N', time)];
        ctx.fillRect(cx, 0, lw*2, cy-lw*2); 
        
        // S Approach: Drives North on West half of NS road
        ctx.fillStyle = colors[getSignal('S', time)];
        ctx.fillRect(cx-lw*2, cy+lw*2, lw*2, 400-(cy+lw*2)); 
        
        // E Approach: Drives West on South half of EW road
        ctx.fillStyle = colors[getSignal('E', time)];
        ctx.fillRect(cx+lw*2, cy, 800-(cx+lw*2), lw*2); 
        
        // W Approach: Drives East on North half of EW road
        ctx.fillStyle = colors[getSignal('W', time)];
        ctx.fillRect(0, cy-lw*2, cx-lw*2, lw*2); 

        // Draw Center Block
        ctx.fillStyle = '#111';
        ctx.fillRect(cx-lw*2, cy-lw*2, lw*4, lw*4);
        
        // Draw Free-Flow LHD Arcs
        ctx.strokeStyle = '#008833';
        ctx.lineWidth = 4;
        ctx.setLineDash([10, 10]);
        // N->E Free-flow left
        ctx.beginPath(); ctx.moveTo(cx+lw, cy-lw*2); ctx.quadraticCurveTo(cx+lw, cy-lw, cx+lw*2, cy-lw); ctx.stroke();
        // S->W Free-flow left
        ctx.beginPath(); ctx.moveTo(cx-lw, cy+lw*2); ctx.quadraticCurveTo(cx-lw, cy+lw, cx-lw*2, cy+lw); ctx.stroke();
        // E->S Free-flow left
        ctx.beginPath(); ctx.moveTo(cx+lw*2, cy+lw); ctx.quadraticCurveTo(cx+lw, cy+lw, cx+lw, cy+lw*2); ctx.stroke();
        // W->N Free-flow left
        ctx.beginPath(); ctx.moveTo(cx-lw*2, cy-lw); ctx.quadraticCurveTo(cx-lw, cy-lw, cx-lw, cy-lw*2); ctx.stroke();
        ctx.setLineDash([]);
    }}

    function loop() {{
        time += 1/60; // 60fps clock
        if (time >= params.cycle) time = 0;
        
        draw();
        
        let info = getPhaseInfo(time);
        sText.innerText = info.name + ` [${{time.toFixed(1)}}s / ${{params.cycle.toFixed(1)}}s]`;
        pBar.value = time;
        
        requestAnimationFrame(loop);
    }}
    loop();
    </script>
    """
    components.html(html_code, height=600)

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

    # 🔥 NEW: Render Abstract Phase Visualization
    render_signal_animation(gn, gs, ge, gw, cycle_time, total_clearance_time)

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