import os
import requests
from statistics import mean

CFB_API = "https://api.collegefootballdata.com"
CFB_KEY = os.getenv("CFBD_API_KEY", "")

def get_tempo(team: str):
    """
    Returns team tempo from drive-level stats:
    - plays_per_game
    - plays_per_minute (based on average drive duration)
    """
    headers = {"Authorization": f"Bearer {CFB_KEY}"} if CFB_KEY else {}
    url = f"{CFB_API}/drives"
    params = {"year": 2025, "team": team}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()

        if not data:
            return {"error": f"no drive data found for {team}"}

        total_plays = []
        durations = []

        for d in data:
            if "plays" in d:
                total_plays.append(d["plays"])
            # Drive duration sometimes in "mm:ss"
            if "driveTime" in d and isinstance(d["driveTime"], str):
                try:
                    mm, ss = map(int, d["driveTime"].split(":"))
                    durations.append(mm + ss / 60)
                except Exception:
                    pass

        if not total_plays:
            return {"error": f"no tempo data found for {team}"}

        avg_plays = mean(total_plays)
        avg_duration = mean(durations) if durations else 2.5  # 2.5 min avg drive fallback

        # Estimate: ~12 drives/game → scale per game
        plays_per_game = avg_plays * 12
        plays_per_minute = round(plays_per_game / (avg_duration * 12), 3)

        return {
            "plays_per_game": round(plays_per_game, 3),
            "plays_per_minute": plays_per_minute,
        }

    except Exception as e:
        return {"error": f"tempo fetch failed: {str(e)}"}
