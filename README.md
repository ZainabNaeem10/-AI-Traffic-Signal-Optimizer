# AI Signal Time Optimizer

This project optimizes traffic signal timings for a two-phase intersection (North-South and East-West).  
We use Simulated Annealing (SA) to reduce average waiting time better than fixed equal-split plans.  
Hill Climbing (HC) is the baseline.  
Genetic Algorithm (GA) for comparisons
A 600-second point-queue simulation calculates delay.  
Inputs and results are handled through a Streamlit app.

# Execution Instructions and Dependencies

## Required Packages
Run this command once to install everything:

pip install -r requirements.txt

## How to Run
1. Open terminal or VS Code in the project folder.
2. Type this command:

streamlit run app.py

3. Browser opens the app at localhost:8501.
4. Use sliders to set values. Click Run AI Optimization. See results.

# Sample Input / Output Demonstrations

## Sample Input (sidebar sliders in Streamlit)
Cycle Length: 60 seconds  
Clearance (Yellow + All-Red): 6 seconds  
(Other sliders: Demand values you used — e.g., North 15, South 12, East 10, West 8 vehicles per minute — note them if you remember)

Click "Run AI Optimization" button after setting sliders.

Sliders to select type of technique to visualize:
Simmulated Annealing
Genetic Algorithm
Hill Climbing

## Sample Output (real results from the app)
Optimized NS Green Time: 16 seconds  
Optimized EW Green Time: 38 seconds  
Delay Reduction: 11.8 percent  

Check formula displayed: NS(16) + EW(38) + Clearance(6) = 60s (Cycle: 60s)  

Bar chart shows:  
AI Optimized delay (lower)  
Equal Split delay (higher)  

Runtime: around 10-20 seconds (depends on laptop)


# Brief Technical Overview of Implementation Approach

Streamlit (app.py) collects inputs. Demand per direction, cycle length, clearance time.
Simulation (traffic_engine.py) runs 600-second time-stepped point-queue model. FIFO queues, per-second updates, computes delay.
Optimization (optimizer.py) uses Simulated Annealing. Starts with random feasible timings. Creates neighbors with small changes to green times. Evaluates delay. Accepts or rejects with Metropolis criterion. Cools temperature. Stops at max 2000 iterations.
Hill Climbing runs as greedy baseline for comparison.
Equal-split baseline divides cycle minus clearance equally.
Genetic Algorithm is used with muatations,crossover and populations.
Output shows timings, reduction percentage, metrics, matplotlib charts in Streamlit.
Simple ML (linear regression or clustering) predicts traffic patterns from simulated data to guide scenarios.

Only SA and HC (local search methods) are used. Runs offline with user inputs. No sensors.

# Files
app.py Streamlit interface
traffic_engine.py simulation
optimizer.py SA, GA and HC code

