import os

from mlb_videos import Statcast

# test = Statcast.Search(start_date="2023-10-01", end_date="2023-10-10")
test = Statcast.Search(start_date="2023-10-01", descriptions=["called_strike"])

df = test.execute()
