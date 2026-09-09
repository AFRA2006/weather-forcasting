
import requests
from urllib.parse import quote


# ============================================================
# CITY SEARCH
# ============================================================

def search_city(city_name="Islamabad"):
    """
    Pakistani city ka naam lekar coordinates return karta hai.
    Default city = Islamabad
    """

    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={quote(city_name)}"
        "&count=10"
        "&language=en"
        "&format=json"
        "&countryCode=PK"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            return None

        city = results[0]

        return {
            "name": city.get("name"),
            "latitude": city.get("latitude"),
            "longitude": city.get("longitude"),
            "country": city.get("country"),
        }

    except requests.RequestException as e:
        print("City search error:", e)
        return None


# ============================================================
# WEATHER BY COORDINATES
# ============================================================

def get_weather_by_coordinates(latitude, longitude):
    """
    Coordinates ke basis par current weather return karta hai.
    """

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current="
        "temperature_2m,"
        "relative_humidity_2m,"
        "surface_pressure,"
        "wind_speed_10m,"
        "precipitation,"
        "weather_code"
        "&timezone=auto"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        current = data.get("current", {})

        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "pressure": current.get("surface_pressure"),
            "wind_speed": current.get("wind_speed_10m"),
            "rainfall": current.get("precipitation"),
            "weather_code": current.get("weather_code"),
            "time": current.get("time"),
        }

    except requests.RequestException as e:
        print("Weather API error:", e)
        return None


# ============================================================
# WEATHER BY CITY NAME
# ============================================================

def get_weather_by_city(city_name="Islamabad"):
    """
    City name → coordinates → live weather
    """

    location = search_city(city_name)

    if location is None:
        return None

    weather = get_weather_by_coordinates(
        location["latitude"],
        location["longitude"]
    )

    if weather is None:
        return None

    weather["city"] = location["name"]
    weather["latitude"] = location["latitude"]
    weather["longitude"] = location["longitude"]

    return weather


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = get_weather_by_city("Islamabad")

    if result:
        print("City:", result["city"])
        print("Temperature:", result["temperature"], "°C")
        print("Humidity:", result["humidity"], "%")
        print("Pressure:", result["pressure"], "hPa")
        print("Wind Speed:", result["wind_speed"], "km/h")
        print("Rainfall:", result["rainfall"], "mm")
    else:
        print("Weather data not found.")