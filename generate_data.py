import pandas as pd
import random
from traffic_engine import TrafficEnvironment
from optimizer import SimulatedAnnealing

data = []

env = TrafficEnvironment()

for _ in range(300):  # generate 300 samples

    # Features
    time_of_day = random.randint(0, 23)
    day_type = random.choice([0, 1])  # 0 = weekday, 1 = weekend

    # Simulated traffic pattern (IMPORTANT LOGIC)
    base = 10

    if 7 <= time_of_day <= 9 or 17 <= time_of_day <= 19:
        base += 20  # rush hour

    if day_type == 1:
        base -= 5  # weekends less traffic

    cars = {
        'N': max(5, base + random.randint(-5, 5)),
        'S': max(5, base + random.randint(-5, 5)),
        'E': max(5, base + random.randint(-5, 5)),
        'W': max(5, base + random.randint(-5, 5)),
    }

    optimizer = SimulatedAnnealing(env, cars)
    ns, ew, delay = optimizer.optimize()

    data.append([
        time_of_day, day_type,
        cars['N'], cars['S'], cars['E'], cars['W']
    ])

    print(f"Sample {_} generated")

df = pd.DataFrame(data, columns=[
    "time", "day",
    "N", "S", "E", "W"
])

df.to_csv("traffic_data.csv", index=False)
print("Dataset generated!")