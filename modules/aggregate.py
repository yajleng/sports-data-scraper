from modules import cfb_extended, odds_totals, weather_openmeteo

def aggregate_game_data(team, opponent, year, week):
    base = cfb_extended.get_team_metrics(team, year)
    odds = odds_totals.get_odds(team, opponent)
    weather = weather_openmeteo.get_weather(team, year, week)
    return {**base, **odds, **weather}
