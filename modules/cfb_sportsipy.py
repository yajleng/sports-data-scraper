from datetime import datetime
from sportsipy.ncaaf.teams import Teams
from sportsipy.ncaaf.boxscore import Boxscore
import difflib
import time

def get_cfb_games(date_str):
    try:
        # Convert YYYYMMDD → datetime
        date_obj = datetime.strptime(str(date_str), "%Y%m%d")
        teams = Teams(date_obj.year)
        games = []
        for team in teams:
            for game in team.schedule:
                if game.date == date_obj:
                    games.append({
                        "home_team": game.home_name,
                        "away_team": game.away_name,
                        "home_points": game.home_points,
                        "away_points": game.away_points,
                        "winner": game.winner,
                        "location": game.location,
                        "date": game.date.isoformat()
                    })
        return {
            "source": "sportsipy",
            "sport": "NCAAF",
            "game_count": len(games),
            "games": games,
            "timestamp": int(time.time())
        }
    except Exception as e:
        return {"error": str(e)}

def get_cfb_team(name, year):
    try:
        teams = Teams(year)
        all_names = [t.name for t in teams]
        match = difflib.get_close_matches(name, all_names, n=1)
        if not match:
            return {"match": None, "error": "No team found"}
        team = next(t for t in teams if t.name == match[0])
        data = {
            "source": "sportsipy",
            "sport": "NCAAF",
            "team": team.name,
            "abbreviation": team.abbreviation,
            "conference": team.conference,
            "wins": team.wins,
            "losses": team.losses,
            "points_for": team.points_for,
            "points_against": team.points_against,
            "offensive_rank": getattr(team, "offense_rank", None),
            "defensive_rank": getattr(team, "defense_rank", None),
            "timestamp": int(time.time())
        }
        return data
    except Exception as e:
        return {"error": str(e)}

def get_cfb_boxscore(boxscore_id):
    try:
        box = Boxscore(boxscore_id)
        return {
            "source": "sportsipy",
            "sport": "NCAAF",
            "home_team": box.home_name,
            "away_team": box.away_name,
            "home_score": box.home_points,
            "away_score": box.away_points,
            "winning_team": box.winner,
            "summary": box.summary,
            "timestamp": int(time.time())
        }
    except Exception as e:
        return {"error": str(e)}
