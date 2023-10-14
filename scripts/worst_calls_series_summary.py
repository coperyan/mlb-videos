import os
import time
import logging
import logging.config

from mlb_videos.utils import setup_project2
from mlb_videos import MLBVideoClient


_PROJECT_NAME = "worst_calls_2023_playoffs"
_PROJECT_DESC = "atl_phi_nlds_2023"

project_path = setup_project2(_PROJECT_NAME, _PROJECT_DESC)

logging.config.fileConfig(
    "logging.ini",
    defaults={"project_name": _PROJECT_NAME, "project_date": _PROJECT_DESC},
)
logger = logging.getLogger(__name__)

data = MLBVideoClient(
    project_name=_PROJECT_NAME,
    project_path=project_path,
    start_date="2023-10-07",
    end_date="2023-10-12",
    enable_cache=False,
    game_info=False,
    player_info=False,
    team_info=False,
    analysis=["umpire_calls"],
)
data.query_df("away_team == 'ATL' or home_team == 'ATL'")
data.query_df("total_miss >= 1")
data._get_filmroom_videos(params={"download": True, "feed": "best"})
data.compilation_params = {"use_intro": True}
data.create_compilation()
data.youtube_params = {
    "title": "MLB Umpires | Worst Calls (ATL vs. PHI NLDS 2023)",
    "description": "",
    "tags": [
        "mlb umpires",
        "umpire bad calls",
        "2023 mlb playoffs",
        "2023 mlb nlds",
        "2023 braves",
        "2023 phillies",
        "angel hernandez",
    ],
    "playlist": "Umpires - Worst Calls",
    "privacy": "public",
}
data.upload_youtube()


# PARAMS = {
#     "project_name": "worst_calls_yesterday",
#     "project_path": project_path,
#     "start_date": date_var,
#     "end_date": date_var,
#     "enable_cache": False,
#     "game_info": False,
#     "player_info": False,
#     "team_info": False,
#     "analysis": ["umpire_calls"],
#     "queries": None,
#     "steps": [
#         {
#             "type": "query",
#             "params": {"query": "description in ('called_strike','ball')"},
#         },
#         {"type": "query", "params": {"query": "release_speed >= 65"}},
#         {"type": "query", "params": {"query": "total_miss >= 2"}},
#         {
#             "type": "rank",
#             "params": {
#                 "name": "total_miss_rank",
#                 "group_by": None,
#                 "fields": ["total_miss"],
#                 "ascending": [False],
#                 "keep_sort": True,
#             },
#         },
#         # {"type": "query", "params": {"query": "total_miss_rank <= 25"}},
#     ],
#     "search_filmroom": True,
#     "filmroom_params": {"feed": "Best", "download": True},
#     "build_compilation": True,
#     "compilation_params": {"use_intro": True},
#     "youtube_upload": True,
#     "youtube_params": {
#         "title": f"MLB Umpires | Worst Calls ({_PROJECT_DESC})",
#         "description": f"Here are the worst calls from the series {_PROJECT_DESC}.",
#         "tags": [
#             "umpires",
#             "angel hernandez",
#             "bad baseball calls",
#             "2023 mlb playoffs",
#         ],
#         "playlist": "Umpires - Worst Calls",
#         "privacy": "public"
#         # "thumbnail": "resources/acuna.jpg",
#     },
#     "purge_files": False,
# }

# MLBVideoClient(**PARAMS)
