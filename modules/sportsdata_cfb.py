import os
import time
import requests

# Load SportsData.io API key from Render's environment variables
SPORTSDATA_KEY = os.getenv("SPORTSDATA_API_KEY")

# Base URL for all College Football endpoints
BASE_URL = "https://api.sportsdata.io/v4/cfb/scores/json"


def get_sportsdata_team_stats(team_name: str):
    """
    Fetches basic College Football team stats from SportsData.io
    Example: get_sportsdata_team_stats("Georgia")
    """

    if not SPORTSDATA_KEY:
        return {"error": "Missing SPORTS_DATA_API_KEY", "source": "sportsdata.io"}

    url = f"{BASE_URL}/Teams"
    headers = {"Ocp-Apim-Subscription-Key": SPORTSDATA_KEY}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {
                "error": f"SportsData.io error {response.status_code}",
                "content": response.text
            }

        teams = response.json()
        for team in teams:
            name = team.get("Name", "")
            if team_name.lower() in name.lower():
                return {
                    "source": "sportsdata.io",
                    "team": team.get("Name"),
                    "conference": team.get("Conference"),
                    "stadium": team.get("StadiumDetails", {}).get("Name"),
                    "city": team.get("StadiumDetails", {}).get("City"),
                    "state": team.get("StadiumDetails", {}).get("State"),
                    "wins": team.get("Wins"),
                    "losses": team.get("Losses"),
                    "abbreviation": team.get("Key"),
                    "team_id": team.get("TeamID"),
                    "timestamp": int(time.time())
                }

        return {"error": "No team found", "match": None}

    except Exception as e:
        return {"error": str(e), "source": "sportsdata.io"}
