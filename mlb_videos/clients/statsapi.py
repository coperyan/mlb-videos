import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

_GAME_URL = 'https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live'
_PLAYER_URL = 'https://statsapi.mlb.com/api/v1/people/{id}'
_PLAYER_SITE_URL = 'https://www.mlb.com/player/{ns}'

_ROUTES = {
    'metadata': ['metaData'],
    'game': ['gameData','game'],
    'game_date': ['gameData','datetime'],
    'game_status': ['gameData','status'],
    'teams': ['gameData','teams'],
    'players': ['gameData','players'],
    'venue': ['gameData','venue'],
    'umpires': ['liveData','boxscore','officials'],
}
_SOCIALS = [
    {'name':'twitter','repl':'https://twitter.com/@'},
    {'name':'instagram','repl':'https://instagram.com/'}
]

class Game:

    DEFAULT_ROUTES = [
        'game',
        'game_date',
        'teams',
        'players',
        'venue',
        'umpires'
    ]

    def __init__(self, game_pk: int = None):
        """
        """
        self.game_pk = game_pk
        self.json = {}
        self._make_api_request()
    
    def _make_api_request(self):
        """
        """
        req_url = _GAME_URL.format(
            game_pk = self.game_pk
        )
        resp = requests.get(req_url)
        self.json = resp.json()

    def get_full_json(self) -> dict:
        """
        """
        return self.json

    def get_route(self, route: str = None) -> dict:
        """
        """
        wrk = self.json.copy()
        try:
            for key in _ROUTES[route]:
                wrk = wrk.get(key,{})
            return wrk
        except Exception as e:
            print(f'Get Data Failed, Message: {e}')

    def get_data(self, routes: list = DEFAULT_ROUTES) -> dict:
        """
        """
        master_json = {}
        for rte in routes:
            iter_json = self.get_route(rte)
            master_json[rte] = iter_json
        self.master_json = master_json
        return self.master_json

class Player:
    def __init__(self, player_id: int = None):
        """
        """
        self.player_id = player_id
        self.player_data = {}
        self._make_api_request()
    
    def _make_api_request(self):
        """
        """
        req_url = _PLAYER_URL.format(
            id = self.player_id
        )
        resp = requests.get(req_url)
        self.player_data = resp.json()['people'][0]

    def _get_socials(self):
        """
        """
        ns = self.player_data['nameSlug']
        req_url = _PLAYER_SITE_URL.format(
            ns = ns
        )
        resp = requests.get(req_url)
        soup = BeautifulSoup(resp.text)

        for s in _SOCIALS:
            try:
                val = soup.find('li',{'class':s['name']}).find('a')['href'].replace(s['repl'],'')
            except:
                val = None
            self.player_data[s['name']] = val

    def get_data(self):
        """
        """
        return self.player_data

class StatsAPI:
    def __init__(self):
        """
        """
    def get_player(self, player_id: int = None, socials: bool = True) -> dict:
        """
        """
        p = Player(player_id)
        if socials:
            p._get_socials()
        return p.get_data()

    def get_game(self, game_pk: int = None) -> dict:
        """
        """
        g = Game(game_pk)
        return g.get_data()

    def get_players(self, player_list: list = [], socials: bool = True) -> list:
        """
        """
        r_list = []
        for p in player_list:
            r_list.append(
                self.get_player(player_id = p, socials = socials)
            )
        return r_list

    def get_games(self, game_list: list = []):
        """
        """
        g_list = []
        for g in game_list:
            g_list.append(
                self.get_game(game_pk = g)
            )
        return g_list
        

