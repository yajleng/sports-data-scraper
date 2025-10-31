# modules/cfb_batch.py
import os, json, time
from typing import Dict, Any, List
import requests
import pandas as pd
from modules.normalization import normalize_frame

CFBD_API_KEY = os.getenv("CFBD_API_KEY", "")
CFBD_BASE = "https://api.collegefootballdata.com"

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def _cfbd_headers():
    if not CFBD_API_KEY:
        # CFBD works without a key for many endpoints, but you’ll be rate-limited.
        return {}
    return {"Authorization": f"Bearer {CFBD_API_KEY}"}

def _cache_path(year: int, week: int) -> str:
    return os.path.join(DATA_DIR, f"cfb_{year}_week{week}.json")

def fetch_all_teams_metrics(year: int, week: int) -> pd.DataFrame:
    """
    Example aggregator:
    - pulls team season stats & derives a few simple metrics.
    Replace/extend with the exact CFBD endpoints you prefer.
    """
    # 1) Offense/Defense EPA per play (by game or season-to-date)
    # Here we use /stats/season?year=YYYY&team=... in a batched manner:
    # Simpler: /teams/fbs?year=YYYY -> list all teams, then per-team calls.
    # To keep rate-light, we hit team season stats aggregate endpoints.

    # List teams
    r = requests.get(f"{CFBD_BASE}/teams/fbs?year={year}", headers=_cfbd_headers(), timeout=30)
    r.raise_for_status()
    teams = [t["school"] for t in r.json()]

    rows: List[Dict[str, Any]] = []
    for team in teams:
        # offense EPA (proxy using CFBD advanced stats endpoint)
        try:
            adv = requests.get(
                f"{CFBD_BASE}/stats/season/advanced?year={year}&team={requests.utils.quote(team)}",
                headers=_cfbd_headers(), timeout=30
            )
            adv.raise_for_status()
            advj = adv.json()
        except Exception:
            advj = []

        # pull a single season row if present
        epa_off = epa_def = sr_off = sr_def = expl = 0.0
        if advj:
            row = advj[0]  # season aggregate row
            # these keys vary by endpoint version; adjust as needed:
            epa_off = float(row.get("offense", {}).get("successRate", 0))  # as example
            epa_def = float(row.get("defense", {}).get("successRate", 0))
            sr_off  = float(row.get("offense", {}).get("successRate", 0))
            sr_def  = float(row.get("defense", {}).get("successRate", 0))
            expl    = float(row.get("offense", {}).get("explosiveness", 0))

        rows.append({
            "team": team,
            "epa_off": epa_off,
            "epa_def": epa_def,
            "success_rate_off": sr_off,
            "success_rate_def": sr_def,
            "explosiveness": expl
        })

        # light throttle for free tier
        time.sleep(0.08)

    df = pd.DataFrame(rows)
    return df

def update_weekly_cache(year: int, week: int) -> Dict[str, Any]:
    df = fetch_all_teams_metrics(year, week)
    norm = normalize_frame(df)
    blob = {
        "year": year,
        "week": week,
        "generated_ts": int(time.time()),
        "count": int(len(norm)),
        "metrics": norm.to_dict(orient="records")
    }
    with open(_cache_path(year, week), "w", encoding="utf-8") as f:
        json.dump(blob, f, ensure_ascii=False)
    return {"ok": True, "count": blob["count"], "year": year, "week": week}

def read_from_cache(year: int, week: int) -> Dict[str, Any]:
    path = _cache_path(year, week)
    if not os.path.exists(path):
        return {"ok": False, "error": "cache_not_found"}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_team_from_cache(year: int, week: int, team: str) -> Dict[str, Any]:
    data = read_from_cache(year, week)
    if not data or not data.get("metrics"):
        return {"ok": False, "error": "cache_not_found"}
    team_row = next((m for m in data["metrics"] if m["team"].lower() == team.lower()), None)
    if not team_row:
        return {"ok": False, "error": "team_not_in_cache"}
    return {"ok": True, "team": team_row, "meta": {"year": year, "week": week}}
