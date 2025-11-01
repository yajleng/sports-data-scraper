import os
import requests
from statistics import mean

CFB_API = "https://api.collegefootballdata.com"
CFB_KEY = os.getenv("CFBD_API_KEY", "")

def get_tempo(team: str):
    """
    Returns estimated tempo metrics:
    - plays_per_game
    - plays_per_minute
    """

    headers = {"Authorization": f"Bearer {CFB_KEY}"} if CFB_KEY else {}
    url = f"{CFB_API}/stats/season"
    params = {"year": 2025, "team": team}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        # --- Extract plays per game and TOP (time of possession)
        plays = []
        poss_minutes = []

        for stat in data:
            stats = stat.get("stats", [])
            for s in stats:
                if s["category"] == "plays":
                    plays.append(float(s["stat"]))
                if s["category"] in ["timeOfPossession", "time_of_possession"]:
                    # Convert MM:SS → total minutes
                    try:
                        parts = str(s["stat"]).split(":")
                        total_minutes = int(parts[0]) + int(parts[1]) / 60
                        poss_minutes.append(total_minutes)
                    except Exception:
                        pass

        if not plays:
            return {"error": f"no tempo data found for {team}"}

        avg_plays = mean(plays)
        avg_poss = mean(poss_minutes) if poss_minutes else 30.0  # assume 30 minutes if missing
        plays_per_minute = round(avg_plays / avg_poss, 3)

        return {
            "plays_per_game": round(avg_plays, 3),
            "plays_per_minute": plays_per_minute,
        }

    except Exception as e:
        return {"error": f"tempo fetch failed: {str(e)}"}
