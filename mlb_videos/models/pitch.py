import os
#from sqlite3 import TimestampFromTicks
import swifter
import pandas as pd

#from tqdm import tqdm
#from collections import namedtuple

from models.game import Game
from models.player import Player
from models.Team import Team
from models.video import Video

from analysis.pitch_movement import COLS as PM_COLS, calculate_movement
from analysis.ump_calls import COLS as UMP_COLS, calculate_miss


class Pitches:

    def __init__(self, df):
        """Pitches collection initialized by DF
        Where each row represents a pitch & metadata
        """
        self.df = df
        self.orig_df = pd.DataFrame

    def backup_df(self):
        """
        """
        self.orig_df = self.df.copy()

    def calculate_missed_calls(self):
        """
        """
        self.df[UMP_COLS] = self.df.swifter.apply(
            lambda x: calculate_miss(x),
            axis = 1,
            result_type = 'expand'
        )

    def calculate_movement(self):
        """
        """
        self.df[PM_COLS] = self.df.swifter.apply(
            lambda x:calculate_movement(x),
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
    
    def add_player_info(self, batters: bool = True, pitchers: bool = True,
                        socials: bool = False):
        """
        """
        player_iterations = [('batter',batters),('pitcher',pitchers)]

        for player_type in [x[0] for x in player_iterations if x[1]]:

            player_list = self.df[self.df[player_type]].drop_duplicates()[player_type].to_list()
            players = []

            for player in player_list:
                players.append(Player(player,socials).get_data())
            
            player_df = pd.DataFrame(players)
            player_df.rename(
                columns={c:f'{player_type}_{c}'
                for c in player_df.columns.values},
                inplace = True
            )
            self.df = self.df.merge(
                player_df, left_on = player_type, right_on = f'{player_type}_id'
            )

    def add_team_info(self):
        """Add a few team-related fields to the DF
            - full name, division, etc.
            - important element are the hashtags / twitter accounts
            - our tweets WILL be generated using some items from here
        """
        team_iterations = ['home_team','away_team']

        for team_type in team_iterations:

            team_list = self.df[self.df[team_type]].drop_duplicates()[[team_type]].tolist()
            teams = []

            for team in team_list:
                teams.append(Team(team).get_data())

            team_df = pd.DataFrame(teams)
            team_df.rename(
                columns={c:f'{team_type}_{c}'
                for c in team_df.columns.values},
                inplace = True
            )
            self.df = self.df.merge(
                team_df,left_on=team_type,right_on=f'{team_type}_abbreviation'
            )

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