import os
import json
import time

CACHE_DIR = "cache"
CACHE_TTL = 6 * 3600  # 6 hours

def _path(name: str):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{name}.json")

def load_cache(name: str):
    path = _path(name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if time.time() - data.get("_ts", 0) < CACHE_TTL:
            return data.get("payload")
    except Exception:
        pass
    return None

def save_cache(name: str, payload):
    try:
        with open(_path(name), "w", encoding="utf-8") as f:
            json.dump({"_ts": time.time(), "payload": payload}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
