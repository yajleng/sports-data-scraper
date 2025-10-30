import time
from sportsipy.ncaaf.boxscore import Boxscores, Boxscore
from sportsipy.ncaaf.teams import Teams

def _ts():
    return int(time.time())

def get_cfb_games(date_yyyymmdd):
    data = Boxscores(int(date_yyyymmdd)).games
    games = []
    for _, games_list in data.items():
        for g in games_list:
            games.append({
                "id": g.get("boxscore"),
                "away": g.get("away_name"),
                "home": g.get("home_name"),
                "away_score": g.get("away_score"),
                "home_score": g.get("home_score"),
                "start_time": g.get("time"),
                "venue": g.get("location"),
                "status": g.get("non_di")
            })
    return {"source":"sportsipy","sport":"NCAAF","date":date_yyyymmdd,"game_count":len(games),"games":games,"timestamp":_ts()}

def get_cfb_team(team_query, year=None):
    teams = Teams(year)
    target = None
    q = team_query.lower()
    for t in teams:
        if q in t.name.lower() or q == t.abbreviation.lower():
            target = t
            break
    if not target:
        return {"source":"sportsipy","sport":"NCAAF","match":None,"timestamp":_ts()}
    return {
        "source":"sportsipy",
        "sport":"NCAAF",
        "match":{
            "name": target.name,
            "abbreviation": target.abbreviation,
            "conference": target.conference,
            "wins": target.wins,
            "losses": target.losses,
            "points_for": target.points_for,
            "points_against": target.points_against,
            "simple_rating_system": target.simple_rating_system,
            "year": target.year
        },
        "timestamp": _ts()
    }

def get_cfb_boxscore(game_id):
    b = Boxscore(game_id)
    return {
        "source":"sportsipy",
        "sport":"NCAAF",
        "game_id": b.boxscore_index,
        "away":{"name": b.away_name, "points": b.away_points},
        "home":{"name": b.home_name, "points": b.home_points},
        "timestamp": _ts()
    }
