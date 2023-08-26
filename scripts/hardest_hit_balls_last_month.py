import os
import time
from datetime import datetime, date
import logging
import logging.config

from mlb_videos.utils import setup_project2, x_days_ago, x_months_ago
from mlb_videos import MLBVideoClient

month_dict = x_months_ago(x=1)
month_desc = f"{month_dict.get('month_name')} {month_dict.get('year')}"
start_date = month_dict.get("start_date")
end_date = month_dict.get("end_date")
date_var = f"{month_dict.get('year')}{str(month_dict.get('month_number')).zfill(2)}"

_PROJECT_NAME = "hardest_hit_balls_last_month"
project_path = setup_project2(_PROJECT_NAME, date_var)

logging.config.fileConfig(
    "logging.ini",
    defaults={"project_name": _PROJECT_NAME, "project_date": date_var},
)
logger = logging.getLogger(__name__)

PARAMS = {
    "project_name": "hardest_hit_balls_last_month",
    "project_path": project_path,
    "start_date": date_var,
    "end_date": date_var,
    "enable_cache": False,
    "game_info": False,
    "player_info": False,
    "team_info": False,
    # "analysis": ["umpire_calls"],
    "queries": None,
    "steps": [
        {
            "type": "query",
            "params": {"query": "description == 'hit_into_play'"},
        },
        {
            "type": "query",
            "params": {
                "query": "events not in ('single','double','triple','home_run')"
            },
        },
        {"type": "query", "params": {"query": "launch_speed > 0"}},
        {
            "type": "rank",
            "params": {
                "name": "exit_velocity_rank",
                "group_by": None,
                "fields": ["launch_speed"],
                "ascending": [False],
                "keep_sort": True,
            },
        },
        {"type": "query", "params": {"query": "exit_velocity_rank <= 25"}},
    ],
    "search_filmroom": True,
    "filmroom_params": {"feed": "Best", "download": True},
    "build_compilation": True,
    "youtube_upload": True,
    "youtube_params": {
        "title": f"MLB | Hardest Hits ({month_desc})",
        "description": f"Here are the top 25 balls hit for hits over the past month in {month_desc}.",
        "tags": ["ohtani", "angel hernandez", "baseball smoked"],
        "playlist": "Hardest Hits",
        "privacy": "public"
        # "thumbnail": "resources/acuna.jpg",
    },
    "purge_files": False,
}

MLBVideoClient(**PARAMS)
