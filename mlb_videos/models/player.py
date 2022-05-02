import os
import pandas as pd

from sources.statsapi import StatsAPI
import constants as Constants

players = [593428,543333,608700,641531]

class Player:
    def __init__(self, player_id: int = 0, socials: bool = False):
        self.player_id = player_id
        self.socials = socials
        self.full_data = {}
        self.clean_data = {}
        self.df = pd.DataFrame()
        self.get_initial_data()
        self.parse_data()

    def get_initial_data(self):
        """
        """
        p = StatsAPI.Player(
            player_id = self.player_id
        )
        if self.socials:
            p.get_socials()
        self.full_data = p.get_data()

    def parse_data(self):
        """
        """
        [self.clean_data.update(
            {c.lower():self.full_data[c]}
        ) for c in Constants.Player.Fields
        if c in self.full_data.keys()]

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