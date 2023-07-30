import os

from data import Data
from video import Compilation

_PROJECT_NAME = "testing_development"

mlbdata = Data(
    project_name=_PROJECT_NAME, start_date="2023-07-01", end_date="2023-07-28"
)
mlbdata.query_df("events == 'home_run'")
mlbdata.rank_df(
    name="distance_rank", group_by=None, fields=["hit_distance_sc"], ascending=[False]
)
mlbdata.query_df("distance_rank <= 10")
mlbdata.get_videos(download=True)

comp = Compilation(
    name=_PROJECT_NAME,
    df=mlbdata.df,
    local_path=mlbdata.local_path,
    metric_caption="hit_distance_sc",
)
