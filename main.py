import os
import time
from flask import Flask, jsonify, request
from modules.cfb_data import get_cfbd_team
from modules.cfb_batch import update_weekly_cache, read_from_cache, get_team_from_cache

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "CFB weekly cache service (batch + normalization)",
        "endpoints": {
            "admin_update": "/admin/cfb/update?year=2025&week=10",
            "cache_info":  "/cfb/cache?year=2025&week=10",
            "team":        "/cfb/team?name=Georgia&year=2025&week=10",
        },
        "status": "ok"
    })

@app.route("/admin/cfb/update")
def admin_update():
    try:
        year = int(request.args.get("year", 2025))
        week = int(request.args.get("week", 10))
    except ValueError:
        return jsonify({"error": "year/week must be integers"}), 400
    result = update_weekly_cache(year, week)
    return jsonify(result)

@app.route("/cfb/cache")
def cache_info():
    try:
        year = int(request.args.get("year", 2025))
        week = int(request.args.get("week", 10))
    except ValueError:
        return jsonify({"error": "year/week must be integers"}), 400
    return jsonify(read_from_cache(year, week))

# ---- CollegeFootballData.io ----
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

@app.route("/health")
def health():
    return jsonify({"ok": True, "ts": int(time.time())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
