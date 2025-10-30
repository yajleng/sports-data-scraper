import requests
import time

def get_nfl_standings():
    headers = {"User-Agent": "Mozilla/5.0"}
    base_url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/standings"
    r = requests.get(base_url, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()

    ref_url = data.get("$ref")
    if not ref_url:
        return {"source": "espn", "error": "No $ref found", "timestamp": int(time.time())}

    r2 = requests.get(ref_url, headers=headers, timeout=15)
    r2.raise_for_status()
    standings_data = r2.json()

    # Dive deeper if ESPN returned nested children
    children = standings_data.get("children", [])
    if not children and "$ref" in standings_data:
        # sometimes standings_data itself is just another ref wrapper
        next_ref = standings_data["$ref"]
        r3 = requests.get(next_ref, headers=headers, timeout=15)
        r3.raise_for_status()
        standings_data = r3.json()
        children = standings_data.get("children", [])

    teams = []

    # iterate through group refs (divisions/conferences)
    for child in children:
        child_ref = child.get("$ref")
        if not child_ref:
            continue
        child_data = requests.get(child_ref, headers=headers, timeout=15).json()
        group_name = child_data.get("name", "")
        for entry in child_data.get("entries", []):
            team_info = {}
            team_ref = entry.get("team", {}).get("$ref")
            if team_ref:
                tdata = requests.get(team_ref, headers=headers, timeout=15).json()
                team_info["team"] = tdata.get("displayName")
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
