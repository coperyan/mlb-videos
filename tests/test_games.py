import os
import pandas as pd

from sources.statsapi import StatsAPI
import constants as Constants

games = [662797, 663364, 662288, 661534]
# test = StatsAPI.Game(662797).get_data()

# def parse_normal(d,r):
#     """
#     """
#     return {k:v for k, v in d.items() if k in _ROUTECOLS[r]}


class Game:
    def __init__(self, game_pk: int = 0):
        self.game_pk = game_pk
        self.full_data = {}
        self.clean_data = {}
        self.df = pd.DataFrame()
        self.get_initial_data()
        self.parse_data()

    def get_initial_data(self):
        """ """
        self.full_data = StatsAPI.Game(game_pk=self.game_pk).get_data()

    def parse_data(self):
        """Working with the slightly limited JSON returned by API
        Will iterate through each key in the Constants.Game.Routes dict
        Passing final result to clean_data
        """
        for k, v in Constants.Game.Routes.items():
            iter_data = self.full_data[k]
            if not v.Custom:
                [self.clean_data.update({c: iter_data[c]}) for c in v.Columns]
            elif k == "Umpires":
                for ump in v.Columns:
                    self.clean_data.update(
                        {
                            ump: [
                                x["official"]["fullName"]
                                for x in iter_data
                                if x["officialType"] == ump
                            ][0]
                        }
                    )


test = Game(game_pk=662797)
