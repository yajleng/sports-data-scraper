
#!/usr/bin/env python3
"""
cfb_spread_model_v2.py
Deterministic (no-ML) CFB spread model with an expanded, reproducible stack:

1) True probability (logit/normal ATS)
2) Variance (sigma^2) with weather/injury adjustments
3) Confidence intervals for predicted margin
4) Reliability score (R^2-like, deterministic heuristic)
5) Lambda-weighted recency scalar (configurable)
6) Fixed-seed Monte Carlo (reproducible) for sanity-check probabilities

CLI:
  python cfb_spread_model_v2.py --input input.json --out report.json

This file is API-compatible with the v1 JSON schema used by your bridge:
  - cfg['inputs'] ... fields
  - cfg['market'] ... spread, odds_home, odds_away
"""

import json, math, argparse, sys, random
from typing import Dict, Any

RECENCY_LAMBDA = 0.834421  # user-specified

def phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

def american_to_decimal(american: float) -> float:
    if american <= 0:
        return 1 + 100.0/abs(american)
    else:
        return 1 + american/100.0

def implied_prob_from_american(american: float) -> float:
    if american <= 0:
        return abs(american) / (abs(american) + 100.0)
    else:
        return 100.0 / (american + 100.0)

def kelly_fraction(p: float, american: float) -> float:
    b = american_to_decimal(american) - 1.0
    q = 1.0 - p
    k = (b*p - q) / b if b != 0 else 0.0
    return max(0.0, k)

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def compute_expected_margin(cfg: Dict[str, Any]) -> Dict[str, Any]:
    I = cfg.get("inputs", {})
    C = cfg.get("coefficients", {})

    # Defaults (tunable)
    defaults = {
        "b0": 0.0,
        "b_matchup": 7.0,
        "b_hfa": 1.2,
        "b_rest": 0.15,
        "b_travel": -0.10,
        "b_qb": 3.0,
        "b_injury": 0.35,
        "b_weather_margin": 0.03,
        "sigma_spread": 14.0,
        # extra v2 knobs
        "r2_prior": 0.65,
        "wind_sigma_step": 0.01,   # +1% sigma per mph above 10
        "inj_sigma_step": 0.03,    # +3% sigma per non-QB starter out (sum both sides)
    }
    for k,v in defaults.items():
        C.setdefault(k, v)

    off_home = float(I.get("offense_home", 0.0))
    def_home = float(I.get("defense_home", 0.0))
    off_away = float(I.get("offense_away", 0.0))
    def_away = float(I.get("defense_away", 0.0))

    matchup_gap = (off_home - def_away) - (off_away - def_home)

    hfa = float(I.get("home_field_points", 0.0))
    rest_diff_days = float(I.get("rest_diff_days", 0.0))
    away_travel_miles = float(I.get("away_travel_miles", 0.0))
    qb_home_delta = float(I.get("qb_home_delta", 0.0))
    qb_away_delta = float(I.get("qb_away_delta", 0.0))
    key_inj_home = float(I.get("key_injuries_home", 0.0))
    key_inj_away = float(I.get("key_injuries_away", 0.0))

    wind_mph = float(I.get("wind_mph", 0.0))
    pass_rate_home = clamp(float(I.get("pass_rate_home", 0.5)), 0.0, 1.0)
    pass_rate_away = clamp(float(I.get("pass_rate_away", 0.5)), 0.0, 1.0)
    pass_rate_diff = (pass_rate_home - pass_rate_away)

    # True margin prediction (points)
    em = (
        C["b0"]
        + C["b_matchup"] * matchup_gap
        + (C["b_hfa"] if hfa == 0.0 else hfa)
        + C["b_rest"] * rest_diff_days
        + C["b_travel"] * (away_travel_miles / 500.0)
        + C["b_qb"] * (qb_home_delta - qb_away_delta)
        + C["b_injury"] * ((-key_inj_home) - (-key_inj_away))
        + C["b_weather_margin"] * (wind_mph * pass_rate_diff)
    )

    # Base variance
    sigma = float(C["sigma_spread"])
    # Weather increases sigma beyond 10mph (1% / mph)
    sigma *= (1.0 + C["wind_sigma_step"] * max(0.0, wind_mph - 10.0))
    # Injuries add % to sigma (sum both sides)
    inj_total = max(0.0, key_inj_home) + max(0.0, key_inj_away)
    sigma *= (1.0 + C["inj_sigma_step"] * inj_total)

    # Lambda-weighted recency scalar (deterministic): shrink sigma modestly if lambda < 1
    # Effective observations proxy: n_eff = 1/(1-lambda) up to cap
    n_eff = min(12.0, 1.0 / max(1e-6, (1.0 - RECENCY_LAMBDA)))
    sigma /= math.sqrt(n_eff/4.0)  # divide by sqrt to keep realistic CFB variance

    return {
        "expected_margin_home_minus_away": em,
        "sigma_spread": sigma,
        "components": {
            "matchup_gap": matchup_gap,
            "hfa_used": (C["b_hfa"] if hfa == 0.0 else hfa),
            "rest_points": C["b_rest"] * rest_diff_days,
            "travel_points": C["b_travel"] * (away_travel_miles / 500.0),
            "qb_points": C["b_qb"] * (qb_home_delta - qb_away_delta),
            "injury_points": C["b_injury"] * ((-key_inj_home) - (-key_inj_away)),
            "weather_points": C["b_weather_margin"] * (wind_mph * pass_rate_diff)
        },
        "coefficients_used": C
    }

