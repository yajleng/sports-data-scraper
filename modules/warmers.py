import time
from datetime import datetime, timezone
from typing import List, Tuple, Optional, Dict, Any

# ✅ Adjust these imports if your real module names differ:
from modules.cfb_data import get_team_matchup
from modules.cfb_data import get_lines
from modules.weather_openmeteo import get_kickoff_window


def _to_dt_utc(s: str) -> datetime:
    """Convert ISO8601 string like '2025-10-31T23:00Z' to UTC datetime."""
    s = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def warm_game(team: str, opp: str, year: int, week: Optional[int],
              lat: float, lon: float, kickoff_iso: str) -> Dict[str, Any]:
    """Prefetch matchup, line, and weather data for a single game."""
    kickoff_dt = _to_dt_utc(kickoff_iso)
    report: Dict[str, Any] = {"team": team, "opp": opp, "year": year, "week": week, "ok": {}}

    try:
        get_team_matchup(team, opp, year, week)
        report["ok"]["matchup"] = True
    except Exception as e:
        report["ok"]["matchup"] = f"err:{e}"

    try:
        get_lines(team, year, week)
        get_lines(opp, year, week)
        report["ok"]["lines"] = True
    except Exception as e:
        report["ok"]["lines"] = f"err:{e}"

    try:
        get_kickoff_window(lat, lon, kickoff_dt)
        report["ok"]["weather"] = True
    except Exception as e:
        report["ok"]["weather"] = f"err:{e}"

    return report


def warm_slate(pairs: List[Tuple[str, str]], year: int, week: Optional[int],
               latlons: List[Tuple[float, float]], kickoffs: List[str],
               delay: float = 0.25) -> List[Dict[str, Any]]:
    """Warm multiple games in one pass (safe to run periodically)."""
    out = []
    for (team, opp), (lat, lon), kickoff in zip(pairs, latlons, kickoffs):
        res = warm_game(team, opp, year, week, lat, lon, kickoff)
        out.append(res)
        time.sleep(delay)  # polite pause between requests
    return out
