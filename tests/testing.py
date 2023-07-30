import os

from data import Data
from video import Compilation

_PROJECT_NAME = "testing_development"

data_class = Data(
    project_name=_PROJECT_NAME, start_date="2023-07-01", end_date="2023-07-28"
)
data_class.transform_statcast("umpire_calls")
data_class.query_df("total_miss >= 3")
data_class.query_df("release_speed >= 65")
data_class.rank_df(
    "total_miss_rank",
    group_by=None,
    fields=["total_miss", "vertical_miss", "horizontal_miss"],
    ascending=[False, False, False],
)
data_class.query_df("total_miss_rank <= 25")
data_class.get_videos(download=True)


test = Compilation(
    name="Worst_Calls_Last_Week", df=data_class.df, local_path=data_class.local_path
)
test.generate_compilation()
