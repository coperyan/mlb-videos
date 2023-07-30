import os

from mlb_videos.main import Data


mlbdata = Data(
    project_name="test_pitch_movement",
    start_date="2023-03-01",
    end_date="2023-07-28",
    enable_cache=True,
)
# mlbdata.query_df(
#     "pitcher == 676254 & description in ('called_strike','swinging_strike')"
# )
mlbdata.query_df("description in ('called_strike','swinging_strike')")
mlbdata.transform_statcast(["pitch_movement"])

test = (
    mlbdata.df[(mlbdata.df["pitch_type"] == "SI") & (mlbdata.df["release_speed"] >= 98)]
    .sort_values(by="horizontal_break", ascending=False)
    .reset_index(drop=True)
)
test.iloc[0].to_dict()


test = (
    mlbdata.df[(mlbdata.df["pitch_type"] == "SI") & (mlbdata.df["release_speed"] >= 98)]
    .sort_values(by="vertical_break", ascending=True)
    .reset_index(drop=True)
)
test.iloc[0].to_dict()


##Slider -- look at horizontal break, start with negative numbers??
