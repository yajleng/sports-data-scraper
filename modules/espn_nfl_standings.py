import requests
import time

def get_nfl_standings():
    url = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
    r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    data = r.json()

    standings = []
    for conference in data.get("children", []):
        conf_name = conference.get("name", "")
        for division in conference.get("children", []):
            div_name = division.get("name", "")
            for team_entry in division.get("standings", []):
                team = team_entry.get("team", {})
                record = team_entry.get("stats", [])
                team_stats = {stat["name"]: stat.get("displayValue") for stat in record}
                standings.append({
                    "conference": conf_name,
                    "division": div_name,
                    "team": team.get("displayName"),
                    "wins": team_stats.get("wins"),
                    "losses": team_stats.get("losses"),
                    "ties": team_stats.get("ties"),
                    "points_for": team_stats.get("pointsFor"),
                    "points_against": team_stats.get("pointsAgainst"),
                    "win_percent": team_stats.get("winPercent"),
                    "streak": team_stats.get("streak"),
                    "rank": team_stats.get("rank")
                })

    return {
        "source": "espn",
        "sport": "NFL",
        "timestamp": int(time.time()),
        "team_count": len(standings),
        "standings": standings
    }
