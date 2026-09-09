import requests
import pandas as pd
import joblib
from datetime import datetime


# ==========================================
# 1. LOAD TRAINED MODEL
# ==========================================

model = joblib.load("models/weather_prediction_model.pkl")

features = joblib.load("models/model_features.pkl")

print("Model loaded successfully!")


# ==========================================
# 2. ISLAMABAD COORDINATES
# ==========================================

latitude = 33.6844
longitude = 73.0479


# ==========================================
# 3. GET LIVE WEATHER DATA
# ==========================================

url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    "&current=temperature_2m,relative_humidity_2m,"
    "surface_pressure,wind_speed_10m,precipitation,weather_code"
)

response = requests.get(url)

response.raise_for_status()

data = response.json()

current = data["current"]

print("\nLive weather data received successfully!")


# ==========================================
# 4. CURRENT DATE AND TIME
# ==========================================

now = datetime.now()


# ==========================================
# 5. CREATE INPUT DATA
# ==========================================

input_data = pd.DataFrame([{
    "temperature": current["temperature_2m"],
    "humidity": current["relative_humidity_2m"],
    "pressure": current["surface_pressure"],
    "wind_speed": current["wind_speed_10m"],
    "rainfall": current["precipitation"],
    "weather_code": current["weather_code"],

    "year": now.year,
    "month": now.month,
    "day": now.day,
    "hour": now.hour,
    "day_of_week": now.weekday(),

    # Temporary values for lag features
    "temperature_lag_1": current["temperature_2m"],
    "humidity_lag_1": current["relative_humidity_2m"],
    "pressure_lag_1": current["surface_pressure"],
    "wind_speed_lag_1": current["wind_speed_10m"],
    "rainfall_lag_1": current["precipitation"],

    # Temporary values for rolling averages
    "temperature_rolling_mean_3": current["temperature_2m"],
    "humidity_rolling_mean_3": current["relative_humidity_2m"]
}])


# ==========================================
# 6. ARRANGE FEATURES
# ==========================================

input_data = input_data[features]


# ==========================================
# 7. MAKE PREDICTION
# ==========================================

prediction = model.predict(input_data)

predicted_temperature = prediction[0]


# ==========================================
# 8. DISPLAY RESULTS
# ==========================================

print("\n===================================")
print("       WEATHER PREDICTION")
print("===================================")

print("Current Temperature:",
      current["temperature_2m"], "°C")

print("Current Humidity:",
      current["relative_humidity_2m"], "%")

print("Current Pressure:",
      current["surface_pressure"], "hPa")

print("Current Wind Speed:",
      current["wind_speed_10m"], "km/h")

print("Current Rainfall:",
      current["precipitation"], "mm")

print("\nPredicted Next Hour Temperature:")

print(round(predicted_temperature, 2), "°C")

print("===================================")