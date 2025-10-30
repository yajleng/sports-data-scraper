import os
import time
from flask import Flask, jsonify
from modules.espn_nfl import get_nfl_data  # import the scraper function
from modules.espn_nfl_standings import get_nfl_standings

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Sports Data Scraper is running.",
        "endpoints": {
            "nfl": "/scrape/nfl",
            "health": "/health"
        },
        "status": "ok"
    })

@app.route("/scrape/nfl")
def scrape_nfl():
    """Fetch live NFL data from ESPN."""
    data = get_nfl_data()
    return jsonify(data)

@app.route("/health")
def health():
    return jsonify({"ok": True, "ts": int(time.time())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
