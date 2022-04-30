import os

os.chdir('mlb_videos')

from clients.statcast import Statcast
from models.pitch import Pitches

sc = Statcast(start_dt = '2022-04-29', end_dt = '2022-04-29').get_df()
p = Pitches(sc)
p.calculate_missed_calls()
p.rank_pitches(
    partition_by = ['game_pk'],
    order_by = ['total_miss'],
    ascending = False,
    name = 'total_miss_game_rank'
)
