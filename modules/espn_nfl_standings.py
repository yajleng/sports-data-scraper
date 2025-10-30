# modules/espn_nfl_standings.py  (clean, ready-to-run)
import requests
import time

UA = {"User-Agent": "Mozilla/5.0"}

def _stats_map(stats):
    out = {}
    for s in stats or []:
        name = s.get("name") or s.get("type")
        if name:
            out[name] = s.get("displayValue") if "displayValue" in s else s.get("value")
    return out

def _parse_children_tree(data):
    rows = []
    for conference in data.get("children", []) or []:
        conf_name = conference.get("name", "")
        for division in conference.get("children", []) or []:
            div_name = division.get("name", "")
            st = division.get("standings") or {}
            entries = st.get("entries") or division.get("standings", [])
            for entry in entries:
                team = entry.get("team", {}) or {}
                stats = _stats_map(entry.get("stats"))
                rows.append({
                    "conference": conf_name,
                    "division": div_name,
                    "team": team.get("displayName") or team.get("name"),
                    "wins": stats.get("wins"),
                    "losses": stats.get("losses"),
                    "ties": stats.get("ties"),
                    "points_for": stats.get("pointsFor") or stats.get("points_for"),
                    "points_against": stats.get("pointsAgainst") or stats.get("points_against"),
                    "win_percent": stats.get("winPercent") or stats.get("win_percent"),
                    "streak": stats.get("streak"),
                    "rank": stats.get("rank") or entry.get("rank")
                })
    return rows

def _parse_flat_standings(data):
    rows = []
    st = data.get("standings", {}) or {}
    entries = st.get("entries", []) or []
    for entry in entries:
        team = entry.get("team", {}) or {}
        stats = _stats_map(entry.get("stats"))
        group = entry.get("group", {}) or {}
        parent = group.get("parent", {}) if isinstance(group, dict) else {}
        rows.append({
            "conference": (parent.get("name") or "") if isinstance(parent, dict) else "",
            "division": group.get("name") if isinstance(group, dict) else "",
            "team": team.get("displayName") or team.get("name"),
            "wins": stats.get("wins"),
            "losses": stats.get("losses"),
            "ties": stats.get("ties"),
            "points_for": stats.get("pointsFor") or stats.get("points_for"),
            "points_against": stats.get("pointsAgainst") or stats.get("points_against"),
            "win_percent": stats.get("winPercent") or stats.get("win_percent"),
            "streak": stats.get("streak"),
            "rank": stats.get("rank") or entry.get("rank")
        })
    return rows

def get_nfl_standings():
    season = str(time.gmtime().tm_year)
    url = f"https://site.api.espn.com/apis/v2/sports/football/nfl/standings?season={season}"
    r = requests.get(url, timeout=20, headers=UA)
    r.raise_for_status()
    data = r.json()

    rows = _parse_children_tree(data)
    if not rows:
        rows = _parse_flat_standings(data)

    return {
        "source": "espn",
        "sport": "NFL",
        "timestamp": int(time.time()),
        "team_count": len(rows),
        "standings": rows
    }
