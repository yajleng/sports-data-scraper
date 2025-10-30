import os
import time
from flask import Flask, jsonify, request
from modules.cfb_sportsipy import get_cfb_games, get_cfb_team, get_cfb_boxscore

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "College Football Data Scraper (Sportsipy) is running.",
        "endpoints": {
            "cfb_games": "/scrape/cfb/games?date=YYYYMMDD",
            "cfb_team": "/scrape/cfb/team?name=TeamName&year=YYYY",
            "cfb_boxscore": "/scrape/cfb/boxscore?id=BoxscoreID",
            "health": "/health"
        },
        "status": "ok"
    })

@app.route("/scrape/cfb/games")
def cfb_games():
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "Missing ?date=YYYYMMDD"}), 400
    try:
        data = get_cfb_games(date)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/scrape/cfb/team")
def cfb_team():
    name = request.args.get("name")
    year = request.args.get("year")
    if not name:
        return jsonify({"error": "Missing ?name="}), 400
    try:
        data = get_cfb_team(name, year)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/scrape/cfb/boxscore")
def cfb_boxscore():
    gid = request.args.get("id")
    if not gid:
        return jsonify({"error": "Missing ?id="}), 400
    try:
        data = get_cfb_boxscore(gid)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"ok": True, "timestamp": int(time.time())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
