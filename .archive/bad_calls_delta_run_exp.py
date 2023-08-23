import os

from data import Data
from video import Compilation

_PROJECT_NAME = "bad_calls_delta_run_exp"

mlbdata = Data(
    project_name=_PROJECT_NAME, start_date="2023-03-01", end_date="2023-07-28"
)
mlbdata.transform_statcast(["umpire_calls", "adj_delta_win_exp"])
mlbdata.query_df("total_miss >= 2 & release_speed >= 65 & adj_delta_win_exp > 0")

mlbdata.rank_df(
    name="delta_bad_call_rank",
    group_by=None,
    fields=["adj_delta_win_exp"],
    ascending=[False],
)

mlbdata.query_df("delta_bad_call_rank <= 20")
mlbdata.get_videos(download=True)

comp = Compilation(
    name=_PROJECT_NAME,
    df=mlbdata.df,
    local_path=mlbdata.local_path,
)
