from datetime import datetime, timezone
import time
from typing import List, Tuple, Optional, Dict, Any

# ✅ Adjusted imports to match your real files
from modules.cfb_data import get_team_matchup  # or from cfb_extended if that’s where it lives
from modules.cfb_data import get_lines         # or rename if exists elsewhere
from modules.weather_openmeteo import get_kickoff_window

def _to_dt_utc(s: str) -> datetime:
    s = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def warm_game(team: str, opp: str, year: int, week: Optional[int],
              lat: float, lon: float, kickoff_iso: str) -> Dict[str, Any]:
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
