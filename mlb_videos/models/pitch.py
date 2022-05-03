import os
#from sqlite3 import TimestampFromTicks
import swifter
import pandas as pd
import logging
import logging.config

#from tqdm import tqdm
#from collections import namedtuple
from models.game import Game
from models.player import Player
from models.team import Team
from models.video import Video

from analysis.pitch_movement import COLS as PM_COLS, calculate_movement
from analysis.ump_calls import COLS as UMP_COLS, calculate_miss

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

class Pitches:
    """
    """

    def __init__(self, df):
        """Pitches collection initialized by DF
        Where each row represents a pitch & metadata
        """
        self.df = df
        self.orig_df = pd.DataFrame
        logging.info(f'Initialized Pitches object: {len(df)} rows..')

    def backup_df(self):
        """
        """
        self.orig_df = self.df.copy()

    def calculate_missed_calls(self):
        """
        """
        logging.info(f'Calculating missed calls..')
        self.df[UMP_COLS] = self.df.swifter.apply(
            lambda x: calculate_miss(x),
            axis = 1,
            result_type = 'expand'
        )
        logging.info(f'Completed calculation of missed calls')

    def calculate_movement(self):
        """
        """
        logging.info(f'Starting movement..')
        self.df[PM_COLS] = self.df.swifter.apply(
            lambda x:calculate_movement(x),
            axis = 1,
            result_type = 'expand'
        )
        logging.info(f'Completed calculation of pitch movement..')

    def add_game_info(self):
        """
        """
        logging.info(f'Adding game info..')
        game_list = self.df[['game_pk']].drop_duplicates()['game_pk'].to_list()
        games = []

        for g in game_list:
            games.append(Game(g).get_data())
        game_df = pd.DataFrame(games)

        self.df = self.df.merge(game_df, left_on='game_pk', right_on='pk') 
        logging.info(f'Added game info for {len(game_df)} game(s)..')
    
    def add_player_info(self, batters: bool = True, pitchers: bool = True,
                        socials: bool = False):
        """
        """
        logging.info(
            'Adding player info..\n' + 
            f'PARAMS: batters:{batters}, pitchers:{pitchers}, socials:{socials}'
        )
        player_iterations = [('batter',batters),('pitcher',pitchers)]

        for player_type in [x[0] for x in player_iterations if x[1]]:

            player_list = self.df[[player_type]].drop_duplicates()[player_type].to_list()
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
        logging.info(f'Completed adding player info for {len(player_df)} player(s)..')

    def add_team_info(self):
        """Add a few team-related fields to the DF
            - full name, division, etc.
            - important element are the hashtags / twitter accounts
            - our tweets WILL be generated using some items from here
        """
        team_iterations = ['home_team','away_team']

        for team_type in team_iterations:

            team_list = self.df[[team_type]].drop_duplicates()[team_type].to_list()
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
        logging.info(f'Added team info..')

    def get_videos(self):
        """
        """
        logging.info(f'Starting video search & download for {len(self.df)} pitches..')
        wrk = self.df.copy()
        wrk['video_path'] = None
        for index, row in wrk.iterrows():
            iter_v = Video(
                row.to_dict()
            )
            iter_v.download()
            wrk.at[index,'video_path'] = iter_v.get_fp()
            logging.info(f'Completed download for video - {iter_v.play_id} - {index} of {len(wrk)}..')
        self.df = wrk
        logging.info(f'Completed video search & download for ALL pitches..')

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