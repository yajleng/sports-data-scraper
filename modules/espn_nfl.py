# modules/espn_nfl.py
import time, requests

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
UA = "Mozilla/5.0 (compatible; CheekSpreader/1.0; +https://example.com/bot)"

def _get_json(url: str):
    r = requests.get(url, timeout=20, headers={"User-Agent": UA})
    r.raise_for_status()
    return r.json()

def _parse_game(evt):
    cid = evt.get("id")

    comps = evt.get("competitions", [{}])[0]
    status_raw = evt.get("status", {}).get("type", {}).get("name", "").lower()
    date_utc = evt.get("date")

    # teams array contains home/away; “homeAway” flag tells which
    teams = comps.get("competitors", [])
    home_t = next((t for t in teams if t.get("homeAway") == "home"), {})
    away_t = next((t for t in teams if t.get("homeAway") == "away"), {})

    home_name = (home_t.get("team") or {}).get("displayName")
    away_name = (away_t.get("team") or {}).get("displayName")

    home_score = int(home_t.get("score") or 0) if home_t else 0
    away_score = int(away_t.get("score") or 0) if away_t else 0

    # records if available
    def rec(team):
        recs = team.get("records") or []
        if recs and "summary" in recs[0]:
            return recs[0]["summary"]  # e.g., "5-2"
        return None

    # odds (if provided in feed)
    odds = None
    od = (comps.get("odds") or [{}])[0]
    if od:
        fav = od.get("details")  # e.g., "Eagles -6.5"
        spread = od.get("spread")
        odds = {"details": fav, "spread": spread}

    return {
        "id": cid,
        "datetime_utc": date_utc,
        "status": status_raw,  # pre / in / final
        "teams": {"home": home_name, "away": away_name},
        "score": {"home": home_score, "away": away_score},
        "records": {"home": rec(home_t), "away": rec(away_t)},
        "odds": odds,
    }

def get_nfl_data():
    data = _get_json(SCOREBOARD_URL)
    events = data.get("events") or []
    games = [_parse_game(e) for e in events]
    return {
        "sport": "NFL",
        "count": len(games),
        "timestamp": int(time.time()),
        "games": games,
    }
------------------------------------------------------------

STEP 3 — Update main.py to add the new route
1) In GitHub, open main.py → “Edit”.
2) Replace the whole file with this (keeps /scrape and adds /scrape/nfl):

------------------------------------------------------------
import os, requests, time
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from modules.espn_nfl import get_nfl_data  # <-- new import

app = Flask(__name__)

def run_scrape():
    url = "https://www.espn.com/college-football/"
    r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    headlines = [h.get_text(strip=True) for h in soup.select("section h1, section h2")][:5]
    return {"source": "espn", "timestamp": int(time.time()), "headlines_sample": headlines}

@app.route("/scrape")
def scrape():
    return jsonify(run_scrape())

@app.route("/scrape/nfl")
def scrape_nfl():
    return jsonify(get_nfl_data())

@app.route("/health")
def health():
    return jsonify({"ok": True, "ts": int(time.time())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
