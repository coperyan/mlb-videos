import os
import json
import pandas as pd
from datetime import datetime, timedelta

os.chdir('C:/Users/Ryan.Cope/Desktop/Dev/mlb_videos')
from Game import Game
from Helpers import get_player_name, get_player_twitter, get_team_attribute

video_df = pd.read_csv('downloads/video_df.csv')

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
    f'Umpire {hp_ump} was responsible for the largest miss yesterday. This ' + 
    ('strike call' if worst_miss['description'] == 'called_strike' else 'missed call') + 
    (f'@{hitter_twitter}' if hitter_twitter else f'{hitter_name}') + f' missed by ' + 
    f'{worst_miss["total_miss"]} inches.\n\n' + 
    f'#{h_hashtag} #{a_hashtag} #{vs_1} #{vs_2}'
)