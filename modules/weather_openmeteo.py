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

# ---------------------------------------------------------------------
# Added helper for warmers.py compatibility
# ---------------------------------------------------------------------
def get_kickoff_window(lat: float, lon: float, kickoff: str):
    """
    Placeholder wrapper to make warmers.py run.
    You can later replace this with a real hourly forecast slice around kickoff.
    """
    try:
        data = get_weather(lat, lon)
        # Simplified: just return hourly data subset or empty fallback
        return {
            "kickoff": kickoff,
            "lat": lat,
            "lon": lon,
            "sample": data
        }
    except Exception as e:
        return {"error": f"weather window fetch failed: {str(e)}"}
