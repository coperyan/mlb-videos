import os

os.chdir('mlb_videos')

from clients.statcast import Statcast
from clients.statsapi import StatsAPI
from models.pitch import Pitches

sc = Statcast(start_dt = '2022-04-29', end_dt = '2022-04-29').get_df()

batters = StatsAPI().get_players(
    player_list = sc[['batter']].drop_duplicates()['batter'].to_list(),
    socials = False
)
games = StatsAPI().get_games(
    game_list = sc[['game_pk']].drop_duplicates()['game_pk'].to_list()
)

p = Pitches(sc)
p.calculate_missed_calls()
p.rank_pitches(
    partition_by = ['game_pk'],
    order_by = ['total_miss'],
    ascending = False,
    name = 'total_miss_game_rank'
)


## Model this out?