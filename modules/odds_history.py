import requests, os

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports/ncaaf/odds-history"

def get_odds_history(date: str):
    params = {"apiKey": ODDS_API_KEY, "regions": "us", "date": date}
    r = requests.get(BASE_URL, params=params, timeout=10)
    return r.json() if r.ok else {"error": r.text}
