import os

from data import Data
from video import Compilation

_PROJECT_NAME = "hardest_hit_outs"

mlbdata = Data(
    project_name=_PROJECT_NAME, start_date="2023-03-01", end_date="2023-11-30"
)

mlbdata.query_df("description == 'hit_into_play'")
mlbdata.query_df("events not in ('single','double','triple','home_run')")
mlbdata.rank_df(
    name="exit_velocity_rank", group_by=None, fields=["launch_speed"], ascending=[False]
)
mlbdata.query_df("exit_velocity_rank <= 20")
mlbdata.get_videos(download=True)

comp = Compilation(
    name=_PROJECT_NAME,
    df=mlbdata.df,
    local_path=mlbdata.local_path,
    metric_caption="launch_speed",
)
