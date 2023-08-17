import os

from mlb_videos.util import setup_project, purge_project_files
from mlb_videos.main import Data
from mlb_videos.video import Compilation

_PROJECT_NAME = "longest_homers"

mlbdata = Data(
    project_name=_PROJECT_NAME, start_date="2023-06-01", end_date="2023-06-30"
)
mlbdata.query_df("events == 'home_run'")
mlbdata.rank_df(
    name="distance_rank", group_by=None, fields=["hit_distance_sc"], ascending=[False]
)
mlbdata.query_df("distance_rank <= 25")
mlbdata.sort_df(fields=["pitch_id"], ascending=True)
mlbdata.get_videos(download=True)

comp = Compilation(
    name=_PROJECT_NAME,
    df=mlbdata.df,
    local_path=mlbdata.local_path,
    metric_caption="hit_distance_sc",
)
