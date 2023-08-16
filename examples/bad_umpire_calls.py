import os

from mlb_videos.main import Data
from mlb_videos.video import Compilation

_PROJECT_NAME = "worst_calls"

data_class = Data(
    project_name=_PROJECT_NAME, start_date="2023-08-07", end_date="2023-08-07"
)
data_class.transform_statcast("umpire_calls")
data_class.query_df("game_pk == 717088")
data_class.query_df("total_miss > 0")
# data_class.rank_df(
#     "total_miss_rank",
#     group_by=None,
#     fields=["total_miss", "vertical_miss", "horizontal_miss"],
#     ascending=[False, False, False],
# )
# data_class.query_df("total_miss_rank <= 25")
data_class.get_videos(download=True)


test = Compilation(
    name="Laz_Diaz_Missed_Calls", df=data_class.df, local_path=data_class.local_path
)
test.generate_compilation()
