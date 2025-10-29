import os
import time
import requests
from flask import Flask, jsonify
from bs4 import BeautifulSoup
from modules.espn_nfl import get_nfl_data  # <-- Import our NFL module

app = Flask(__name__)

# ----------------------------------------
# Default test route
# ----------------------------------------
@app.route("/scrape")
def scrape():
    url = "https://www.espn.com/college-football/"
    r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "lxml")
    headlines = [h.get_text(strip=True) for h in soup.select("section h1, section h2")][:5]
    return jsonify({
        "source": "espn",
        "timestamp": int(time.time()),
        "headlines_sample": headlines
    })

# ----------------------------------------
# NFL data route
# ----------------------------------------
@app.route("/scrape/nfl")
def scrape_nfl():
    """Return live NFL data from ESPN API"""
    data = get_nfl_data()
    return jsonify(data)

# ----------------------------------------
# Health route
# ----------------------------------------
@app.route("/health")
def health():
    return jsonify({"ok": True, "ts": int(time.time())})

# ----------------------------------------
# Flask runner
# ----------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
