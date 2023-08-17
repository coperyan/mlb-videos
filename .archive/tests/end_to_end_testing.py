import os
import logging
import logging.config
from mlb_videos.util import setup_project

_PROJECT_NAME = "test"
project_path = setup_project(_PROJECT_NAME)

logging.config.fileConfig("logging.ini", defaults={"project_name": _PROJECT_NAME})
logger = logging.getLogger(__name__)

from mlb_videos import MLBVideoClient

test = MLBVideoClient(
    project_name=_PROJECT_NAME,
    project_path=project_path,
    start_date="2023-03-01",
    end_date="2023-08-16",
    enable_cache=False,
    game_info=False,
    player_info=False,
    team_info=False,
    analysis=False,
    queries=None,
    steps=[
        {"type": "query", "params": {"query": "events == 'home_run'"}},
        {
            "type": "query",
            "params": {
                "query": "(home_team == 'SF' & inning_topbot == 'Bot') | (away_team == 'SF' & inning_topbot == 'Top')"
            },
        },
        {
            "type": "rank",
            "params": {
                "name": "distance_rank",
                "group_by": None,
                "fields": ["hit_distance_sc"],
                "ascending": [False],
                "keep_sort": True,
            },
        },
        {"type": "query", "params": {"query": "distance_rank <= 30"}},
    ],
    search_clips=False,
    download_clips=True,
    build_compilation=True,
    compilation_params={"metric_caption": "hit_distance_sc"},
    upload_youtube=True,
    youtube_params={
        "title": "San Francisco Giants | Longest Home Runs (MLB 2023)",
        "description": "Here are the top 30 Giants home runs from this year so far.",
        "tags": ["longest home runs", "furthest home runs", "dingers"],
        "playlist": "Longest Home Runs",
        "thumbnail": "resources/jd_davis_batflip.jpg",
    },
    purge_files=False,
)
