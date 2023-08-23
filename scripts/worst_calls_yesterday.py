import os
import time


import logging
import logging.config

# Import utils to set project name & titles
from mlb_videos.utils import setup_project2, yesterday, twilio_message

yesterday_dt = yesterday()
yesterday_title = yesterday("%B %d, %Y")

_PROJECT_NAME = "worst_calls_yesterday"
project_path = setup_project2(_PROJECT_NAME, yesterday_dt)


try:
    # setup logger
    logging.config.fileConfig(
        f"{os.path.dirname(os.path.abspath(__file__))}/../logging.ini",
        defaults={"project_name": _PROJECT_NAME},
    )
    logger = logging.getLogger(__name__)

except Exception as e:
    print(e)
    time.sleep(20)

from mlb_videos import MLBVideoClient

PARAMS = {
    "project_name": "worst_calls_yesterday",
    "project_path": project_path,
    "start_date": yesterday(),
    "end_date": yesterday(),
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
        {"type": "query", "params": {"query": "total_miss >= 3"}},
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
        "title": f"MLB Umpires | Worst Calls ({yesterday_title})",
        "description": f"Here are the worst calls from yesterday's game(s) on {yesterday_title}.",
        "tags": ["umpires", "angel hernandez", "bad baseball calls"],
        "playlist": "Umpires - Worst Calls",
        # "thumbnail": "resources/acuna.jpg",
    },
    "purge_files": False,
}


def main():
    vid_client = MLBVideoClient(**PARAMS)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.info(f"Pipeline failed:{e}")
        time.sleep(25)
        raise Exception(e)
