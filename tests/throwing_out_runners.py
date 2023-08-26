import os
from mlb_videos import Statcast

df = Statcast(start_date="2023-03-01", end_date="2023-08-18").get_df()
df = df.query("fielder_2 == 672275")


import requests

base_url = "https://statsapi.mlb.com/api/"


req = requests.get(base_url + f"1.6.2/game/{717731}/playByPlay")


# Leaderboard
leaderboard = "https://baseballsavant.mlb.com/leaderboard/catcher-throwing?game_type=Regular&n=1&season_end=2023&season_start=2023&split=no&team=&type=Cat&with_team_only=1&csv=true"
detail_for_player = "https://baseballsavant.mlb.com/leaderboard/services/catcher-throwing/672515?game_type=Regular&n=1&season_end=2023&season_start=2023&split=no&team=&type=Cat&with_team_only=1"

test = requests.get(
    # "https://baseballsavant.mlb.com/leaderboard/services/catcher-throwing/672515?season_start=&season_end=&team="
    # "https://baseballsavant.mlb.com/leaderboard/services/catcher-throwing/672515"
    leaderboard
)
resp = test.json()
