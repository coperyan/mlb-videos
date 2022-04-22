import os
import json
import pandas as pd

os.chdir('C:/Users/Ryan.Cope/Desktop/Dev/mlb_videos')

df = pd.read_csv('data/teams.csv')

teams = {}


for _, row in df.iterrows():
    d = row.to_dict()
    teams[d['abbreviation']] = d

with open('teams.json','w') as f:
    json.dump(teams,f)
    