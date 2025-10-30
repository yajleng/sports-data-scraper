import requests
import time

def get_nfl_standings():
    base_url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/standings"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(base_url, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()

    # Follow ESPN’s redirect reference
    ref_url = data.get("$ref")
    if not ref_url:
        return {"source": "espn", "error": "No $ref found", "timestamp": int(time.time())}

    r2 = requests.get(ref_url, headers=headers, timeout=15)
    r2.raise_for_status()
    standings_data = r2.json()

    teams = []
    for group in standings_data.get("children", []):
        g_url = group.get("$ref")
        if not g_url:
            continue
        g_data = requests.get(g_url, headers=headers, timeout=15).json()
        group_name = g_data.get("name", "")
        for entry in g_data.get("entries", []):
            team_info = {}
            team_ref = entry.get("team", {}).get("$ref")
            if team_ref:
                team_data = requests.get(team_ref, headers=headers, timeout=15).json()
                team_info["team"] = team_data.get("displayName")
            for stat in entry.get("stats", []):
                team_info[stat.get("name")] = stat.get("displayValue")
            team_info["group"] = group_name
            teams.append(team_info)

    return {
        "source": "espn",
        "sport": "NFL",
        "timestamp": int(time.time()),
        "team_count": len(teams),
        "standings": teams
    }
