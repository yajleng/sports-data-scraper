import requests

def get_weather(lat, lon):
    """Fetch simple hourly weather forecast for game location."""
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,precipitation,windspeed_10m"
    )
    r = requests.get(url)
    data = r.json()
    return {
        "avg_temp": sum(data["hourly"]["temperature_2m"]) / len(data["hourly"]["temperature_2m"]),
        "avg_wind": sum(data["hourly"]["windspeed_10m"]) / len(data["hourly"]["windspeed_10m"]),
        "rain_prob": sum(data["hourly"]["precipitation"]) / len(data["hourly"]["precipitation"]),
    }
