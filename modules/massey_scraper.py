import os
import json
import datetime
import pandas as pd

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # one level up (to repo root)
CACHE_FILE = os.path.join(BASE_DIR, "massey_cache.json")
CSV_FALLBACK = os.path.join(BASE_DIR, "massey_snapshot.csv")


def fetch_massey_ratings():
    """
    Fetch or load Massey College Football Power Ratings.
    Prefers cache → static CSV fallback (weekly snapshot).
    """

    # 1️⃣ Check for existing cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            return {"source": "cached", **cached}
        except Exception:
            pass

    # 2️⃣ CSV fallback (root-level file)
    if os.path.exists(CSV_FALLBACK):
        try:
            df = pd.read_csv(CSV_FALLBACK)
            df = df.rename(columns=str.lower)
            records = df.to_dict(orient="records")

            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "ts": datetime.datetime.utcnow().isoformat(),
                    "count": len(records),
                    "ratings": records
                }, f, indent=2)

            return {"source": "csv_fallback", "count": len(records), "ratings": records}
        except Exception as e:
            return {"error": f"CSV fallback failed: {str(e)}"}

    # 3️⃣ No cache or CSV found
    return {"error": "No cache or CSV snapshot found."}
