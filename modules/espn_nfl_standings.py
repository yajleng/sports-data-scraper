import requests
import time

def get_nfl_standings():
    url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/standings"
    r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    data = r.json()

    standings = []
    for group in data.get("children", []):
        g_url = group.get("$ref")
        if not g_url:
            continue
        g_data = requests.get(g_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).json()
        group_name = g_data.get("name", "")
        entries = g_data.get("entries", [])
        for entry in entries:
            team_info = {}
            team_ref = entry.get("team", {}).get("$ref")
            if team_ref:
                team = requests.get(team_ref, timeout=15, headers={"User-Agent": "Mozilla/5.0"}).json()
                team_info["team"] = team.get("displayName")
            stats_ref = entry.get("stats", {}).get("$ref")
            if stats_ref:
                stats = requests.get(stats_ref, timeout=15, headers={"User-Agent": "Mozilla/5.0"}).json().get("stats", [])
                for s in stats:
                    team_info[s.get("name")] = s.get("displayValue")
            team_info["group"] = group_name
            standings.append(team_info)

    return {
        "source": "espn",
        "sport": "NFL",
        "timestamp": int(time.time()),
        "team_count": len(standings),
        "standings": standings
    }
