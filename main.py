import os
import time
from flask import Flask, jsonify
from modules.espn_nfl import get_nfl_data
from modules.espn_nfl_teamstats import get_nfl_teamstats
from modules.espn_nfl_standings import get_nfl_standings  # optional, if already exists

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Sports Data Scraper is running.",
        "endpoints": {
            "nfl": "/scrape/nfl",
            "teamstats": "/scrape/nfl/teamstats",
            "standings": "/scrape/nfl/standings",
            "health": "/health"
        },
        "status": "ok"
    })

@app.route("/scrape/nfl")
def scrape_nfl():
    """Fetch live NFL data from ESPN."""
    data = get_nfl_data()
    return jsonify(data)

@app.route("/scrape/nfl/teamstats")
def scrape_nfl_teamstats():
    """Fetch NFL team stats."""
    return jsonify(get_nfl_teamstats())

@app.route("/scrape/nfl/standings")
def scrape_nfl_standings():
    """Fetch NFL standings."""
    return jsonify(get_nfl_standings())

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"ok": True, "ts": int(time.time())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
