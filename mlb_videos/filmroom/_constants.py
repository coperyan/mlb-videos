from mlb_videos._helpers import DotDict

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Origin": "https://www.mlb.com",
    "Referer": "https://www.mlb.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}

DEFAULT_DOWNLOAD = True
DEFAULT_FEED = "best"
DEFAULT_PARAMETERS = [
    "batter_id",
    "pitcher_id",
    "date",
    "pitch_type",
    "inning",
    "balls",
    "strikes",
]

DOWNLOAD_CHUNK_SIZE = 1024
DOWNLOAD_SAVE_SUBFOLDER = "clips"

FEED_TYPES = [
    {"id": "CMS_highBit", "type": "network", "quality": "best"},
    {"id": "CMS_mp4Avc", "type": "network", "quality": "normal"},
    {"id": "NETWORK_mp4Avc", "type": "network", "quality": "normal"},
    {"id": "HOME_mp4Avc", "type": "home", "quality": "normal"},
    {"id": "AWAY_mp4Avc", "type": "away", "quality": "normal"},
]

METADATA_PATHS = {
    "id": ["id"],
    "slug": ["slug"],
    "title": ["title"],
    "short_desc": ["blurb"],
    "long_desc": ["description"],
    "date": ["date"],
    "game_id": ["playInfo", "gamePk"],
    "inning": ["playInfo", "inning"],
    "outs": ["playInfo", "outs"],
    "balls": ["playInfo", "balls"],
    "strikes": ["playInfo", "strikes"],
    "pitch_speed": ["playInfo", "pitchSpeed"],
    "exit_velo": ["playInfo", "exitVelocity"],
    "pitcher_id": ["playInfo", "players", "pitcher", "id"],
    "pitcher_name": ["playInfo", "players", "pitcher", "name"],
    "batter_id": ["playInfo", "players", "batter", "id"],
    "batter_name": ["playInfo", "players", "batter", "name"],
    "home_team": ["playInfo", "teams", "home", "triCode"],
    "away_team": ["playInfo", "teams", "away", "triCode"],
    "batting_team": ["playInfo", "teams", "batting", "triCode"],
    "pitching_team": ["playInfo", "teams", "pitching", "triCode"],
}


def read_query(filename: str) -> str:
    with open(f"mlb_videos/filmroom/graphql/{filename}.txt", "r") as f:
        return f.read()


QUERIES = {
    "clip": {
        "query": read_query("clip"),
        "headers": {"Content-Type": "application/json", "TE": "Trailers"},
        "resp_path": ["data", "mediaPlayback"],
    },
    "search": {
        "query": read_query("search"),
        "headers": {"Content-Type": "application/json", "TE": "Trailers"},
        "resp_path": ["data", "search", "plays"],
    },
}

QUERY_SUFFIX = "Order By Timestamp DESC"

QUERY_PARAMETERS = [
    {"Name": "player_id", "Url": "PlayerId", "Ref": None, "Type": "int", "EqCt": 2},
    {
        "Name": "batter_id",
        "Url": "BatterId",
        "Ref": "batter",
        "Type": "int",
        "EqCt": 1,
    },
    {
        "Name": "pitcher_id",
        "Url": "PitcherId",
        "Ref": "pitcher",
        "Type": "int",
        "EqCt": 1,
    },
    {"Name": "date", "Url": "Date", "Ref": "game_date", "Type": "str", "EqCt": 1},
    {"Name": "date_range", "Url": "Date", "Ref": None, "Type": "str", "EqCt": 1},
    {"Name": "season", "Url": "Season", "Ref": None, "Type": "int", "EqCt": 1},
    {"Name": "team", "Url": "Team", "Ref": None, "Type": "int", "EqCt": 1},
    {"Name": "inning", "Url": "Inning", "Ref": "inning", "Type": "int", "EqCt": 1},
    {
        "Name": "top_bottom",
        "Url": "TopBottom",
        "Ref": None,
        "Type": "str",
        "EqCt": 1,
    },
    {"Name": "outs", "Url": "Outs", "Ref": None, "Type": "int", "EqCt": 1},
    {"Name": "balls", "Url": "Balls", "Ref": "balls", "Type": "int", "EqCt": 1},
    {
        "Name": "strikes",
        "Url": "Strikes",
        "Ref": "strikes",
        "Type": "int",
        "EqCt": 1,
    },
    {
        "Name": "hit_result",
        "Url": "HitResult",
        "Ref": None,
        "Type": "str",
        "EqCt": 1,
    },
    {
        "Name": "pitch_result",
        "Url": "PitchResult",
        "Ref": None,
        "Type": "str",
        "EqCt": 1,
    },
    {
        "Name": "content_tags",
        "Url": "ContentTags",
        "Ref": None,
        "Type": "str",
        "EqCt": 1,
    },
    {
        "Name": "pitch_type",
        "Url": "PitchType",
        "Ref": "pitch_type",
        "Type": "str",
        "EqCt": 1,
    },
    {
        "Name": "pitch_speed",
        "Url": "PitchSpeed",
        "Ref": None,
        "Type": "int",
        "EqCt": 1,
    },
    {
        "Name": "pitch_zone",
        "Url": "GameDayPitchZone",
        "Ref": None,
        "Type": "int",
        "EqCt": 1,
    },
]
