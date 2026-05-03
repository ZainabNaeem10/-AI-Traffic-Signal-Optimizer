import math

class TrafficEnvironment:
    def __init__(self, cycle_length=60, t_total_clearance=12):
        """
        Initialize a 4-phase Traffic Environment for LHD.
        Total clearance is split across 4 phases.
        """
        self.cycle_time = cycle_length
        
        # Total clearance time in one full cycle (Sum of all yellow/all-red phases)
        self.total_clearance_time = t_total_clearance
        
        # Clearance time between any two phases
        self.clearance_per_phase = t_total_clearance / 4
        
        # Simulation duration (10 minutes)
        self.simulation_duration = 600
        
        # Saturation flow: max cars that can leave per second during green
        self.rate_of_outgoing_cars = 1.67  

    def get_total_delay(self, gn, gs, ge, gw, cars_per_minute):
        """
        Calculate total delay for 4 phases: North, South, East, West.
        Implements LHD Split-Phasing logic.
        """
        # Mathematical Invariant Check
        total_time = gn + gs + ge + gw + self.total_clearance_time
        if abs(total_time - self.cycle_time) > 0.1:
            return float('inf')

        waiting_cars = {'N': 0.0, 'S': 0.0, 'E': 0.0, 'W': 0.0}
        total_wait_time = 0.0
        total_cars_arrived = 0.0

        # Sequential Green Windows (LHD Split Phasing)
        clr = self.clearance_per_phase
        
        # Window 1: North
        n_start, n_end = 0, gn
        
        # Window 2: South
        s_start = n_end + clr
        s_end = s_start + gs
        
        # Window 3: East
        e_start = s_end + clr
        e_end = e_start + ge
        
        # Window 4: West
        w_start = e_end + clr
        w_end = w_start + gw

        # Second-by-second simulation
        for current_second in range(self.simulation_duration):
            position_in_cycle = current_second % self.cycle_time

            green_states = {
                'N': n_start <= position_in_cycle < n_end,
                'S': s_start <= position_in_cycle < s_end,
                'E': e_start <= position_in_cycle < e_end,
                'W': w_start <= position_in_cycle < w_end
            }

            for direction in ['N', 'S', 'E', 'W']:
                # LHD Physics: Split demand into 80% (Straight/Right) and 20% (Free-Flow Left)
                arrival_rate_sec = cars_per_minute[direction] / 60.0
                ff_rate = arrival_rate_sec * 0.20  # 20% constant flow
                reg_rate = arrival_rate_sec * 0.80 # 80% subject to light
                
                # Update queue with 80% regulated traffic
                waiting_cars[direction] += reg_rate
                total_cars_arrived += arrival_rate_sec

                # Cars leaving: 
                # 1. 80% can leave ONLY during Green
                # 2. 20% (FF) leave regardless of light, but limited by rate
                
                outgoing = 0.0
                if green_states[direction]:
                    # Green: Regular cars leave + Free-flow cars leave
                    outgoing = self.rate_of_outgoing_cars
                else:
                    # Red: Only Free-flow cars can leave
                    outgoing = ff_rate 

                waiting_cars[direction] = max(0.0, waiting_cars[direction] - outgoing)

                # Add current queue to total delay
                total_wait_time += waiting_cars[direction]

        # Oversaturation penalty
        penalty = 0.0
        for direction in ['N', 'S', 'E', 'W']:
            arrival_rate_sec = cars_per_minute[direction] / 60.0
            max_normal_queue = arrival_rate_sec * self.cycle_time

            if waiting_cars[direction] > max_normal_queue:
                penalty += ((waiting_cars[direction] - max_normal_queue) ** 2) * 50

        # Normalized delay
        return (total_wait_time + penalty) / max(0.001, total_cars_arrived)