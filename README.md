# AI Signal Time Optimizer (4-Phase LHD Split-Phasing)

This project is a high-fidelity **Traffic Signal Optimization System** designed for Left-Hand Drive (LHD) environments. It utilizes AI search heuristics to minimize vehicular delay at a four-way intersection by dynamically optimizing the green time distribution across four distinct phases.

---

## Features
- **4-Phase Split-Phasing**: Dynamically optimizes green windows for North, South, East, and West directions.
- **LHD Physics Integration**: Implements "Free-Flow Left" logic where 20% of traffic bypasses the red-light queue, reflecting real-world LHD movement patterns.
- **AI Search Suite**: Includes three optimization strategies:
  - **Simulated Annealing (SA)**: Global search with Metropolis Criterion.
  - **Hill Climbing (HC)**: Fast, greedy local optimization.
  - **Genetic Algorithm (GA)**: Population-based evolutionary optimization.
- **ML Traffic Prediction**: Uses a RandomForest model to predict traffic demand based on the Time of Day and Day Type (Weekday/Weekend).
- **Real-time Simulation**: A 600-second point-queue simulation engine validates timings and calculates the Average Vehicular Delay (AVD).
- **Live Signal Visualizer**: A real-time, bird's-eye animated intersection display showing active signal phases, traffic flow states, and LHD free-flow left-turn logic.

---

## Live 4-Phase Signal Visualizer

The dashboard includes an embedded **real-time graphical signal visualizer** rendered as an animated top-down view of the intersection.

### What It Shows
- A **cross-shaped intersection layout** representing the North-South and East-West road corridors.
- **Color-coded lane bands** that animate in sync with the current signal phase:
  | Color | Meaning |
  |---|---|
  | 🟩 Green | Phase is active — traffic is flowing |
  | 🟧 Yellow | Clearance phase — traffic is slowing |
  | 🟥 Red | Phase is stopped — vehicles are queued |
- A **dashed green arc** in the center box that activates during permissive phases to indicate the **Free-Flow Left (LHD)** movement is available.

### How It Works
The visualizer reads the current phase state from the simulation engine in real time and updates each directional lane band accordingly. At any moment, only non-conflicting directions are shown as green, accurately reflecting the 4-phase split logic enforced by the optimizer.

### Graphical Output (Sample)
> *Figure: Live 4-Phase Signal Visualizer — Bird's-eye view. West approach: Green (flowing). North, South, East approaches: Red (stopped). Dashed arc indicates active Free-Flow Left turn permission.*

This component serves as the primary **graphical output** of the system, providing visual confirmation that the optimized signal timings are being applied correctly across all four phases.

---

## Execution Instructions and Dependencies

### 1. Required Packages
Install the necessary dependencies via pip:
```bash
pip install -r requirements.txt
```

### 2. How to Run
1. Navigate to the project directory in your terminal.
2. Execute the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. The dashboard will open at `http://localhost:8501`.
4. The **Live Signal Visualizer** panel will animate automatically as the simulation runs.

---

## Sample Metrics & Results
- **Optimized Phases**: N(12s), S(12s), E(14s), W(10s)
- **Baseline**: Comparison against an "Equal Split" (25% per phase) plan.
- **Delay Reduction**: Typically ranges from 10% to 30% depending on traffic congestion levels.
- **Mathematical Invariant**: Ensures $g_N + g_S + g_E + g_W + \text{Clearance} = \text{Cycle Length}$.

---

## Technical Implementation Details

### Simulation Engine (`traffic_engine.py`)
- **Point-Queue Model**: Tracks car arrivals and departures second-by-second.
- **Oversaturation Penalty**: Implements a squared penalty ($excess^2 \times 50$) to prevent massive queue build-ups in any single direction.
- **Normalized Delay**: Calculates the Average Vehicular Delay (AVD) as the primary fitness metric.

### Optimization Layer (`optimizer.py`)
- **4D State Space**: Searches the vector $[g_N, g_S, g_E, g_W]$.
- **Constraint Handling**: Enforces a minimum 10s green time per phase and maintains the total cycle sum during neighbor generation and mutation.

### ML Component
- **RandomForestRegressor**: Predicts the `cars_per_minute` demand for each direction, allowing the AI to optimize for predicted future peaks rather than just current values.

### Visualizer Component (`app.py`)
- **Rendered via Streamlit**: The signal visualizer is built using Streamlit's layout and custom HTML/CSS components, embedded directly in the dashboard.
- **Phase-Driven State**: Each lane band's color is driven by the live phase variable output from `traffic_engine.py`, ensuring the visual is always in sync with the simulation state.
- **LHD Arc Rendering**: The free-flow left turn arc is toggled on/off based on whether the current phase permits unprotected left turns under LHD rules.

---

## Project Structure
- `app.py`: Streamlit dashboard, UI logic, and Live Signal Visualizer rendering.
- `traffic_engine.py`: Simulation environment and delay calculation.
- `optimizer.py`: AI Search algorithms (SA, HC, GA).
- `generate_data.py`: Synthetic traffic data generator.
- `train_model.py`: ML training script.
- `traffic_model.pkl`: Serialized ML weights.
- `requirements.txt`: Project dependencies.