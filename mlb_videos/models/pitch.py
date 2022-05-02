import os
import swifter
import pandas as pd

#from tqdm import tqdm
#from collections import namedtuple

from analysis.ump_calls import COLS as UMP_COLS, calculate_miss
from models.game import Game
from models.player import Player
from models.video import Video

class Pitches:

    def __init__(self, df):
        """Pitches collection initialized by DF
        Where each row represents a pitch & metadata
        """
        self.df = df

    def calculate_missed_calls(self):
        """
        """
        self.df[UMP_COLS] = self.df.swifter.apply(
            lambda x: calculate_miss(x),
            axis = 1,
            result_type = 'expand'
        )

    def add_game_info(self):
        """
        """
        game_list = self.df[self.df['game_pk']].drop_duplicates()[['game_pk']]
        games = []

        for g in game_list:
            games.append(Game(g).get_data())
        game_df = pd.DataFrame(games)

        self.df = self.df.merge(game_df, left_on='game_pk', right_on='pk')      
    
    def add_player_info(self, batters: bool = False,
                        pitchers: bool = False, socials: bool = False):
        """
        """
        if batters:
            batter_list = self.df[self.df['batter']].drop_duplicates()[['batter']]
            batters = []
            
            for b in batter_list:
                batters.append(Player(b,socials).get_data())
            batter_df = pd.DataFrame(batters)

            self.df = self.df.merge(batter_df, left_on='batter', right_on='player_id')

        if pitchers:
            pitcher_list = self.df[self.df['pitcher']].drop_duplicates()[['pitcher']]
            pitchers = []
            
            for p in pitcher_list:
                pitchers.append(Player(p,socials).get_data())
            pitcher_df = pd.DataFrame(pitchers)

            self.df = self.df.merge(pitcher_df, left_on='pitcher', right_on='player_id')

    def get_videos(self):
        """
        """
        wrk = self.df.copy()
        wrk['video_path'] = None
        for index, row in wrk.iterrows():
            iter_v = Video(
                row.to_dict()
            )
            iter_v.download()
            wrk.at[index,iter_v.get_fp()]
        self.df = wrk

    def rank_pitches(self, partition_by: list = [], order_by: str = None,
                    ascending: bool = False, name: str = None):
        """
        """
        wrk = self.df.copy()
        wrk[name] = wrk.groupby(partition_by)[order_by].rank(
            method = 'first', ascending = ascending
        )
        wrk = wrk.sort_values(by=name, ascending=True)
        wrk = wrk.reset_index(drop=True)
        
        self.df = wrk

    def get_df(self):
        """
        """
        return self.df