import os
import time
import requests
import pandas as pd


# ============================================================
# SETTINGS
# ============================================================

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

OUTPUT_FILE = "data/processed/pakistan_weather_cleaned.csv"

os.makedirs("data/processed", exist_ok=True)


# ============================================================
# REMAINING 16 CITIES
# ============================================================

CITIES = {
    "Murree": (33.9073, 73.3903),
    "Taxila": (33.7463, 72.8397),
    "Kahuta": (33.5917, 73.3875),
    "Kallar Syedan": (33.4167, 73.3833),

    "Gilgit": (35.9208, 74.3083),
    "Skardu": (35.2971, 75.6333),
    "Chilas": (35.4206, 74.0967),
    "Hunza": (36.3167, 74.6500),
    "Gupis": (36.1667, 73.4333),
    "Khaplu": (35.1333, 76.3333),

    "Muzaffarabad": (34.3700, 73.4711),
    "Mirpur": (33.1483, 73.7517),
    "Rawalakot": (33.8578, 73.7604),
    "Kotli": (33.5184, 73.9022),
    "Bagh": (33.9861, 73.9478),
    "Bhimber": (32.9747, 74.0780),
}


# ============================================================
# DOWNLOAD ONE CITY
# ============================================================

def download_city_weather(city_name, latitude, longitude):

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "surface_pressure,"
            "wind_speed_10m,"
            "precipitation,"
            "weather_code"
        ),
        "timezone": "Asia/Karachi",
    }

    print(f"\nDownloading: {city_name}")

    try:

        response = requests.get(
            url,
            params=params,
            timeout=120
        )

    except requests.exceptions.RequestException as error:

        print(f"❌ Request error for {city_name}: {error}")
        return None

    if response.status_code != 200:

        print(f"❌ Failed: {city_name}")
        print(response.text[:300])

        return None

    result = response.json()

    if "hourly" not in result:

        print(f"❌ Hourly data unavailable: {city_name}")

        return None

    hourly = result["hourly"]

    dataframe = pd.DataFrame({
        "city": city_name,
        "date_time": hourly["time"],
        "temperature": hourly["temperature_2m"],
        "humidity": hourly["relative_humidity_2m"],
        "pressure": hourly["surface_pressure"],
        "wind_speed": hourly["wind_speed_10m"],
        "rainfall": hourly["precipitation"],
        "weather_code": hourly["weather_code"],
        "latitude": latitude,
        "longitude": longitude,
    })

    print(
        f"✅ {city_name}: "
        f"{len(dataframe)} rows downloaded"
    )

    return dataframe


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("UPDATING PAKISTAN WEATHER DATASET")
    print("=" * 60)

    # --------------------------------------------------------
    # CHECK EXISTING FILE
    # --------------------------------------------------------

    if not os.path.exists(OUTPUT_FILE):

        print("\n❌ Existing dataset not found!")
        print(f"Expected: {OUTPUT_FILE}")

        return

    # --------------------------------------------------------
    # LOAD EXISTING DATA
    # --------------------------------------------------------

    existing_dataframe = pd.read_csv(
        OUTPUT_FILE
    )

    existing_cities = set(
        existing_dataframe["city"].unique()
    )

    print(
        f"\nExisting cities: "
        f"{len(existing_cities)}"
    )

    print(
        f"Existing rows: "
        f"{len(existing_dataframe)}"
    )

    # --------------------------------------------------------
    # FIND WHICH OF THE 16 CITIES ARE STILL MISSING
    # --------------------------------------------------------

    missing_cities = {
        city: coordinates
        for city, coordinates in CITIES.items()
        if city not in existing_cities
    }

    print(
        f"\nRemaining missing cities: "
        f"{len(missing_cities)}"
    )

    if not missing_cities:

        print("\n🎉 All 107 cities are already present!")

        print(
            f"Total cities: "
            f"{existing_dataframe['city'].nunique()}"
        )

        print(
            f"Total rows: "
            f"{len(existing_dataframe)}"
        )

        return

    print("\nCities still missing:")

    for city in missing_cities:

        print(f" - {city}")

    # --------------------------------------------------------
    # DOWNLOAD ONLY MISSING CITIES
    # --------------------------------------------------------

    new_city_data = []

    for index, (city_name, coordinates) in enumerate(
        missing_cities.items(),
        start=1
    ):

        latitude, longitude = coordinates

        print("\n" + "-" * 60)

        print(
            f"[{index}/{len(missing_cities)}] "
            f"{city_name}"
        )

        city_data = download_city_weather(
            city_name,
            latitude,
            longitude
        )

        if city_data is not None:

            new_city_data.append(
                city_data
            )

        # Delay between API requests
        print("Waiting 3 seconds...")
        time.sleep(3)

    # --------------------------------------------------------
    # IF NOTHING DOWNLOADED
    # --------------------------------------------------------

    if not new_city_data:

        print(
            "\n❌ No new city data was downloaded."
        )

        print(
            "API limit may still be active."
        )

        return

    # --------------------------------------------------------
    # COMBINE NEW DATA
    # --------------------------------------------------------

    new_dataframe = pd.concat(
        new_city_data,
        ignore_index=True
    )

    print("\nNew data downloaded:")

    print(
        f"Cities: "
        f"{new_dataframe['city'].nunique()}"
    )

    print(
        f"Rows: "
        f"{len(new_dataframe)}"
    )

    # --------------------------------------------------------
    # COMBINE OLD + NEW
    # --------------------------------------------------------

    final_dataframe = pd.concat(
        [
            existing_dataframe,
            new_dataframe
        ],
        ignore_index=True
    )

    # --------------------------------------------------------
    # FIX DATETIME
    # --------------------------------------------------------

    final_dataframe["date_time"] = pd.to_datetime(
        final_dataframe["date_time"],
        format="mixed"
    )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    before_duplicates = len(
        final_dataframe
    )

    final_dataframe = final_dataframe.drop_duplicates(
        subset=[
            "city",
            "date_time"
        ]
    )

    after_duplicates = len(
        final_dataframe
    )

    print(
        f"\nDuplicates removed: "
        f"{before_duplicates - after_duplicates}"
    )

    # --------------------------------------------------------
    # SORT DATA
    # --------------------------------------------------------

    final_dataframe = final_dataframe.sort_values(
        by=[
            "city",
            "date_time"
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # SAVE FINAL DATASET
    # --------------------------------------------------------

    final_dataframe.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("✅ DATASET UPDATED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"Total cities: "
        f"{final_dataframe['city'].nunique()}"
    )

    print(
        f"Total rows: "
        f"{len(final_dataframe)}"
    )

    print(
        f"Dataset shape: "
        f"{final_dataframe.shape}"
    )

    print(
        f"Saved file: "
        f"{OUTPUT_FILE}"
    )

    print("=" * 60)

    print("\nRows per city:")

    print(
        final_dataframe[
            "city"
        ].value_counts().sort_index()
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()