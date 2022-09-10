import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import logging.config

import constants as Constants

logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)

GAME_URL = "https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
PLAYER_URL = "https://statsapi.mlb.com/api/v1/people/{id}"
PLAYER_SITE_URL = "https://www.mlb.com/player/{ns}"

SOCIALS = [
    {"name": "twitter", "repl": "https://twitter.com/@"},
    {"name": "instagram", "repl": "https://www.instagram.com/"},
]


class Game:
    def __init__(self, game_pk: int = None):
        """ """
        self.game_pk = game_pk
        self.json = {}
        self._make_api_request()

    def _make_api_request(self):
        """ """
        req_url = GAME_URL.format(game_pk=self.game_pk)
        resp = requests.get(req_url)
        self.json = resp.json()

    def get_full_json(self) -> dict:
        """ """
        return self.json

    def get_route(self, route: str = None) -> dict:
        """ """
        wrk = self.json.copy()
        try:
            for key in route:
                wrk = wrk.get(key, {})
            return wrk
        except Exception as e:
            print(f"Get Data Failed, Message: {e}")

    def get_data(self, routes: dict = Constants.Game.Routes) -> dict:
        """ """
        master_json = {}
        for k, v in routes.items():
            iter_json = self.get_route(v.Route)
            master_json[k] = iter_json
        self.master_json = master_json
        return self.master_json


class Player:
    def __init__(self, player_id: int = None):
        """ """
        self.player_id = player_id
        self.player_data = {}
        self._make_api_request()

    def _make_api_request(self):
        """ """
        req_url = PLAYER_URL.format(id=self.player_id)
        resp = requests.get(req_url)
        self.player_data = resp.json()["people"][0]

    def get_socials(self):
        """ """
        ns = self.player_data["nameSlug"]
        req_url = PLAYER_SITE_URL.format(ns=ns)
        resp = requests.get(req_url)
        soup = BeautifulSoup(resp.text, features="lxml")

        for s in SOCIALS:
            try:
                val = (
                    soup.find("li", {"class": s["name"]})
                    .find("a")["href"]
                    .replace(s["repl"], "")
                )
            except:
                val = None
            self.player_data[s["name"]] = val

    def get_data(self):
        """ """
        return self.player_data


# Either over-doing the OO or simplifying calls
# StatsAPI will be imported as a single reference
# Then will be able to call "Game" or "Player" with parameters as needed..
class StatsAPI:

    Game = Game
    Player = Player

    def __init__(self):
        """ """
