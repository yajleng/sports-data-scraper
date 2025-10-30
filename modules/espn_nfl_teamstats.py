import requests
import time

def fetch_json(url, headers):
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def get_nfl_teamstats():
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
    data = fetch_json(url, headers)
    teams = []

    for team in data.get("sports", [])[0].get("leagues", [])[0].get("teams", []):
        info = team.get("team", {})
        team_id = info.get("id")
        if not team_id:
            continue
        stats_url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/statistics"
        stats = fetch_json(stats_url, headers)
        categories = stats.get("splits", {}).get("categories", [])
        team_stats = {"team": info.get("displayName")}
        for cat in categories:
            for stat in cat.get("stats", []):
                name = stat.get("name")
                val = stat.get("value")
                if name and val is not None:
                    team_stats[name] = val
        teams.append(team_stats)

    return {
        "source": "espn",
        "sport": "NFL",
        "timestamp": int(time.time()),
        "team_count": len(teams),
        "teams": teams
    }
