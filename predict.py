import os
import joblib
import pandas as pd

from weather_api import get_weather_by_city


# ============================================================
# FILE PATHS
# ============================================================

MODEL_PATH = "models/temperature_model.pkl"
FEATURES_PATH = "models/model_features.pkl"
DATASET_PATH = "data/processed/pakistan_weather_cleaned.csv"


# ============================================================
# LOAD MODEL AND FEATURES
# ============================================================

def load_temperature_model():

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Temperature model not found: {MODEL_PATH}"
        )

    if not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError(
            f"Model features not found: {FEATURES_PATH}"
        )

    model = joblib.load(MODEL_PATH)
    model_features = joblib.load(FEATURES_PATH)

    return model, model_features


# ============================================================
# LOAD AVAILABLE CITIES FROM DATASET
# ============================================================

def get_available_cities():

    if not os.path.exists(DATASET_PATH):
        return []

    try:
        df = pd.read_csv(
            DATASET_PATH,
            usecols=["city"]
        )

        cities = (
            df["city"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        return sorted(cities)

    except Exception as error:
        print(f"Error loading city list: {error}")
        return []


# ============================================================
# FIND CITY NAME
# ============================================================

def find_dataset_city(city_name):

    available_cities = get_available_cities()

    if not available_cities:
        return city_name.strip()

    city_name = city_name.strip().lower()

    for city in available_cities:

        if city.lower() == city_name:
            return city

    for city in available_cities:

        if city_name in city.lower():
            return city

    return None


# ============================================================
# CREATE MODEL INPUT
# ============================================================

def create_prediction_input(weather, model_features):

    current_time = pd.Timestamp.now()

    temperature = float(weather["temperature"])
    humidity = float(weather["humidity"])
    pressure = float(weather["pressure"])
    wind_speed = float(weather["wind_speed"])
    rainfall = float(weather["rainfall"])

    input_data = {
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": wind_speed,
        "rainfall": rainfall,

        "year": current_time.year,
        "month": current_time.month,
        "day": current_time.day,
        "hour": current_time.hour,
        "day_of_week": current_time.dayofweek,

        # Temporary lag values
        "temperature_lag_1": temperature,
        "humidity_lag_1": humidity,
        "pressure_lag_1": pressure,
        "wind_speed_lag_1": wind_speed,
        "rainfall_lag_1": rainfall,

        # Temporary rolling values
        "temperature_rolling_3": temperature,
        "humidity_rolling_3": humidity,
    }

    input_df = pd.DataFrame([input_data])

    # Add any missing model features with zero
    for feature in model_features:

        if feature not in input_df.columns:
            input_df[feature] = 0

    # Keep only the features used during training
    input_df = input_df[model_features]

    return input_df


# ============================================================
# PREDICT NEXT-HOUR TEMPERATURE
# ============================================================

def predict_temperature(city_name):

    # Check city in dataset
    dataset_city = find_dataset_city(city_name)

    if dataset_city is None:

        print(
            f"City '{city_name}' is not available in the dataset."
        )

        return None

    # Load model
    model, model_features = load_temperature_model()

    # Get live weather
    weather = get_weather_by_city(dataset_city)

    if weather is None:

        print(
            f"Live weather data not found for {dataset_city}."
        )

        return None

    # Create model input
    input_df = create_prediction_input(
        weather,
        model_features
    )

    # Make prediction
    predicted_temperature = model.predict(input_df)[0]

    predicted_temperature = float(predicted_temperature)

    current_temperature = float(
        weather["temperature"]
    )

    temperature_change = (
        predicted_temperature - current_temperature
    )

    return {
        "city": weather["city"],
        "current_temperature": current_temperature,
        "predicted_temperature": predicted_temperature,
        "temperature_change": temperature_change,
        "humidity": weather["humidity"],
        "pressure": weather["pressure"],
        "wind_speed": weather["wind_speed"],
        "rainfall": weather["rainfall"],
        "time": weather["time"],
        "latitude": weather["latitude"],
        "longitude": weather["longitude"],
    }


# ============================================================
# TEST ALL DATASET CITIES
# ============================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("PAKISTAN WEATHER TEMPERATURE PREDICTION")
    print("==========================================")

    available_cities = get_available_cities()

    print(
        f"\nDataset mein available cities: "
        f"{len(available_cities)}"
    )

    print("\nAvailable cities:")

    for index, city in enumerate(available_cities, start=1):
        print(f"{index}. {city}")

    city = input(
        "\nEnter city name for prediction: "
    ).strip()

    if city == "":
        print("City name cannot be empty.")

    else:

        try:

            result = predict_temperature(city)

            if result:

                print("\n==========================================")
                print("PREDICTION RESULT")
                print("==========================================")

                print(
                    f"City: {result['city']}"
                )

                print(
                    f"Current Temperature: "
                    f"{result['current_temperature']:.2f} °C"
                )

                print(
                    f"Predicted Next Hour: "
                    f"{result['predicted_temperature']:.2f} °C"
                )

                print(
                    f"Expected Change: "
                    f"{result['temperature_change']:+.2f} °C"
                )

                print(
                    f"Humidity: "
                    f"{result['humidity']} %"
                )

                print(
                    f"Pressure: "
                    f"{result['pressure']} hPa"
                )

                print(
                    f"Wind Speed: "
                    f"{result['wind_speed']} km/h"
                )

                print(
                    f"Rainfall: "
                    f"{result['rainfall']} mm"
                )

            else:

                print(
                    "\nPrediction could not be generated."
                )

        except Exception as error:

            print(
                f"\nPrediction error: {error}"
            )