import os
import json
from datetime import datetime, timedelta

os.chdir('/Users/rcope/Desktop/Dev/mlb_videos')

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

calls = ['ball','called_strike']
statcast_df[statcast_df['description'].isin(calls)]

missed_calls = get_misses(statcast_df)
missed_calls = missed_calls[missed_calls['total_miss'] >= 3.00]
missed_calls = missed_calls.sort_values(by=['total_miss'],ascending=False).reset_index(drop=True)

#Downloading videos (worst strikes)
video_df = StatcastVideos(feed = 'best', dl=True, statcast_df = missed_calls)

vc = VideoCompilation(dt=yesterday)