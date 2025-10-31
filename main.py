import os
import time
from flask import Flask, jsonify, request
from modules.cfb_data import get_cfbd_team, get_sportsdata_team_stats

app = Flask(__name__)

@app.route("/")
def root():
    return jsonify({
        "message": "College Football Data API is running.",
        "endpoints": {
            "cfbd_team": "/fetch/cfb/team?name=TeamName&year=YYYY",
            "sportsdata_team": "/fetch/cfb/teamstats?name=TeamName",
            "health": "/health"
        },
        "status": "ok"
    })

# ---- CollegeFootballData endpoint ----
@app.route("/fetch/cfb/team")
def cfbd_team():
    name = request.args.get("name")
    year = request.args.get("year", 2024)
    if not name:
        return jsonify({"error": "missing ?name= parameter"})
    return jsonify(get_cfbd_team(name, year))

# ---- SportsData.io endpoint ----
@app.route("/fetch/cfb/teamstats")
def sportsdata_team():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "missing ?name= parameter"})
    return jsonify(get_sportsdata_team_stats(name))

@app.route("/health")
def health():
    return jsonify({"ok": True, "ts": int(time.time())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
