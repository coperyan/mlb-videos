import os
import logging
import logging.config
from mlb_videos.util import setup_project

_PROJECT_NAME = "hardest_hits"
project_path = setup_project(_PROJECT_NAME)

logging.config.fileConfig("logging.ini", defaults={"project_name": _PROJECT_NAME})
logger = logging.getLogger(__name__)

from mlb_videos import MLBVideoClient

test = MLBVideoClient(
    project_name=_PROJECT_NAME,
    project_path=project_path,
    start_date="2023-07-01",
    end_date="2023-07-31",
    enable_cache=False,
    game_info=False,
    player_info=False,
    team_info=False,
    analysis=False,
    queries=None,
    steps=[
        {"type": "query", "params": {"query": "description == 'hit_into_play'"}},
        {
            "type": "query",
            "params": {"query": "events in ('single','double','triple','home_run')"},
        },
        {
            "type": "rank",
            "params": {
                "name": "speed_rank",
                "group_by": None,
                "fields": ["launch_speed"],
                "ascending": [False],
                "keep_sort": True,
            },
        },
        {"type": "query", "params": {"query": "speed_rank <= 30"}},
    ],
    search_filmroom=True,
    filmroom_params={"feed": "Best", "download": True},
    build_compilation=True,
    compilation_params={"metric_caption": "launch_speed"},
    upload_youtube=True,
    youtube_params={
        "title": "MLB | Hardest Hits (July 2023)",
        "description": "Here are the top ~30 hardest hit balls in the majors last month.",
        "tags": ["longest home runs", "furthest home runs", "dingers"],
        "playlist": "Hardest Hits",
        "thumbnail": "resources/acuna.jpg",
    },
    purge_files=False,
)
