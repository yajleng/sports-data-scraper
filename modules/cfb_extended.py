# modules/cfb_extended.py
import os
import requests
import pandas as pd

CFB_API = "https://api.collegefootballdata.com"
CFB_KEY = os.getenv("CFBD_API_KEY", "")

def _headers():
    return {"Authorization": f"Bearer {CFB_KEY}"} if CFB_KEY else {}

def get_spplus(year: int = 2025) -> pd.DataFrame:
    """
    CFBD: /ratings/spplus
    Returns columns: team, sp_overall, sp_off, sp_def
    """
    url = f"{CFB_API}/ratings/spplus"
    r = requests.get(url, headers=_headers(), params={"year": year}, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data:
        return pd.DataFrame(columns=["team", "sp_overall", "sp_off", "sp_def"])

    rows = []
    for row in data:
        team = row.get("team")
        off = row.get("offense", {})
        deff = row.get("defense", {})
        rows.append({
            "team": team,
            "sp_overall": row.get("rating", None),
            "sp_off": off.get("rating", None),
            "sp_def": deff.get("rating", None),
        })
    df = pd.DataFrame(rows)
    return df

def get_ppa(year: int = 2025) -> pd.DataFrame:
    """
    CFBD: /ppa/teams
    Returns columns: team, ppa_off, ppa_def
    """
    url = f"{CFB_API}/ppa/teams"
    r = requests.get(url, headers=_headers(), params={"year": year}, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data:
        return pd.DataFrame(columns=["team", "ppa_off", "ppa_def"])

    rows = []
    for row in data:
        team = row.get("team")
        o = row.get("offense", {}) or {}
        d = row.get("defense", {}) or {}
        rows.append({
            "team": team,
            "ppa_off": o.get("overall", None),
            "ppa_def": d.get("overall", None),
        })
    df = pd.DataFrame(rows)
    return df

def merge_extended_metrics(base_df: pd.DataFrame, year: int = 2025) -> pd.DataFrame:
    """
    Given your weekly base DF (must have 'team' col), append SP+ and PPA.
    Returns a new DF with columns added:
      - sp_overall, sp_off, sp_def, ppa_off, ppa_def
    """
    if base_df is None or "team" not in base_df.columns:
        return base_df

    sp = get_spplus(year)
    ppa = get_ppa(year)

    out = base_df.copy()
    # normalize team keys just once for robust merges
    out["_k"] = out["team"].str.lower().str.strip()
    sp["_k"] = sp["team"].str.lower().str.strip()
    ppa["_k"] = ppa["team"].str.lower().str.strip()

    out = out.merge(sp.drop(columns=["team"]), on="_k", how="left")
    out = out.merge(ppa.drop(columns=["team"]), on="_k", how="left")

    # tidy
    out = out.drop(columns=["_k"])
    return out
