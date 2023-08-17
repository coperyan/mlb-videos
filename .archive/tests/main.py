import os


from filmroom import Video
from statcast import Statcast
from statsapi import Game, Player


statcast_data = Statcast(
    start_date="2023-07-28", end_date="2023-07-28", transform=["umpire_calls"]
)
statcast_df = statcast_data.df
statcast_df = statcast_df[statcast_df["total_miss"] > 0.00]
statcast_df["total_miss_rank"] = statcast_df["total_miss"].rank(
    method="first", ascending=False
)
statcast_df = statcast_df.sort_values(
    by=["total_miss_rank"], ascending=True
).reset_index()
video_df = statcast_df[statcast_df["total_miss_rank"] <= 10]
videos = []
for index, row in video_df.iterrows():
    videos.append(Video(pitch=row, download=True, download_path="data"))
