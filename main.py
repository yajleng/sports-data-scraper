import os
import time
from flask import Flask, jsonify, request
from modules.cfb_sportsipy import get_cfb_games, get_cfb_team, get_cfb_boxscore

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "College Football Data Scraper (Sportsipy) is running.",
        "status": "ok",
        "endpoints": {
            "cfb_games": "/scrape/cfb/games?date=YYYYMMDD",
            "cfb_team": "/scrape/cfb/team?name=TeamName&year=YYYY",
            "cfb_boxscore": "/scrape/cfb/boxscore?id=BoxscoreID",
            "health": "/health"
        }
    })

@app.route("/scrape/cfb/games")
def scrape_cfb_games():
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "Missing required query param: date (YYYYMMDD)"})
    data = get_cfb_games(date_str)
    return jsonify(data)

@app.route("/scrape/cfb/team")
def scrape_cfb_team():
    name = request.args.get("name")
    year = request.args.get("year", type=int, default=2024)
    if not name:
        return jsonify({"error": "Missing required query param: name"})
    data = get_cfb_team(name, year)
    return jsonify(data)

@app.route("/scrape/cfb/boxscore")
def scrape_cfb_boxscore():
    boxscore_id = request.args.get("id")
    if not boxscore_id:
        return jsonify({"error": "Missing required query param: id"})
    data = get_cfb_boxscore(boxscore_id)
    return jsonify(data)

@app.route("/health")
def health():
    return jsonify({"ok": True, "ts": int(time.time())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
