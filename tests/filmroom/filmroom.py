import os

from mlb_videos import Statcast
from mlb_videos import FilmRoom


statcast_client = Statcast.Search(
    start_date="2023-10-01", end_date="2023-10-15", events="home run"
)

statcast_df = statcast_client.execute()
statcast_df = statcast_df.sort_values(
    by=["hit_distance_sc"], ascending=False
).reset_index(drop=True)

test_pitch = statcast_df.iloc[0]

filmroom_client = FilmRoom.API()
search_plays = filmroom_client.search_plays(test_pitch)
search_clips = filmroom_client.search_clips(search_plays[0])
download_clip = filmroom_client.download(
    search_clips.get("url"), local_path="tests/filmroom/test.mp4"
)
