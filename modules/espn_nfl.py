import requests
import time

# ESPN NFL API endpoint
SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

def get_nfl_data():
    """
    Fetches live NFL scoreboard data from ESPN's public API.
    Returns JSON-safe Python dictionary with game details.
    """
    try:
        # Request data from ESPN API
        r = requests.get(SCOREBOARD_URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()

        # Parse events
        events = data.get("events", [])
        games = []
        for e in events:
            competition = e.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])

            if len(competitors) == 2:
                home = competitors[0]
                away = competitors[1]

                games.append({
                    "home_team": home["team"]["displayName"],
                    "away_team": away["team"]["displayName"],
                    "home_score": home.get("score"),
                    "away_score": away.get("score"),
                    "status": competition.get("status", {}).get("type", {}).get("description"),
                    "venue": competition.get("venue", {}).get("fullName")
                })

        return {
            "sport": "NFL",
            "source": "espn",
            "timestamp": int(time.time()),
            "game_count": len(games),
            "games": games
        }

    except Exception as e:
        # Return error info if ESPN API call fails
        return {
            "error": str(e),
            "sport": "NFL",
            "timestamp": int(time.time())
        }
