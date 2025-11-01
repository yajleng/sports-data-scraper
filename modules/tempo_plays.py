import os
import requests

def get_tempo(team, year=2025):
    """Compute simple tempo stats from drive data."""
    url = f"https://api.collegefootballdata.com/drives?year={year}&team={team}"
    r = requests.get(url, headers={"Authorization": f"Bearer {os.getenv('CFBD_API_KEY')}"})
    data = r.json()
    if not data: return {}
    plays = sum(d.get("plays", 0) for d in data)
    time = sum(d.get("duration", 0) for d in data) / 60  # sec→min
    return {
        "plays_per_game": plays / len(data),
        "plays_per_minute": plays / time if time else 0,
    }
