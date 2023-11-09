import re
from mlb_videos._helpers import DotDict

ENDPOINTS = DotDict(
    {
        "search": {
            "url": "/statcast_search/csv?all=true&type=details",
            "uuid": {
                "name": "pitch_id",
                "delimiter": "|",
                "keys": ["game_pk", "at_bat_number", "pitch_number"],
            },
            "sort_keys": ["game_pk", "at_bat_number", "pitch_number"],
            "fill_na_cols": ["plate_x", "plate_z", "sz_bot", "sz_top"],
            "kwargs": [
                "start_date",
                "end_date",
                "game_pks",
                "batter_ids",
                "pitcher_ids",
                "teams",
                "pitch_types",
                "events",
                "descriptions",
            ],
        }
    }
)

DATE_FORMATS = [
    (re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$"), "%Y-%m-%d"),
    (
        re.compile(r"^\d{4}-\d{1,2}-\d{1,2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z$"),
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ),
]

REQUEST_TIMEOUT = None
