import os
import requests
import time

CFBD_KEY = os.getenv("CFBD_API_KEY")
SPORTSDATA_KEY = os.getenv("SPORTSDATA_API_KEY")

# ---- CollegeFootballData API ----
def get_cfbd_team(team, year=2024):
    url = f"https://api.collegefootballdata.com/teams?year={year}"
    headers = {"Authorization": f"Bearer {CFBD_KEY}"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return {"error": f"CFBD error {r.status_code}", "content": r.text}

    data = r.json()
    match = next((t for t in data if team.lower() in t["school"].lower()), None)
    if not match:
        return {"error": "No team found", "match": None}

    return {
        "source": "collegefootballdata",
        "team": match["school"],
        "conference": match.get("conference"),
        "mascot": match.get("mascot"),
        "abbreviation": match.get("abbreviation"),
        "timestamp": int(time.time())
    }


# ---- SportsData.io API ----
def get_sportsdata_team_stats(team):
    url = "https://api.sportsdata.io/v4/cfb/scores/json/Teams"
    headers = {"Ocp-Apim-Subscription-Key": SPORTSDATA_KEY}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return {"error": f"SportsData error {r.status_code}", "content": r.text}

    data = r.json()
    match = next((t for t in data if team.lower() in t["School"].lower()), None)
    if not match:
        return {"error": "No team found", "match": None}

    return {
        "source": "sportsdata.io",
        "team": match["School"],
        "conference": match.get("Conference"),
        "stadium": match.get("StadiumDetails", {}).get("Name"),
        "team_id": match.get("TeamID"),
        "timestamp": int(time.time())
    }
