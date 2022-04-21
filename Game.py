import os
import json
import requests
import pandas as pd

with open('config.json') as f:
    CONFIG = json.load(f)

GAME_URL = CONFIG['games']['game_url']
GAME_ROUTES = CONFIG['games']['routes']

class Game:
    def __init__(self, game_pk):
        self.game_pk = game_pk
        self.url = GAME_URL.format(game_pk = game_pk)
        self.get_game_data()

    def get_game_data(self):
        """
        """
        r = requests.get(self.url)
        self.json = r.json()
        self.df = pd.DataFrame(self.json)

    def get_full_json(self):
        """
        """
        return self.json

    def get_data(self, data):
        """
        """
        r_json = self.json
        try:
            for key in CONFIG['game_data'][data]:
                r_json = r_json.get(key,{})
        except:
            print('Issue parsing JSON, returning full..')
        
        return r_json