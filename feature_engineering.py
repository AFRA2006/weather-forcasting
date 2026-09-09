import os
import pandas as pd

# ============================================================
# 1. FILE PATHS
# ============================================================

INPUT_FILE = "data/processed/pakistan_weather_cleaned.csv"
OUTPUT_FILE = "data/processed/pakistan_weather_features.csv"

os.makedirs("data/processed", exist_ok=True)

# ============================================================
# 2. LOAD DATASET
# ============================================================

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"\nPakistan dataset nahi mili:\n{INPUT_FILE}\n\n"
        "Pehle Pakistan historical dataset create karein."
    )

df = pd.read_csv(INPUT_FILE)

print("Dataset loaded successfully!")
print("Original shape:", df.shape)
print("Original columns:", df.columns.tolist())

# ============================================================
# 3. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "city",
    "date_time",
    "temperature",
    "humidity",
    "pressure",
    "wind_speed",
    "rainfall",
    "weather_code",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"\nRequired columns missing hain: {missing_columns}\n"
        f"Available columns: {df.columns.tolist()}"
    )

# ============================================================
# 4. CONVERT DATE AND SORT CITY-WISE
# ============================================================

df["date_time"] = pd.to_datetime(df["date_time"])

df = df.sort_values(
    by=["city", "date_time"]
).reset_index(drop=True)

# ============================================================
# 5. CREATE DATE/TIME FEATURES
# ============================================================

df["year"] = df["date_time"].dt.year
df["month"] = df["date_time"].dt.month
df["day"] = df["date_time"].dt.day
df["hour"] = df["date_time"].dt.hour
df["day_of_week"] = df["date_time"].dt.dayofweek

# ============================================================
# 6. CREATE CITY-WISE LAG FEATURES
# ============================================================

grouped = df.groupby("city", group_keys=False)

df["temperature_lag_1"] = grouped["temperature"].shift(1)
df["humidity_lag_1"] = grouped["humidity"].shift(1)
df["pressure_lag_1"] = grouped["pressure"].shift(1)
df["wind_speed_lag_1"] = grouped["wind_speed"].shift(1)
df["rainfall_lag_1"] = grouped["rainfall"].shift(1)

# ============================================================
# 7. CREATE CITY-WISE ROLLING FEATURES
# ============================================================

df["temperature_rolling_mean_3"] = (
    grouped["temperature"]
    .rolling(window=3, min_periods=3)
    .mean()
    .reset_index(level=0, drop=True)
)

df["humidity_rolling_mean_3"] = (
    grouped["humidity"]
    .rolling(window=3, min_periods=3)
    .mean()
    .reset_index(level=0, drop=True)
)

# ============================================================
# 8. REMOVE MISSING VALUES
# ============================================================

df.dropna(inplace=True)
df.reset_index(drop=True, inplace=True)

# ============================================================
# 9. DISPLAY INFORMATION
# ============================================================

print("\nFeature engineering completed!")
print("Final shape:", df.shape)

print("\nCities in dataset:")
print(df["city"].unique())

print("\nRows per city:")
print(df["city"].value_counts())

print("\nFinal columns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

# ============================================================
# 10. SAVE DATASET
# ============================================================

df.to_csv(OUTPUT_FILE, index=False)

print("\nPakistan feature dataset saved successfully!")
print("File:", OUTPUT_FILE)