def evaluate_market_v2(em_report: Dict[str, Any], market: Dict[str, Any]) -> Dict[str, Any]:
    em = em_report["expected_margin_home_minus_away"]
    sigma = em_report["sigma_spread"]
    C = em_report["coefficients_used"]

    S = float(market.get("spread", 0.0))
    odds_home = float(market.get("odds_home", -110))
    odds_away = float(market.get("odds_away", -110))

    # ATS cover probabilities (analytic)
    z_home = (em - S) / max(1e-9, sigma)
    p_home_cover = phi(z_home)
    p_away_cover = 1.0 - p_home_cover

    # Moneyline-style win prob from zero line (proxy)
    z_home_ml = em / max(1e-9, sigma)
    p_home_win = phi(z_home_ml)
    p_away_win = 1.0 - p_home_win

    # Confidence intervals for predicted margin (68% and 95%)
    ci68 = [em - 1.0 * sigma, em + 1.0 * sigma]
    ci95 = [em - 1.96 * sigma, em + 1.96 * sigma]

    # Deterministic reliability (R^2-like)
    r2 = float(C.get("r2_prior", 0.65))
    edge_pts = abs(em - S)
    r2 *= (1.0 - min(0.35, sigma/20.0))   # more variance → lower reliability
    r2 *= (0.85 + 0.15 * min(1.0, edge_pts / 7.0))  # reward clearer edges a bit
    r2 = max(0.0, min(0.95, r2))

    # EV per $1
    def ev_per_dollar(p, american):
        dec = american_to_decimal(american)
        b = dec - 1.0
        q = 1.0 - p
        return p*b - q

    ev_home = ev_per_dollar(p_home_cover, odds_home)
    ev_away = ev_per_dollar(p_away_cover, odds_away)

    # Edge confidence (0..1): blend of z, r2
    edge_confidence = max(0.0, min(1.0, (abs(z_home) / 2.5) * r2))

    # Kelly
    k_home = kelly_fraction(p_home_cover, odds_home)
    k_away = kelly_fraction(p_away_cover, odds_away)

    # Fixed-seed Monte Carlo to sanity-check cover prob
    random.seed(42)
    N = 10000
    cnt_home = 0
    for _ in range(N):
        # normal draw via Box-Muller (deterministic with fixed seed)
        u1 = max(1e-12, random.random())
        u2 = random.random()
        g = math.sqrt(-2.0*math.log(u1)) * math.cos(2.0*math.pi*u2)  # ~N(0,1)
        margin = em + sigma * g
        if (margin - S) > 0:
            cnt_home += 1
    mc_p_home_cover = cnt_home / float(N)

    return {
        "market_spread": S,
        "prob_home_cover_analytic": p_home_cover,
        "prob_home_cover_mc": mc_p_home_cover,
        "prob_away_cover_analytic": p_away_cover,
        "win_prob_home": p_home_win,
        "win_prob_away": p_away_win,
        "ev_home_per_$1": ev_home,
        "ev_away_per_$1": ev_away,
        "kelly_home": k_home,
        "kelly_away": k_away,
        "ci68_margin": ci68,
        "ci95_margin": ci95,
        "r2_reliability": r2,
        "edge_confidence": edge_confidence
    }

def decide_pick_v2(market_report: Dict[str, Any]) -> Dict[str, Any]:
    edge_threshold_ev = 0.03
    ev_home = market_report["ev_home_per_$1"]
    ev_away = market_report["ev_away_per_$1"]
    name = "home" if ev_home > ev_away else "away"
    ev = max(ev_home, ev_away)
    prob = market_report["prob_home_cover_analytic"] if name == "home" else market_report["prob_away_cover_analytic"]
    kelly = market_report["kelly_home"] if name == "home" else market_report["kelly_away"]
    side = name if ev >= edge_threshold_ev else "no_bet"
    return {
        "side": side,
        "edge_ev_per_$1": ev,
        "prob_cover": prob,
        "recommended_fraction_bankroll_quarter_kelly": (0.25*kelly) if side != "no_bet" else 0.0,
        "note": "No bet if EV < 0.03 to avoid thin edges."
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to input JSON")
    ap.add_argument("--out", required=True, help="Path to write report JSON")
    args = ap.parse_args()

    with open(args.input, "r") as f:
        cfg = json.load(f)

    em_report = compute_expected_margin(cfg)
    market = cfg.get("market", {})
    market_report = evaluate_market_v2(em_report, market)

    report = {
        "metadata": {
            "model": "cfb_spread_model_v2",
            "version": "2.0.0",
            "generated_at_utc": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "recency_lambda": RECENCY_LAMBDA,
        },
        "inputs": cfg.get("inputs", {}),
        "coefficients_used": em_report["coefficients_used"],
        "components": em_report["components"],
        "expected_margin_home_minus_away": em_report["expected_margin_home_minus_away"],
        "sigma_spread": em_report["sigma_spread"],
        "market_evaluation": market_report,
        "recommendation": decide_pick_v2(market_report)
    }

    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
