import os, requests, time
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

def run_scrape():
    url = "https://www.espn.com/college-football/"
    r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    headlines = [h.get_text(strip=True) for h in soup.select("section h1, section h2")][:5]
    return {
        "source": "espn",
        "timestamp": int(time.time()),
        "headlines_sample": headlines
    }

@app.route("/scrape")
def scrape():
    return jsonify(run_scrape())

@app.route("/health")
def health():
    return jsonify({"ok": True, "ts": int(time.time())})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
