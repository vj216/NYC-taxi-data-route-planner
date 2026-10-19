import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

DATA = os.path.join("data","trips_sample.parquet")
MODEL = os.path.join("data","travel_time_model.pkl")

df = pd.read_parquet(DATA)

df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"])
df["pickup_hour"] = df["pickup_datetime"].dt.hour
df["pickup_dayofweek"] = df["pickup_datetime"].dt.dayofweek

df = df[
    (df["duration_min"]>=1.0) & (df["duration_min"]<=180.0) & (df["trip_miles"]>0.1) & (df["trip_miles"]<50.0)
].dropna()


features = ["trip_miles", "pickup_hour", "pickup_dayofweek","PULocationID", "DOLocationID"]
target = "duration_min"

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=50, max_depth=12, n_jobs =-1,random_state=42)
model.fit(X_train, y_train)

#evaluate
preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
r2 = r2_score(y_test, preds)

print(f"MAE: {mae:.2f} minutes")
print(f"Model R square score: {r2:.3f}")

joblib.dump(model,MODEL)
print(f"Saved to {MODEL}")

