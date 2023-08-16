import os
import logging
import logging.config

_PROJECT_NAME = "test"

logging.config.fileConfig("logging.ini", defaults={"project_name": _PROJECT_NAME})
logger = logging.getLogger(__name__)

from mlb_videos.main import Data
from mlb_videos.video import Compilation


mlbdata = Data(
    project_name=_PROJECT_NAME, start_date="2023-04-01", end_date="2023-08-10"
)
mlbdata.query_df("events == 'home_run'")
mlbdata.rank_df(
    name="distance_rank", group_by=None, fields=["hit_distance_sc"], ascending=[False]
)
mlbdata.query_df("distance_rank <= 1")
mlbdata.get_videos(download=True)

comp = Compilation(
    name=_PROJECT_NAME,
    df=mlbdata.df,
    local_path=mlbdata.local_path,
    metric_caption="hit_distance_sc",
)
