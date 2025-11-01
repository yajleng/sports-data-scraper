from pydantic import BaseModel

class GameSpread(BaseModel):
    team: str
    opponent: str
    spread: float
    win_prob: float
    edge: float
    weather_temp: float
    wind_speed: float
    injuries: int
