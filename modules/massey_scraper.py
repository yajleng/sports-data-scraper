import os
import json
import datetime
import pandas as pd

CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "massey_cache.json")
CSV_FALLBACK = os.path.join(os.path.dirname(__file__), "..", "data", "massey_snapshot.csv")


def fetch_massey_ratings():
    """
    Fetch or load Massey College Football Power Ratings.
    Prefers cache → live scrape (disabled here) → static CSV fallback.
    """

    # 1️⃣ Check for recent JSON cache first
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            return {"source": "cached", **cached}
        except Exception:
            pass  # if corrupted, proceed to CSV fallback

    # 2️⃣ CSV fallback (weekly static snapshot)
    if os.path.exists(CSV_FALLBACK):
        try:
            df = pd.read_csv(CSV_FALLBACK)
            df = df.rename(columns=str.lower)
            records = df.to_dict(orient="records")

            # save to cache for consistency
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "ts": datetime.datetime.utcnow().isoformat(),
                    "count": len(records),
                    "ratings": records
                }, f, indent=2)

            return {"source": "csv_fallback", "count": len(records), "ratings": records}
        except Exception as e:
            return {"error": f"CSV fallback failed: {str(e)}"}

    # 3️⃣ If nothing exists
    return {"error": "No live scrape, cache, or CSV snapshot found."}
