import os
import time
from datetime import datetime, date
import logging
import logging.config

from mlb_videos.utils import setup_project2, x_days_ago
from mlb_videos import MLBVideoClient

date_var = x_days_ago(1)
date_desc = x_days_ago(1, "%B %d, %Y")

_PROJECT_NAME = "worst_calls_yesterday"
project_path = setup_project2(_PROJECT_NAME, date_var)

logging.config.fileConfig(
    "logging.ini",
    defaults={"project_name": _PROJECT_NAME, "project_date": date_var},
)
logger = logging.getLogger(__name__)

PARAMS = {
    "project_name": "worst_calls_yesterday",
    "project_path": project_path,
    "start_date": date_var,
    "end_date": date_var,
    "enable_cache": False,
    "game_info": False,
    "player_info": False,
    "team_info": False,
    "analysis": ["umpire_calls"],
    "queries": None,
    "steps": [
        {
            "type": "query",
            "params": {"query": "description in ('called_strike','ball')"},
        },
        {"type": "query", "params": {"query": "release_speed >= 65"}},
        {"type": "query", "params": {"query": "total_miss >= 2"}},
        {
            "type": "rank",
            "params": {
                "name": "total_miss_rank",
                "group_by": None,
                "fields": ["total_miss"],
                "ascending": [False],
                "keep_sort": True,
            },
        },
        # {"type": "query", "params": {"query": "total_miss_rank <= 25"}},
    ],
    "search_filmroom": True,
    "filmroom_params": {"feed": "Best", "download": True},
    "build_compilation": True,
    "compilation_params": {"use_intro": True},
    "youtube_upload": True,
    "youtube_params": {
        "title": f"MLB Umpires | Worst Calls ({date_desc})",
        "description": f"Here are the worst calls from yesterday's game(s) on {date_desc}.",
        "tags": ["umpires", "angel hernandez", "bad baseball calls"],
        "playlist": "Umpires - Worst Calls",
        "privacy": "public"
        # "thumbnail": "resources/acuna.jpg",
    },
    "purge_files": False,
}

MLBVideoClient(**PARAMS)
