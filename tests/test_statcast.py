import os

#os.chdir('mlb_videos')

from sources.statcast import Statcast
from sources.statsapi import StatsAPI
from models.pitch import Pitches

SEARCH_DATE = '2022-04-30'

#Get pitches from yesterday
#Backing up statcast for easy cache?
sc_df = Statcast(start_dt = SEARCH_DATE).get_df()
sc_df.to_csv('data/statcast.csv',index=False)

#Init pitch collection from data grabbed (essentially just a class with a DF)
p = Pitches(sc_df)
p.calculate_missed_calls()
p.rank_pitches(
    partition_by = ['game_date'], order_by = 'total_miss',
    ascending = False, name = 'total_miss_rank',
    ret_only = False
)
#Only keeping misses >= 2"
p.df = p.df[p.df['total_miss'] >= 2]