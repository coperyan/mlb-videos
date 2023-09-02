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

_PROJECT_NAME = "longest_home_runs_last_month"
project_path = setup_project2(_PROJECT_NAME, date_var)

logging.config.fileConfig(
    "logging.ini",
    defaults={"project_name": _PROJECT_NAME, "project_date": date_var},
)
logger = logging.getLogger(__name__)

PARAMS = {
    "project_name": "longest_home_runs_last_month",
    "project_path": project_path,
    "start_date": start_date,
    "end_date": end_date,
    "enable_cache": False,
    "game_info": False,
    "player_info": False,
    "team_info": False,
    # "analysis": ["umpire_calls"],
    "queries": None,
    "steps": [
        {
            "type": "query",
            "params": {"query": "events == 'home_run'"},
        },
        {"type": "query", "params": {"query": "hit_distance_sc > 0"}},
        {
            "type": "rank",
            "params": {
                "name": "homer_distance_rank",
                "group_by": None,
                "fields": ["hit_distance_sc"],
                "ascending": [False],
                "keep_sort": True,
            },
        },
        {"type": "query", "params": {"query": "homer_distance_rank <= 25"}},
    ],
    "search_filmroom": True,
    "filmroom_params": {"feed": "Best", "download": True},
    "build_compilation": True,
    "compilation_params": {"metric_caption": "hit_distance_sc"},
    "youtube_upload": True,
    "youtube_params": {
        "title": f"MLB | Longest Home Runs ({month_desc})",
        "description": f"Here are the top 25 longest homers over the past month in {month_desc}.",
        "tags": ["ohtani", "angel hernandez", "baseball smoked"],
        "playlist": "Longest Home Runs",
        "privacy": "public"
        # "thumbnail": "resources/acuna.jpg",
    },
    "purge_files": False,
}

MLBVideoClient(**PARAMS)
