import os

from mlb_videos.main import Data
from mlb_videos.video import Compilation

_PROJECT_NAME = "highest_xba_outs"

mlbdata = Data(
    project_name=_PROJECT_NAME, start_date="2023-07-01", end_date="2023-07-31"
)
mlbdata.query_df("description == 'hit_into_play'")
mlbdata.query_df("events not in ('single','double','triple','home_run')")
mlbdata.rank_df(
    name="xba_rank",
    group_by=None,
    fields=["estimated_ba_using_speedangle"],
    ascending=[False],
)
mlbdata.query_df("xba_rank <= 25")
mlbdata.get_videos(download=True)

comp = Compilation(
    name=_PROJECT_NAME,
    df=mlbdata.df,
    local_path=mlbdata.local_path,
    # metric_caption="estimated_ba_using_speedangle",
)
