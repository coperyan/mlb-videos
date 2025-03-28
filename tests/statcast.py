import os
import sys

sys.path.append(r"C:\Users\ryanc\Documents\Dev\rc\mlb-videos-dev-2025\mlb_videos")

from mlb_videos.statcast import Statcast
from mlb_videos.filmroom import FilmRoom

df = Statcast().search(
    analysis_types=["umpire_calls"],
    start_date="2025-03-27",
    end_date="2025-03-27",
    descriptions=["called_strike"],
    # events=["home_run"], teams=["SF"]
)
df = df.query("total_miss >= 3").reset_index(drop=True)
df = df.query("release_speed >= 65").reset_index(drop=True)
df = df.sort_values(by="total_miss", ascending=False)
df["total_miss_rank"] = 1
df["total_miss_rank"] = df["total_miss_rank"].cumsum()
df = df.reset_index(drop=True)

test = FilmRoom()
test.search(df.iloc[4])
