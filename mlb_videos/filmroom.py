import os
import requests
import pandas as pd
from typing import Union, Dict

from .constants import _DT_FORMAT
from .queries import (
    _VIDEO_ROOM_QUERIES,
)

_VIDEO_ROOM_CHUNK_SIZE = 1024
_VIDEO_ROOM_QUERY_SUFFIX = "Order By Timestamp DESC"
_VIDEO_ROOM_DEFAULT_FEED = "Best"
_VIDEO_ROOM_DEFAULT_PARAMETERS = [
    "batter_id",
    "pitcher_id",
    "date",
    "pitch_type",
    "inning",
    "balls",
    "strikes",
]
_VIDEO_ROOM_RESPONSE_PATH = {
    "Search": ["data", "search", "plays"],
    "Clip": ["data", "mediaPlayback"],
}
_VIDEO_ROOM_PARAMETERS = [
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

_VIDEO_ROOM_HEADERS = {
    "Clip": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Origin": "https://www.mlb.com",
        "Referer": "https://www.mlb.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
    },
    "Search": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Origin": "https://www.mlb.com",
        "Referer": "https://www.mlb.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
    },
    "Download": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Origin": "https://www.mlb.com",
        "Referer": "https://www.mlb.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    },
}


_VIDEO_ROOM_METADATA_PATH = {
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
    "feeds": [],
    "feed_choice": "",
}


_VIDEO_ROOM_FEED_TYPES = {
    "Best": [
        "CMS_highBit",
        "CMS_mp4Avc",
        "NETWORK_mp4Avc",
        "HOME_mp4Avc",
        "AWAY_mp4Avc",
    ],
    "Optimal": [
        "CMS_mp4Avc",
        "NETWORK_mp4Avc",
        "HOME_mp4Avc",
        "AWAY_mp4Avc",
        "CMS_highBit",
    ],
    "Home": [
        "HOME_mp4Avc",
        "NETWORK_mp4Avc",
        "CMS_mp4Avc",
        "AWAY_mp4Avc",
        "CMS_highBit",
    ],
    "Away": [
        "AWAY_mp4Avc",
        "NETWORK_mp4Avc",
        "CMS_mp4Avc",
        "HOME_mp4Avc",
        "CMS_highBit",
    ],
}


class Video:
    def __init__(
        self,
        pitch: pd.Series,
        params: list = _VIDEO_ROOM_DEFAULT_PARAMETERS,
        feed: str = _VIDEO_ROOM_FEED_TYPES.get(_VIDEO_ROOM_DEFAULT_FEED, "Optimal"),
        play_id: str = None,
        download: bool = False,
        download_path: str = None,
    ):
        self.pitch = pitch
        self.params = params
        self.play_id = play_id
        self.feed = feed
        self.download = download
        self.download_path = f"{download_path}/clips"
        self.file_name = None
        self.file_path = None
        self.metadata = None
        self.feed_choice = None
        if self.play_id is None:
            self._build_search_query()
            self.perform_search()
        self.get_clip()
        if self.download:
            self.download_clip()

    def _build_search_query(self):
        query = ""
        for param in self.params:
            param_ref = next(
                filter(lambda x: x["Name"] == param, _VIDEO_ROOM_PARAMETERS)
            )
            param_val = self.pitch.get(param_ref["Ref"], {})
            if param == "date":
                param_val = param_val.strftime(_DT_FORMAT)
            eq_sep = "=" * param_ref["EqCt"]
            sp_pad = r"\"" if param_ref["Type"] == "str" else ""

            sparam_str = f"{param_ref['Url']} {eq_sep} [{sp_pad}{param_val}{sp_pad}]"

            if query == "":
                query = sparam_str
            else:
                query += f" AND {sparam_str}"

        query = f"{query} {_VIDEO_ROOM_QUERY_SUFFIX}"
        self.search_url = _VIDEO_ROOM_QUERIES.get("Search").replace(
            '"query":""', f'"query":"{query}"'
        )

    def _make_request(
        self,
        url: str,
        request_type: str,
        return_json: bool = False,
        download: bool = False,
        download_path: str = None,
    ) -> Union[Dict, None]:
        headers = _VIDEO_ROOM_HEADERS.get(request_type)
        resp_path = _VIDEO_ROOM_RESPONSE_PATH.get(request_type)
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            raise Exception(
                f"Bad Request, Status Code: {resp.status_code}: {resp.text}"
            )
        if return_json:
            data = resp.json()
            if resp_path:
                for rp in resp_path:
                    data = data.get(rp)
            return data
        elif download:
            with open(download_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=_VIDEO_ROOM_CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)

    def _clip_metadata(self, data: dict) -> dict:
        metadata = {}
        for k, v in _VIDEO_ROOM_METADATA_PATH.items():
            data_copy = data.copy()
            if k in ["feeds", "feed choice"]:
                metadata.update({k: v})
            else:
                for p in v:
                    data_copy = data_copy.get(p, {})
                if data_copy:
                    metadata.update({k: data_copy})
                else:
                    metadata.update({k: None})
        return metadata

    def _clip_feeds(self, data: dict) -> dict:
        feeds = []
        for cf in data.get("feeds"):
            for pb in cf.get("playbacks"):
                if ".mp4" in os.path.basename(pb.get("url")).lower():
                    feeds.append(
                        {
                            "id": f"{cf['type']}_{pb['name']}",
                            "type": cf.get("type"),
                            "name": pb.get("name"),
                            "url": pb.get("url"),
                        }
                    )
        for ft in self.feed:
            if ft in [f.get("id") for f in feeds]:
                feed_choice = [f for f in feeds if f.get("id") == ft][0]
                break

        if feed_choice is not None:
            self.metadata["feeds"] = feeds
            self.metadata["feed_choice"] = feed_choice
            self.feed_choice = feed_choice
            print(f"Feed Choice: {self.feed_choice}")
        else:
            raise Exception("No valid feeds found.")

    def perform_search(self):
        search_json = self._make_request(
            self.search_url, request_type="Search", return_json=True
        )
        clip_ct = len(search_json)
        self.play_id = search_json[0]["mediaPlayback"][0]["slug"]
        print(f"Found {clip_ct} clip(s) for {self.play_id}")

    def get_clip(self):
        clip_json = self._make_request(
            _VIDEO_ROOM_QUERIES.get("Clip").replace("slug_id", self.play_id),
            request_type="Clip",
            return_json=True,
        )
        clip_json = clip_json[0]
        self.metadata = self._clip_metadata(clip_json)
        self._clip_feeds(clip_json)

    def get_clip_filename(self):
        return (
            f"{self.metadata['date']}_"
            f"{self.metadata['slug']}_"
            f"{self.feed_choice['id']}.mp4"
        )

    def get_clip_filepath(self):
        return os.path.join(
            self.download_path,
            (
                f"{self.metadata['date']}_"
                f"{self.metadata['slug']}_"
                f"{self.feed_choice['id']}.mp4"
            ),
        )

    def download_clip(self):
        if self.feed_choice.get("url"):
            try:
                self.file_name = (
                    f"{self.metadata['date']}_"
                    f"{self.metadata['slug']}_"
                    f"{self.feed_choice['id']}.mp4"
                )
                self.file_path = os.path.join(self.download_path, self.file_name)
                self._make_request(
                    self.feed_choice.get("url"),
                    request_type="Download",
                    download=True,
                    download_path=self.file_path,
                )
            except Exception as e:
                print("Downloading failed..")
        else:
            pass
