import os
import json
import requests

CACHE_FILE = "data/odds_cache.json"
API_KEY = os.getenv("ODDS_API_KEY")

def get_odds_totals(week=10, year=2025):
    """Fetch odds and totals from TheOddsAPI, with fallback to cached data."""
    url = f"https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "american"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # normalize and structure
        games = []
        for g in data:
            home = g.get("home_team", "")
            away = g.get("away_team", "")
            bookmakers = g.get("bookmakers", [])
            if not bookmakers:
                continue

            lines = bookmakers[0].get("markets", [])
            spread, total = None, None
            for market in lines:
                if market["key"] == "spreads":
                    spread = market["outcomes"][0]["point"]
                elif market["key"] == "totals":
                    total = market["outcomes"][0]["point"]

            games.append({
                "home_team": home,
                "away_team": away,
                "spread": spread,
                "total": total
            })

        if not games:
            raise ValueError("no_games_parsed")

        # ✅ write cache
        os.makedirs("data", exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump({"cached_at": week, "games": games}, f)

        return {"source": "live", "games": games}

    except Exception as e:
        # 🩵 fallback path
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                cached = json.load(f)
            return {
                "source": "cache",
                "note": f"Live fetch failed ({str(e)}), serving cached data.",
                "games": cached.get("games", [])
            }

        # ❌ if no cache exists yet
        return {
            "error": f"Failed to fetch odds: {str(e)}",
            "note": "No cached data available yet."
        }
