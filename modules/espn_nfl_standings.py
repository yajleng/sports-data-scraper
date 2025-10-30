import requests
import time

def fetch_json(url, headers):
    """Helper function to safely get JSON."""
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def get_nfl_standings():
    headers = {"User-Agent": "Mozilla/5.0"}
    base_url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/standings"
    root = fetch_json(base_url, headers)

    # Follow all nested $ref links until we reach standings with entries
    visited = set()
    to_visit = [root.get("$ref") or base_url]
    teams = []

    while to_visit:
        url = to_visit.pop()
        if not url or url in visited:
            continue
        visited.add(url)

        data = fetch_json(url, headers)
        if not data:
            continue

        # If this layer has group children, add their refs
        for child in data.get("children", []):
            ref = child.get("$ref")
            if ref:
                to_visit.append(ref)

        # If this layer has entries, parse teams
        if "entries" in data:
            for entry in data["entries"]:
                team_info = {}
                team_ref = entry.get("team", {}).get("$ref")
                if team_ref:
                    team_data = fetch_json(team_ref, headers)
                    team_info["team"] = team_data.get("displayName")
                for stat in entry.get("stats", []):
                    team_info[stat.get("name")] = stat.get("displayValue")
                teams.append(team_info)

    return {
        "source": "espn",
        "sport": "NFL",
        "timestamp": int(time.time()),
        "team_count": len(teams),
        "standings": teams,
    }
