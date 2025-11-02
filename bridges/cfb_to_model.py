# bridges/cfb_to_model.py
"""
Bridge module that connects your sports-data-scraper repository
to the deterministic cfb_spread_model.py system.
"""

import json, math
from datetime import datetime
from pathlib import Path

# Scraper modules
from modules import (
    cfb_matchup,
    cfb_extended,
    massey_scraper,
    normalization,
    odds_totals,
    injuries_scraper,
    weather_openmeteo,
    tempo_plays,
)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _median(values):
    nums = [v for v in values if isinstance(v, (int, float)) and math.isfinite(v)]
    if not nums:
        return 0.0
    nums.sort()
    n = len(nums)
    return (nums[n // 2] if n % 2 else (nums[n // 2 - 1] + nums[n // 2]) / 2)

def _safe(v, default=0.0):
    return float(v) if isinstance(v, (int, float)) and math.isfinite(v) else default

# ------------------------------------------------------------
# Core
# ------------------------------------------------------------
def build_inputs(team_home: str, team_away: str, year: int, week: int):
    """Collects data from scrapers and formats it for the deterministic model."""
    # --- matchup info ---
    matchup = cfb_matchup.get_team_matchup(team_home, team_away, year)
    venue = matchup.get("venue", {})
    lat, lon = venue.get("lat", 0), venue.get("lon", 0)
    neutral = bool(venue.get("neutral", False))
    home_field_points = 0.0 if neutral else 1.2

    # --- efficiency metrics ---
    sp_h = cfb_extended.get_spplus(year).get(team_home, {})
    sp_a = cfb_extended.get_spplus(year).get(team_away, {})
    ppa_h = cfb_extended.get_ppa(year).get(team_home, {})
    ppa_a = cfb_extended.get_ppa(year).get(team_away, {})

    off_home = _median([sp_h.get("sp_off"), ppa_h.get("ppa_off")])
    def_home = _median([sp_h.get("sp_def"), ppa_h.get("ppa_def")])
    off_away = _median([sp_a.get("sp_off"), ppa_a.get("ppa_off")])
    def_away = _median([sp_a.get("sp_def"), ppa_a.get("ppa_def")])

    # --- odds ---
    odds = odds_totals.get_odds_totals(week=week, year=year)
    spread = odds.get("median_spread_home", 0)
    odds_home = odds.get("median_odds_home", -110)
    odds_away = odds.get("median_odds_away", -110)

    # --- injuries ---
    inj_home = injuries_scraper.get_injuries(team_home)
    inj_away = injuries_scraper.get_injuries(team_away)
    qb_home_delta = inj_home.get("qb_delta", 0)
    qb_away_delta = inj_away.get("qb_delta", 0)
    key_inj_home = inj_home.get("starters_out_non_qb", 0)
    key_inj_away = inj_away.get("starters_out_non_qb", 0)

    # --- weather ---
    weather = weather_openmeteo.get_weather(lat, lon)
    wind_mph = _median([w.get("avg_wind") for w in weather.get("weather_window", [])])

    # --- tempo / pass rates ---
    t_h = tempo_plays.get_tempo(team_home)
    t_a = tempo_plays.get_tempo(team_away)
    pass_rate_home = t_h.get("pass_rate", 0.52)
    pass_rate_away = t_a.get("pass_rate", 0.48)

    # --- rest / travel (stubbed for now) ---
    rest_diff_days = 0
    away_travel_miles = venue.get("travel_miles", 0)

    return {
        "inputs": {
            "offense_home": off_home,
            "defense_home": def_home,
            "offense_away": off_away,
            "defense_away": def_away,
            "home_field_points": home_field_points,
            "rest_diff_days": rest_diff_days,
            "away_travel_miles": away_travel_miles,
            "qb_home_delta": qb_home_delta,
            "qb_away_delta": qb_away_delta,
            "key_injuries_home": key_inj_home,
            "key_injuries_away": key_inj_away,
            "wind_mph": wind_mph,
            "pass_rate_home": pass_rate_home,
            "pass_rate_away": pass_rate_away,
        },
        "market": {
            "spread": spread,
            "odds_home": odds_home,
            "odds_away": odds_away,
        },
    }

# ------------------------------------------------------------
# CLI utility
# ------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build model-ready input JSON for college football.")
    parser.add_argument("--home", required=True)
    parser.add_argument("--away", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--output", default="cfb_input.json")
    args = parser.parse_args()

    data = build_inputs(args.home, args.away, args.year, args.week)
    Path(args.output).write_text(json.dumps(data, indent=2))
    print(f"Wrote {args.output}")
