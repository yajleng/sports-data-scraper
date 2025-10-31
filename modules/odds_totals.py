import os, requests

def get_odds_totals(week=10, year=2025):
    """Pull spread and total lines for NCAAF games via TheOddsAPI."""
    api_key = os.getenv("ODDS_API_KEY")
    url = (
        "https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds/"
        f"?apiKey={api_key}&regions=us&markets=spreads,totals"
    )
    r = requests.get(url)
    data = r.json()
    games = []
    for g in data:
        games.append({
            "home_team": g["home_team"],
            "away_team": g["away_team"],
            "spread": g["bookmakers"][0]["markets"][0]["outcomes"][0]["point"],
            "total": g["bookmakers"][0]["markets"][1]["outcomes"][0]["point"],
        })
    return games
