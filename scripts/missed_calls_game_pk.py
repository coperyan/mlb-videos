import os
import time
from datetime import datetime, date
import logging
import logging.config

from mlb_videos.utils import setup_project2, x_days_ago
from mlb_videos import MLBVideoClient

start_date = "2020-09-27"
end_date = "2020-09-27"
game_pk = 631002

_PROJECT_NAME = "worst_calls_specific_game"
project_path = setup_project2(_PROJECT_NAME, f"{game_pk}")

logging.config.fileConfig(
    "logging.ini",
    defaults={"project_name": _PROJECT_NAME, "project_date": f"{game_pk}"},
)
logger = logging.getLogger(__name__)

PARAMS = {
    "project_name": "worst_calls_yesterday",
    "project_path": project_path,
    "start_date": start_date,
    "end_date": end_date,
    "enable_cache": False,
    "game_info": False,
    "player_info": False,
    "team_info": False,
    "analysis": ["umpire_calls"],
    "queries": None,
    "steps": [
        {"type": "query", "params": {"query": f"game_pk == {game_pk}"}},
        {
            "type": "query",
            "params": {"query": "description in ('called_strike','ball')"},
        },
        {"type": "query", "params": {"query": "release_speed >= 25"}},
        {"type": "query", "params": {"query": "total_miss > 0"}},
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
    "youtube_upload": True,
    "youtube_params": {
        "title": f"MLB Umpires | Worst Calls (Game #{game_pk})",
        "description": f"Here are the worst calls xxxxxx",
        "tags": ["umpires", "angel hernandez", "bad baseball calls"],
        "playlist": "Umpires - Worst Calls",
        "privacy": "unlisted"
        # "thumbnail": "resources/acuna.jpg",
    },
    "purge_files": False,
}

MLBVideoClient(**PARAMS)
