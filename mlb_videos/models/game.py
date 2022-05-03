import os
import pandas as pd
import logging
import logging.config

from sources.statsapi import StatsAPI
import constants as Constants

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

class Game:
    def __init__(self, game_pk: int = 0):
        self.game_pk = game_pk
        self.full_data = {}
        self.clean_data = {}
        self.df = pd.DataFrame()
        self.get_initial_data()
        self.parse_data()
        #self.create_df()
        
    def get_initial_data(self):
        """
        """
        self.full_data = StatsAPI.Game(
            game_pk = self.game_pk
        ).get_data()
        
    def parse_data(self):
        """Working with the slightly limited JSON returned by API
        Will iterate through each key in the Constants.Game.Routes dict
        Passing final result to clean_data
        """
        for k, v in Constants.Game.Routes.items():
            iter_data = self.full_data[k]
            if not v.Custom:
                [self.clean_data.update(
                    {c.lower():iter_data[c]}
                ) for c in v.Columns]
            elif k == 'Umpires':
                for ump in v.Columns:
                    ump_clean = f'{ump.replace(" ","").lower()}_ump'
                    self.clean_data.update({
                        ump_clean: [x['official']['fullName']
                        for x in iter_data \
                        if x['officialType'] == ump][0]
                    })

    def create_df(self):
        """
        """
        self.df = pd.DataFrame([self.clean_data])

    def get_data(self):
        """
        """
        return self.clean_data

    def get_df(self):
        """
        """
        return self.df
