import os
import requests
import pandas as pd
from typing import Union, Dict

import logging
import logging.config

logger = logging.getLogger(__name__)

from constants import _DT_FORMAT, _FILMROOM_QUERIES


_FILMROOM_CHUNK_SIZE = 1024
_FILMROOM_QUERY_SUFFIX = "Order By Timestamp DESC"
_FILMROOM_SUBFOLDER = "clips"
_FILMROOM_DEFAULT_DOWNLOAD = True
_FILMROOM_DEFAULT_FEED = "Best"
_FILMROOM_DEFAULT_PARAMETERS = [
    "batter_id",
    "pitcher_id",
    "date",
    "pitch_type",
    "inning",
    "balls",
    "strikes",
]
_FILMROOM_RESPONSE_PATH = {
    "Search": ["data", "search", "plays"],
    "Clip": ["data", "mediaPlayback"],
}
_FILMROOM_PARAMETERS = [
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

_FILMROOM_HEADERS = {
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


_FILMROOM_METADATA_PATH = {
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


_FILMROOM_FEED_TYPES = {
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


class FilmRoom:
    def __init__(
        self,
        pitch: pd.Series,
        local_path: str = None,
        query_params: list = _FILMROOM_DEFAULT_PARAMETERS,
        feed: str = _FILMROOM_DEFAULT_FEED,
        download: bool = _FILMROOM_DEFAULT_DOWNLOAD,
    ):
        self.pitch = pitch
        self.query_params = query_params
        self.feed = _FILMROOM_FEED_TYPES.get(_FILMROOM_DEFAULT_FEED, "Optimal")
        self.download = download
        self.download_path = f"{local_path}/{_FILMROOM_SUBFOLDER}"
        self.play_id = None
        self.file_name = None
        self.file_path = None
        self.metadata = None
        self.feed_choice = None
        self._build_search_query()
        self.perform_search()
        self.get_clip()
        if self.download:
            self.download_clip()

    def _build_search_query(self, exclude_params: list = []):
        query = ""
        if exclude_params:
            query_params = [x for x in self.query_params if x not in exclude_params]
        else:
            query_params = self.query_params.copy()
        for param in query_params:
            param_ref = next(filter(lambda x: x["Name"] == param, _FILMROOM_PARAMETERS))
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

        query = f"{query} {_FILMROOM_QUERY_SUFFIX}"
        self.search_url = _FILMROOM_QUERIES.get("Search").replace(
            '"query":""', f'"query":"{query}"'
        )
        logging.info(f"Built search query, excluded param(s): {exclude_params}")

    def _make_request(
        self,
        url: str,
        request_type: str,
        return_json: bool = False,
        download: bool = False,
        download_path: str = None,
    ) -> Union[Dict, None]:
        headers = _FILMROOM_HEADERS.get(request_type)
        resp_path = _FILMROOM_RESPONSE_PATH.get(request_type)
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
            logging.info(f"Performed {request_type} query..")
            return data
        elif download:
            with open(download_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=_FILMROOM_CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                logging.info(f"Wrote clip to local store: {download_path}")

    def _clip_metadata(self, data: dict) -> dict:
        metadata = {}
        for k, v in _FILMROOM_METADATA_PATH.items():
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
            logging.info(f"Feed Choice: {self.feed_choice}")
        else:
            raise Exception("No valid feeds found.")

    def perform_search(self):
        search_json = self._make_request(
            self.search_url, request_type="Search", return_json=True
        )
        if len(search_json) == 0:
            self._build_search_query(exclude_params=["inning"])
            search_json = self._make_request(
                self.search_url, request_type="Search", return_json=True
            )
        clip_ct = len(search_json)
        if clip_ct > 0:
            self.play_id = search_json[0]["mediaPlayback"][0]["slug"]
            logging.info(f"Found {clip_ct} clip(s) for {self.play_id}")
        else:
            logging.warning(f"Search query did not return any clips..")

    def get_clip(self):
        clip_json = self._make_request(
            _FILMROOM_QUERIES.get("Clip").replace("slug_id", self.play_id),
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
                logging.warning("Downloading failed..")
        else:
            pass

    def get_file_info(self):
        if self.download:
            return (self.get_clip_filename(), self.get_clip_filepath())
        else:
            return (self.get_clip_filename(), None)


# clips = []
# for index, row in df.iterrows():
#     try:
#         iter_clip = Clip(
#             pitch=row, download=True, download_path="../projects/test/2023-08-17/clips"
#         )
#         iter_clip._build_search_query()
#         iter_clip.perform_search()
#         iter_clip.get_clip()
#         iter_clip.download_clip()
#     except Exception as e:
#         print(row["pitch_id"] + "\n" + str(e))
#         pass
#     clips.append(iter_clip)
