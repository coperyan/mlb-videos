import os
from mlb_videos import Statcast

df = Statcast(start_date="2023-03-01", end_date="2023-08-18").get_df()
df = df.query("fielder_2 == 672275")


import requests

base_url = "https://statsapi.mlb.com/api/"


req = requests.get(base_url + f"1.6.2/game/{717731}/playByPlay")
