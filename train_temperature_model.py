import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "data/processed/pakistan_weather_features.csv"

MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# LOAD DATASET
# ============================================================

data = pd.read_csv(INPUT_FILE)


print("Dataset loaded successfully!")
print("Dataset shape:", data.shape)


# ============================================================
# CREATE NEXT-HOUR TEMPERATURE TARGET
# ============================================================

data = data.sort_values(
    by=["city", "date_time"]
).reset_index(drop=True)

data["target_temperature"] = (
    data.groupby("city")["temperature"].shift(-1)
)

data = data.dropna().reset_index(drop=True)

print("Target created successfully!")
print("Final training shape:", data.shape)


# ============================================================
# FEATURES
# ============================================================

features = [
    "temperature",
    "humidity",
    "pressure",
    "wind_speed",
    "rainfall",
    "weather_code",
    "year",
    "month",
    "day",
    "hour",
    "day_of_week",
    "temperature_lag_1",
    "humidity_lag_1",
    "pressure_lag_1",
    "wind_speed_lag_1",
    "rainfall_lag_1",
    "temperature_rolling_mean_3",
    "humidity_rolling_mean_3",
]

target = "target_temperature"


# ============================================================
# PREPARE X AND Y
# ============================================================

X = data[features]
y = data[target]

print("Features:", X.shape)
print("Target:", y.shape)


# ============================================================
# TRAIN TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))


# ============================================================
# MODELS
# ============================================================

models = {
    "Linear Regression": LinearRegression(),

    "Decision Tree": DecisionTreeRegressor(
        random_state=42,
        max_depth=20
    ),

    "Random Forest": RandomForestRegressor(
        n_estimators=30,
        random_state=42,
        n_jobs=2,
        max_depth=12,
        min_samples_leaf=2
    )

    
}


# ============================================================
# TRAIN AND EVALUATE
# ============================================================

results = []

best_model = None
best_model_name = None
best_mae = float("inf")

for model_name, model in models.items():

    print(f"\nTraining: {model_name}")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    rmse = mse ** 0.5
    r2 = r2_score(y_test, predictions)

    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2 Score: {r2:.4f}")

    results.append({
        "model": model_name,
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "R2": r2
    })

    if mae < best_mae:
        best_mae = mae
        best_model = model
        best_model_name = model_name


# ============================================================
# SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_df.to_csv(
    "data/processed/temperature_model_comparison.csv",
    index=False
)


# ============================================================
# SAVE BEST MODEL
# ============================================================

model_path = os.path.join(
    MODEL_DIR,
    "temperature_model.pkl"
)

features_path = os.path.join(
    MODEL_DIR,
    "model_features.pkl"
)

joblib.dump(best_model, model_path)
joblib.dump(features, features_path)


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 60)
print("TEMPERATURE MODEL TRAINING COMPLETED")
print("=" * 60)

print("Best model:", best_model_name)
print(f"Best MAE: {best_mae:.4f}")

print("Model saved:", model_path)
print("Features saved:", features_path)

print("Comparison saved:")
print("data/processed/temperature_model_comparison.csv")

print("=" * 60)