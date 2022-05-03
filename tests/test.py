import os
#os.chdir('mlb_videos')

from sources.statcast import Statcast
from models.pitch import Pitches

SEARCH_DATE = '2022-05-01'

#Get pitches from yesterday
#Backing up statcast for easy cache?
sc_df = Statcast(start_dt = SEARCH_DATE).get_df()
sc_df.to_csv('data/statcast.csv',index=False)

#Init pitch collection from data grabbed (essentially just a class with a DF)
p = Pitches(sc_df)
p.calculate_missed_calls()
p.rank_pitches(
    partition_by = ['game_date'], order_by = 'total_miss',
    ascending = False, name = 'total_miss_rank'
)
#Only keeping misses >= 2"
p.df = p.df[p.df['total_miss'] >= 2].reset_index(drop=True)
p.df.to_csv('data/misses.csv',index=False)

#Next, grab videos?
p.get_videos()

#Add more info
p.add_game_info()
p.add_player_info(batters = True, pitchers = False, socials = False)
p.add_team_info()

p.df.to_csv('data/full.csv',index=False)