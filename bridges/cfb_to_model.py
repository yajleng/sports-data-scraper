# bridges/cfb_to_model.py
"""
Bridge module connecting your college-football scrapers
to the deterministic cfb_spread_model.py system.

Usage:
    python bridges/cfb_to_model.py --home "Georgia" --away "Alabama" --year 2025 --week 10
"""

import json, math, sys, traceback
from pathlib import Path
from typing import Dict, Any

# Scraper imports
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

# Validation script
import validate_input


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _median(values):
    nums = [v for v in values if isinstance(v, (int, float)) and math.isfinite(v)]
    if not nums:
        return 0.0
    nums.sort()
    n = len(nums)
    return nums[n // 2] if n % 2 else (nums[n // 2 - 1] + nums[n // 2]) / 2


def _safe(v, default=0.0):
    return float(v) if isinstance(v, (int, float)) and math.isfinite(v) else default


def _safe_get(d: Dict, key: str, default=0.0):
    return d[key] if key in d and isinstance(d[key], (int, float)) else default


# ------------------------------------------------------------
# Core Builder
# ------------------------------------------------------------
def build_inputs(team_home: str, team_away: str, year: int, week: int) -> Dict[str, Any]:
    """Collects data from all scrapers and formats it for the deterministic model."""
    try:
        # --- matchup ---
        matchup = cfb_matchup.get_team_matchup(team_home, team_away, year)
        venue = matchup.get("venue", {})
        lat, lon = venue.get("lat", 0), venue.get("lon", 0)
        neutral = bool(venue.get("neutral", False))
        home_field_points = 0.0 if neutral else 1.2

        # --- efficiency metrics ---
        spplus = cfb_extended.get_spplus(year)
        ppa = cfb_extended.get_ppa(year)
        sp_h, sp_a = spplus.get(team_home, {}), spplus.get(team_away, {})
        ppa_h, ppa_a = ppa.get(team_home, {}), ppa.get(team_away, {})

        offense_home = _median([sp_h.get("sp_off"), ppa_h.get("ppa_off")])
        defense_home = _median([sp_h.get("sp_def"), ppa_h.get("ppa_def")])
        offense_away = _median([sp_a.get("sp_off"), ppa_a.get("ppa_off")])
        defense_away = _median([sp_a.get("sp_def"), ppa_a.get("ppa_def")])

        # --- odds ---
        odds = odds_totals.get_odds_totals(week=week, year=year)
        spread = _safe_get(odds, "median_spread_home", 0)
        odds_home = _safe_get(odds, "median_odds_home", -110)
        odds_away = _safe_get(odds, "median_odds_away", -110)

        # --- injuries ---
        inj_home = injuries_scraper.get_injuries(team_home)
        inj_away = injuries_scraper.get_injuries(team_away)
        qb_home_delta = _safe_get(inj_home, "qb_delta", 0)
        qb_away_delta = _safe_get(inj_away, "qb_delta", 0)
        key_injuries_home = int(inj_home.get("starters_out_non_qb", 0))
        key_injuries_away = int(inj_away.get("starters_out_non_qb", 0))

        # --- weather ---
        weather = weather_openmeteo.get_weather(lat, lon)
        wind_mph = _median([w.get("avg_wind") for w in weather.get("weather_window", [])])

        # --- tempo / pass rate ---
        t_h = tempo_plays.get_tempo(team_home)
        t_a = tempo_plays.get_tempo(team_away)
        pass_rate_home = _safe_get(t_h, "pass_rate", 0.52)
        pass_rate_away = _safe_get(t_a, "pass_rate", 0.48)

        # --- rest / travel (temporary placeholders) ---
        rest_diff_days = matchup.get("rest_diff_days", 0)
        away_travel_miles = venue.get("travel_miles", 0)

        return {
            "inputs": {
                "offense_home": offense_home,
                "defense_home": defense_home,
                "offense_away": offense_away,
                "defense_away": defense_away,
                "home_field_points": home_field_points,
                "rest_diff_days": rest_diff_days,
                "away_travel_miles": away_travel_miles,
                "qb_home_delta": qb_home_delta,
                "qb_away_delta": qb_away_delta,
                "key_injuries_home": key_injuries_home,
                "key_injuries_away": key_injuries_away,
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

    except Exception as e:
        print(f"\n[ERROR] Failed to build input JSON: {e}\n")
        traceback.print_exc()
        sys.exit(1)


# ------------------------------------------------------------
# Validation Wrapper
# ------------------------------------------------------------
def validate_inputs(data: Dict[str, Any]) -> bool:
    """Run validator and print result clearly."""
    try:
        tmp = Path("temp_input.json")
        tmp.write_text(json.dumps(data, indent=2))
        print("[INFO] Running validation...")
        ok = validate_input.main(str(tmp))  # expects validate_input.py to have a main()
        if ok:
            print("[SUCCESS] Validation passed ✅")
            return True
        else:
            print("[FAIL] Validation failed ❌ — see above.")
            return False
    except Exception:
        traceback.print_exc()
        return False


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build and validate model-ready input JSON for CFB.")
    parser.add_argument("--home", required=True)
    parser.add_argument("--away", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--output", default="cfb_input.json")
    args = parser.parse_args()

    data = build_inputs(args.home, args.away, args.year, args.week)

    if not data:
        print("[ERROR] No data generated.")
        sys.exit(1)

    if not validate_inputs(data):
        print("[WARNING] Input failed validation. JSON still written for inspection.")

    Path(args.output).write_text(json.dumps(data, indent=2))
    print(f"[OK] Wrote {args.output}")
