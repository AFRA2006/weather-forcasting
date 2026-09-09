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
# 100+ PAKISTANI CITIES
# ============================================================

CITIES = {
    # Punjab
    "Lahore": (31.5204, 74.3587),
    "Faisalabad": (31.4504, 73.1350),
    "Rawalpindi": (33.5651, 73.0169),
    "Gujranwala": (32.1877, 74.1945),
    "Multan": (30.1575, 71.5249),
    "Sargodha": (32.0836, 72.6711),
    "Bahawalpur": (29.3956, 71.6836),
    "Sahiwal": (30.6682, 73.1114),
    "Sheikhupura": (31.7167, 73.9850),
    "Jhang": (31.2781, 72.3118),
    "Gujrat": (32.5736, 74.0780),
    "Kasur": (31.1150, 74.4467),
    "Rahim Yar Khan": (28.4202, 70.2952),
    "Dera Ghazi Khan": (30.0561, 70.6348),
    "Wah Cantt": (33.7700, 72.7500),
    "Muridke": (31.8020, 74.2570),
    "Hafizabad": (32.0709, 73.6880),
    "Khanewal": (30.3017, 71.9321),
    "Muzaffargarh": (30.0703, 71.1933),
    "Lodhran": (29.5405, 71.6336),
    "Pakpattan": (30.3410, 73.3866),
    "Okara": (30.8081, 73.4458),
    "Chiniot": (31.7200, 72.9789),
    "Mianwali": (32.5839, 71.5370),
    "Bhakkar": (31.6252, 71.0657),
    "Khushab": (32.2967, 72.3525),
    "Attock": (33.7660, 72.3609),
    "Jhelum": (32.9425, 73.7257),
    "Chakwal": (32.9336, 72.8634),
    "Nankana Sahib": (31.4500, 73.7000),
    "Toba Tek Singh": (30.9697, 72.4827),
    "Vehari": (30.0419, 72.3528),
    "Burewala": (30.1667, 72.6500),
    "Jalalpur Jattan": (32.6419, 74.2050),
    "Mandi Bahauddin": (32.5861, 73.4917),
    "Narowal": (32.1000, 74.8833),
    "Shakargarh": (32.2646, 75.1608),
    "Kot Addu": (30.4691, 70.9670),

    # Sindh
    "Karachi": (24.8607, 67.0011),
    "Hyderabad": (25.3960, 68.3578),
    "Sukkur": (27.7052, 68.8574),
    "Larkana": (27.5590, 68.2120),
    "Nawabshah": (26.2442, 68.4100),
    "Mirpur Khas": (25.5251, 69.0159),
    "Jacobabad": (28.2819, 68.4388),
    "Shikarpur": (27.9556, 68.6382),
    "Dadu": (26.7319, 67.7750),
    "Thatta": (24.7475, 67.9235),
    "Badin": (24.6550, 68.8380),
    "Tando Adam": (25.7687, 68.6617),
    "Tando Allahyar": (25.4605, 68.7170),
    "Khairpur": (27.5295, 68.7592),
    "Ghotki": (28.0064, 69.3161),
    "Kandhkot": (28.2450, 69.1800),
    "Matiari": (25.5970, 68.4467),
    "Umerkot": (25.3614, 69.7361),

    # Khyber Pakhtunkhwa
    "Peshawar": (34.0151, 71.5249),
    "Mardan": (34.1989, 72.0407),
    "Abbottabad": (34.1688, 73.2215),
    "Mingora": (34.7717, 72.3600),
    "Kohat": (33.5869, 71.4429),
    "Bannu": (32.9853, 70.6042),
    "Dera Ismail Khan": (31.8327, 70.9019),
    "Nowshera": (34.0159, 72.0058),
    "Charsadda": (34.1482, 71.7406),
    "Swabi": (34.1202, 72.4698),
    "Mansehra": (34.3300, 73.2000),
    "Haripur": (33.9942, 72.9340),
    "Chitral": (35.8518, 71.7864),
    "Dir": (35.2058, 71.8767),
    "Timergara": (34.8266, 71.8440),
    "Karak": (33.1167, 71.0833),
    "Tank": (32.2167, 70.3833),
    "Hangu": (33.5311, 71.0597),
    "Lakki Marwat": (32.6070, 70.9114),
    "Batkhela": (34.6167, 71.9667),

    # Balochistan
    "Quetta": (30.1798, 66.9750),
    "Gwadar": (25.1264, 62.3225),
    "Turbat": (26.0023, 63.0485),
    "Khuzdar": (27.8000, 66.6167),
    "Chaman": (30.9177, 66.4597),
    "Sibi": (29.5430, 67.8773),
    "Zhob": (31.3417, 69.4486),
    "Loralai": (30.3705, 68.5979),
    "Kalat": (29.0266, 66.5936),
    "Nushki": (29.5522, 66.0225),
    "Dalbandin": (28.8885, 64.4062),
    "Pasni": (25.2631, 63.4710),
    "Ormara": (25.2088, 64.6357),
    "Mastung": (29.7997, 66.8455),

    # Islamabad and Rawalpindi region
    "Islamabad": (33.6844, 73.0479),
    "Murree": (33.9073, 73.3903),
    "Taxila": (33.7463, 72.8397),
    "Kahuta": (33.5917, 73.3875),
    "Kallar Syedan": (33.4167, 73.3833),

    # Gilgit-Baltistan
    "Gilgit": (35.9208, 74.3083),
    "Skardu": (35.2971, 75.6333),
    "Chilas": (35.4206, 74.0967),
    "Hunza": (36.3167, 74.6500),
    "Gupis": (36.1667, 73.4333),
    "Khaplu": (35.1333, 76.3333),

    # Azad Jammu and Kashmir
    "Muzaffarabad": (34.3700, 73.4711),
    "Mirpur": (33.1483, 73.7517),
    "Rawalakot": (33.8578, 73.7604),
    "Kotli": (33.5184, 73.9022),
    "Bagh": (33.9861, 73.9478),
    "Bhimber": (32.9747, 74.0780),
}


