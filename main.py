import os
import time
from flask import Flask, jsonify, request
from modules.cfb_sportsipy import get_cfb_games, get_cfb_team, get_cfb_boxscore

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "College Football Data Scraper (Sportsipy) is running.",
        "status": "ok",
        "endpoints": {
            "cfb_games": "/scrape/cfb/games?date=YYYYMMDD",
            "cfb_team": "/scrape/cfb/team?name=TeamName&year=YYYY",
            "cfb_boxscore": "/scrape/cfb/boxscore?id=BoxscoreID",
            "health": "/health"
        }
    })

@app.route("/scrape/cfb/games")
def scrape_cf_
