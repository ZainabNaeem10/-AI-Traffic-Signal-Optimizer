import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

df = pd.read_csv("traffic_data.csv")

X = df[["time", "day"]]
y = df[["N", "S", "E", "W"]]

model = RandomForestRegressor()
model.fit(X, y)

joblib.dump(model, "traffic_model.pkl")

print("Model trained and saved!")