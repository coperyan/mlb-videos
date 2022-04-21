import os
import json
from datetime import datetime, timedelta

os.chdir('C:/Users/Ryan.Cope/Desktop/Dev/mlb_videos')

from Game import Game
from Helpers import get_player_name, get_player_twitter, get_team_attribute
from Statcast import StatcastClient
from StatcastVideo import StatcastVideos
from VideoCompilation import VideoCompilation
from analysis.UmpCalls import get_misses

with open('config.json') as f:
    CONFIG = json.load(f)

purge_files = True
if purge_files:
    for x in os.listdir('downloads'):
        os.remove(os.path.join('downloads',x))

yesterday = (datetime.now() - timedelta(days=1)).strftime(CONFIG['helpers']['date_format'])

statcast = StatcastClient(start_date=yesterday,end_date=yesterday)
statcast_df = statcast.get_df()
statcast_df.to_csv('downloads/statcast_df.csv',index=False)

calls = ['ball','called_strike']
statcast_df[statcast_df['description'].isin(calls)]

missed_calls = get_misses(statcast_df)
missed_calls = missed_calls[missed_calls['total_miss'] >= 3.00]
missed_calls = missed_calls.sort_values(by=['total_miss'],ascending=False).reset_index(drop=True)
missed_calls.to_csv('downloads/missed_calls.csv',index=False)

#Downloading videos (worst strikes)
video_df = StatcastVideos(feed = 'best', dl=True, statcast_df = missed_calls).get_df()
video_df.to_csv('downloads/video_df.csv',index=False)

#Create video compilation
vc = VideoCompilation(dt=yesterday)

#Pick out worst clip?
worst_miss = video_df.iloc[0].to_dict()
worst_miss_game = Game(game_pk = worst_miss['game_pk'])
game_json = worst_miss_game.get_full_json()
ump_path = ["liveData", "boxscore", "officials"]
ij = game_json.copy()
for key in ump_path:
    ij = ij.get(key,{})
hp_ump = next(x['official']['fullName'] for x in ij if x['officialType'] == 'Home Plate')
hitter_name = get_player_name(worst_miss['batter'])
hitter_twitter = get_player_twitter(worst_miss['batter'])
h_hashtag = get_team_attribute(worst_miss['home_team'], 'hashtag')
a_hashtag = get_team_attribute(worst_miss['away_team'], 'hashtag')
vs_1 = f'{worst_miss["home_team"]}vs{worst_miss["away_team"]}'
vs_2 = f'{worst_miss["away_team"]}vs{worst_miss["home_team"]}'

test_msg = (
    f'Umpire {hp_ump} was responsible for the largest miss yesterday. This pitch to ' + 
    (f'@{hitter_twitter}' if hitter_twitter else f'{hitter_name}') + f' missed by ' + 
    f'{worst_miss["total_miss"]} inches.\n' + 
    f'#{h_hashtag} #{a_hashtag} #{vs_1} #{vs_2}'
)