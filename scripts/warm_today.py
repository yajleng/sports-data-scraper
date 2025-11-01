#!/usr/bin/env python
"""
Command-line cache warmer for Cheek Spreader.
Example:
  python scripts/warm_today.py --year 2025 --week 10 \
    --teams "North Carolina,Syracuse" \
    --latlon "35.907,-79.049;43.048,-76.147" \
    --kickoffs "2025-10-31T23:00Z"
"""
import argparse
import json
from modules.warmers import warm_slate

def _parse_latlon(s: str):
    return [tuple(map(float, p.split(","))) for p in s.split(";")]

def _parse_teams(s: str):
    return [tuple(p.split(",")) for p in s.split(";")]

def _parse_kickoffs(s: str):
    return [k.strip() for k in s.split(";")]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--week", type=int, required=False)
    ap.add_argument("--teams", required=True,
                    help='"TeamA,TeamB;TeamC,TeamD"')
    ap.add_argument("--latlon", required=True,
                    help='"35.9,-79.0;43.0,-76.1"')
    ap.add_argument("--kickoffs", required=True,
                    help='"2025-10-31T23:00Z;2025-11-01T18:00Z"')
    args = ap.parse_args()

    results = warm_slate(
        pairs=_parse_teams(args.teams),
        year=args.year,
        week=args.week,
        latlons=_parse_latlon(args.latlon),
        kickoffs=_parse_kickoffs(args.kickoffs),
    )
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
