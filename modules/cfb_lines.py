import requests, os

CFBD_API_KEY = os.getenv("CFBD_API_KEY")
BASE_URL = "https://api.collegefootballdata.com"

def get_historical_lines(year: int, week: int):
    url = f"{BASE_URL}/lines?year={year}&week={week}"
    headers = {"Authorization": f"Bearer {CFBD_API_KEY}"}
    resp = requests.get(url, headers=headers, timeout=10)
    return resp.json() if resp.ok else {"error": resp.text}
