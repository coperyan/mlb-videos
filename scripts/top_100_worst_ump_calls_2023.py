import os
import time
from datetime import datetime, date

import logging
import logging.config

from mlb_videos.utils import setup_project2, x_days_ago, x_months_ago
from mlb_videos import MLBVideoClient

from mlb_videos.statsapi import Schedule, Game

## from mlb_videos.statcast import Statcast

_PROJECT_NAME = "worst_umpire_calls_2023"
_MAX_CLIP_LEN = 20

date_var = "2023"
start_date = "2023-03-30"
end_date = "2023-10-03"
project_path = setup_project2(_PROJECT_NAME, date_var)

logging.config.fileConfig(
    "logging.ini",
    defaults={"project_name": _PROJECT_NAME, "project_date": date_var},
)
logger = logging.getLogger(__name__)


data = MLBVideoClient(
    project_name=_PROJECT_NAME,
    project_path=project_path,
    statcast_params={
        "start_date": start_date,
        "end_date": end_date,
        "descriptions": ["called strike", "ball"],
    },
)
data.transform_statcast("umpire_calls")
data.query_df("release_speed >= 60")
data.query_df("total_miss > 0")
data.rank_df(
    name="total_miss_rank",
    group_by=None,
    fields=["total_miss"],
    ascending=[False],
    keep_sort=False,
)
data.query_df("total_miss_rank <= 100")
data.sort_df(fields=["total_miss"], ascending=[True])

data._get_filmroom_videos(params={"download": True, "feed": "best"})
data.compilation_params = {
    "use_intro": True,
    "add_transitions": True,
    "transition_padding": 0.5,
    "max_clip_length": 20,
}
data.create_compilation()
data.youtube_params = {
    "title": "MLB Umpires | Top 100 Worst Calls in 2023",
    "description": "",
    "tags": ["mlb 2023", "worst calls", "angel hernandez", "top 100"],
    "playlist": "Umpires - Worst Calls",
    "privacy": "private",
    "thumbnail": "resources/angel_hernandez_1.jpg",
}
data.upload_youtube()