# ============================================================
# DOWNLOAD WEATHER DATA FOR ONE CITY
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

    response = requests.get(url, params=params, timeout=120)

    if response.status_code != 200:
        print(f"❌ Failed: {city_name}")
        print(response.text[:500])
        return None

    result = response.json()

    if "hourly" not in result:
        print(f"❌ Hourly data not available: {city_name}")
        return None

    hourly = result["hourly"]

    dataframe = pd.DataFrame({
        "date_time": hourly["time"],
        "temperature": hourly["temperature_2m"],
        "humidity": hourly["relative_humidity_2m"],
        "pressure": hourly["surface_pressure"],
        "wind_speed": hourly["wind_speed_10m"],
        "rainfall": hourly["precipitation"],
        "weather_code": hourly["weather_code"],
    })

    dataframe["city"] = city_name
    dataframe["latitude"] = latitude
    dataframe["longitude"] = longitude

    dataframe = dataframe[
        [
            "city",
            "date_time",
            "temperature",
            "humidity",
            "pressure",
            "wind_speed",
            "rainfall",
            "weather_code",
            "latitude",
            "longitude",
        ]
    ]

    print(f"✅ {city_name}: {len(dataframe)} rows")

    return dataframe


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    all_city_data = []

    total_cities = len(CITIES)

    print("=" * 60)
    print("PAKISTAN COMPLETE WEATHER DATA COLLECTION")
    print("=" * 60)
    print(f"Total cities: {total_cities}")
    print(f"Date range: {START_DATE} to {END_DATE}")
    print("=" * 60)

    for index, (city_name, coordinates) in enumerate(CITIES.items(), start=1):
        latitude, longitude = coordinates

        print(f"\n[{index}/{total_cities}] Processing {city_name}")

        try:
            city_data = download_city_weather(
                city_name,
                latitude,
                longitude
            )

            if city_data is not None:
                all_city_data.append(city_data)

        except requests.exceptions.RequestException as error:
            print(f"❌ Internet/API error for {city_name}: {error}")

        except Exception as error:
            print(f"❌ Error for {city_name}: {error}")

        # API ko overload hone se bachane ke liye
        time.sleep(1)

    if not all_city_data:
        print("\n❌ Koi dataset create nahi hua.")
        return

    final_dataframe = pd.concat(
        all_city_data,
        ignore_index=True
    )

    final_dataframe["date_time"] = pd.to_datetime(
        final_dataframe["date_time"]
    )

    final_dataframe = final_dataframe.sort_values(
        by=["city", "date_time"]
    ).reset_index(drop=True)

    final_dataframe.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 60)
    print("DATASET CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"Total cities downloaded: {final_dataframe['city'].nunique()}")
    print(f"Total rows: {len(final_dataframe)}")
    print(f"Dataset shape: {final_dataframe.shape}")
    print(f"Saved file: {OUTPUT_FILE}")
    print("=" * 60)

    print("\nRows per city:")
    print(final_dataframe["city"].value_counts().sort_index())


if __name__ == "__main__":
    main()