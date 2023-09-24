import os
import time
from datetime import datetime, date
import logging
import logging.config

from mlb_videos.utils import setup_project2, x_days_ago
from mlb_videos import MLBVideoClient

date_var = x_days_ago(1)
date_desc = x_days_ago(1, "%B %d, %Y")

_PROJECT_NAME = "kyle_harrison_home_opener"
project_path = setup_project2(_PROJECT_NAME, date_var)

logging.config.fileConfig(
    "logging.ini",
    defaults={"project_name": _PROJECT_NAME, "project_date": date_var},
)
logger = logging.getLogger(__name__)

PARAMS = {
    "project_name": "kyle_harrison_home_debut",
    "project_path": project_path,
    "start_date": date_var,
    "end_date": date_var,
    "enable_cache": False,
    "game_info": False,
    "player_info": False,
    "team_info": False,
    "queries": ["pitcher == 690986"],
    "search_filmroom": True,
    "filmroom_params": {"feed": "Best", "download": True},
    "build_compilation": False,
    "youtube_upload": False,
    "youtube_params": {},
    "purge_files": False,
}

MLBVideoClient(**PARAMS)
