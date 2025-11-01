import os
import time
from flask import Flask, jsonify, request

# Core modules
from modules.cfb_data import get_cfbd_team
from modules.cfb_batch import update_weekly_cache, read_from_cache, get_team_from_cache

# New modules
from modules.weather_openmeteo import get_weather
from modules.odds_totals import get_odds_totals
from modules.tempo_plays import get_tempo
from modules.injuries_scraper import get_injuries
from modules.warmers import warm_game  # ✅ keep this

app = Flask(__name__)


# -----------------------------------------------------------
# ROOT
# -----------------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "CFB weekly cache service (batch + normalization)",
        "endpoints": {
            "admin_update": "/admin/cfb/update?year=2025&week=10",
            "cache_info": "/cfb/cache?year=2025&week=10",
            "team": "/cfb/team?name=Georgia&year=2025&week=10",
            "fetch_team_alias": "/fetch/cfb/team?name=Georgia&year=2025&week=10",
            "weather": "/cfb/weather?lat=33.94&lon=-83.37",
            "odds": "/cfb/odds?year=2025&week=10",
            "tempo": "/cfb/tempo?team=Georgia",
            "injuries": "/cfb/injuries?team=georgia",
            "health": "/health"
        },
        "status": "ok"
    })

# -----------------------------------------------------------
# ADMIN: Update & Cache
# -----------------------------------------------------------
@app.route("/admin/cfb/update")
def admin_update():
    try:
        year = int(request.args.get("year", 2025))
        week = int(request.args.get("week", 10))
    except ValueError:
        return jsonify({"error": "year/week must be integers"}), 400
    result = update_weekly_cache(year, week)
    return jsonify(result)

# -----------------------------------------------------------
# CACHE READ
# -----------------------------------------------------------
@app.route("/cfb/cache")
def cache_info():
    try:
        year = int(request.args.get("year", 2025))
        week = int(request.args.get("week", 10))
    except ValueError:
        return jsonify({"error": "year/week must be integers"}), 400
    return jsonify(read_from_cache(year, week))

# -----------------------------------------------------------
# TEAM STATS (from cache)
# -----------------------------------------------------------
@app.route("/cfb/team")
def cfb_team():
    name = request.args.get("name", "")
    try:
        year = int(request.args.get("year", 2025))
        week = int(request.args.get("week", 10))
    except ValueError:
        return jsonify({"error": "year/week must be integers"}), 400
    if not name:
        return jsonify({"error": "missing ?name="}), 400
    return jsonify(get_team_from_cache(year, week, name))

# optional alias
@app.route("/fetch/cfb/team")
def fetch_cfb_team_alias():
    return cfb_team()

# -----------------------------------------------------------
# WEATHER (Open-Meteo)
# -----------------------------------------------------------
@app.route("/cfb/weather")
def cfb_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "missing lat/lon parameters"}), 400
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return jsonify({"error": "lat/lon must be numeric"}), 400
    return jsonify(get_weather(lat, lon))

# -----------------------------------------------------------
# ODDS / TOTALS (TheOddsAPI)
# -----------------------------------------------------------
@app.route("/cfb/odds")
def cfb_odds():
    year = request.args.get("year", 2025)
    week = request.args.get("week", 10)
    try:
        data = get_odds_totals(week, year)
        return jsonify(data)
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch odds: {str(e)}",
            "note": "If TheOddsAPI free tier was exceeded, recheck your API key or add a fallback cache."
        }), 500

# -----------------------------------------------------------
# TEMPO / DRIVE PACE
# -----------------------------------------------------------
@app.route("/cfb/tempo")
def cfb_tempo():
    team = request.args.get("team")
    if not team:
        return jsonify({"error": "missing ?team="}), 400
    try:
        data = get_tempo(team)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"tempo fetch failed: {str(e)}"}), 500

# -----------------------------------------------------------
# INJURIES (ESPN scrape)
# -----------------------------------------------------------
@app.route("/cfb/injuries")
def cfb_injuries():
    team = request.args.get("team")
    if not team:
        return jsonify({"error": "missing ?team="}), 400
    try:
        data = get_injuries(team)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"injury scrape failed: {str(e)}"}), 500

# -----------------------------------------------------------
# HEALTH CHECK
# -----------------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"ok": True, "ts": int(time.time())})

# -----------------------------------------------------------
# Warmup
# -----------------------------------------------------------

@app.route("/warm", methods=["POST"])
def warm_endpoint():
    data = request.get_json(force=True)
    team = data.get("team")
    opp = data.get("opp")
    year = int(data.get("year"))
    week = data.get("week")
    lat = float(data.get("lat"))
    lon = float(data.get("lon"))
    kickoff = data.get("kickoff")
    result = warm_game(team, opp, year, week, lat, lon, kickoff)
    return jsonify(result)


# -----------------------------------------------------------
# RUN SERVER
# -----------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
