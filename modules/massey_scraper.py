from requests_html import HTMLSession
import os, json, datetime

CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "massey_cache.json")

def fetch_massey_ratings():
    """Scrape and cache Massey college football team ratings."""
    try:
        session = HTMLSession()
        r = session.get("https://masseyratings.com/cf/compare.htm")
        r.html.render(timeout=30)  # render JS

        table = r.html.find("table tbody tr")
        ratings = []

        for row in table[:25]:
            cols = [c.text.strip() for c in row.find("td")]
            if len(cols) >= 5:
                ratings.append({
                    "rank": cols[0],
                    "team": cols[1],
                    "power": cols[2],
                    "offense": cols[3],
                    "defense": cols[4]
                })

        # Cache result
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "ts": datetime.datetime.utcnow().isoformat(),
                "count": len(ratings),
                "ratings": ratings
            }, f, indent=2)

        return {"source": "massey_live", "count": len(ratings), "ratings": ratings}

    except Exception as e:
        # fallback to cache
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            return {"source": "cached", **cached}
        return {"error": f"Failed to scrape and no cache found: {str(e)}"}
