import os
import time
from flask import Flask, jsonify, request
from modules.cfb_data import get_cfbd_team

app = Flask(__name__)

@app.route("/")
def root():
    return jsonify({
        "message": "College Football Data API is running.",
        "endpoints": {
            "cfbd_team": "/fetch/cfb/team?name=TeamName&year=YYYY",
            "health": "/health"
        },
        "status": "ok"
    })

# ---- CollegeFootballData.io ----
@app.route("/fetch/cfb/team")
def cfbd_team():
    name = request.args.get("name")
    year = request.args.get("year", 2024)
    if not name:
        return jsonify({"error": "Missing ?name= parameter"})
    return jsonify(get_cfbd_team(name, year))

@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "timestamp": int(time.time())
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
