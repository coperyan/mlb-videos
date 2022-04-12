import os
import json
from datetime import datetime, timedelta

os.chdir('/Users/rcope/Desktop/Dev/mlb_videos')

from Statcast import StatcastClient
from Video import StatcastVideos
from analysis.UmpCalls import get_misses

with open('config.json') as f:
    CONFIG = json.load(f)

yesterday = (datetime.now() - timedelta(days=2)).strftime(CONFIG['helpers']['date_format'])

statcast = StatcastClient(start_date=yesterday,end_date=yesterday)
statcast_df = statcast.get_df()