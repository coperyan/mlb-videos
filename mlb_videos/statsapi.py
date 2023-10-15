import os
import requests
import pandas as pd
from tqdm import tqdm
import concurrent.futures
from typing import Union

from .constants import Teams
from .utils import yesterday

import logging
import logging.config

logger = logging.getLogger(__name__)

_GAME_URL = "https://statsapi.mlb.com/api/v1.1/game/{0}/feed/live"
_PLAYER_URL = "https://statsapi.mlb.com/api/v1/people/{0}"
_PLAYER_SITE_URL = "https://www.mlb.com/player/{0}"
_SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule"
_CONCURRENT_THRESHOLD = 10

_SOCIALS = [
    {"name": "twitter", "repl": "https://twitter.com/@"},
    {"name": "instagram", "repl": "https://www.instagram.com/"},
]
_GAME_ROUTES = {
    "Info": {
        "Route": ["gameData", "game"],
        "Columns": ["season"],
        "Custom": False,
    },
    "Dates": {
        "Route": ["gameData", "datetime"],
        "Columns": ["dateTime", "officialDate", "dayNight", "time", "ampm"],
        "Custom": False,
    },
    "AwayTeam": {
        "Route": ["gameData", "teams", "away"],
        "Columns": ["name", "abbreviation"],
        "Custom": False,
    },
    "HomeTeam": {
        "Route": ["gameData", "teams", "home"],
        "Columns": ["name", "abbreviation"],
        "Custom": False,
    },
    "Venue": {
        "Route": ["gameData", "venue"],
        "Columns": ["name"],
        "Custom": False,
    },
    "Winner": {
        "Route": ["liveData", "decisions", "winner"],
        "Columns": ["id"],
        "Custom": False,
    },
    "Loser": {
        "Route": ["liveData", "decisions", "loser"],
        "Columns": ["id"],
        "Custom": False,
    },
    "Save": {
        "Route": ["liveData", "decisions", "save"],
        "Columns": ["id"],
        "Custom": False,
    },
    "Umpires": {
        "Route": ["liveData", "boxscore", "officials"],
        "Columns": ["Home Plate", "First Base", "Second Base", "Third Base"],
        "Custom": True,
        "CustomPath": ["official", "fullName"],
    },
}
_PLAYER_FIELDS = [
    "id",
    "fullName",
    "link",
    "firstName",
    "lastName",
    "primaryNumber",
    "currentAge",
    "height",
    "weight",
    "primaryPosition",
    "useName",
    "nickName",
    "nameSlug",
    "twitter",
    "instagram",
]


class Game:
    def __init__(self, game_pks: list):
        self.game_list = list(set(int(gpk) for gpk in game_pks))
        self.df_list = []
        self.df = None
        if len(self.df_list) >= _CONCURRENT_THRESHOLD:
            self.get_games_concurrent()
        else:
            self.get_games()
        self.create_df()

    def _route(self, name: str, cfg: dict, data: dict) -> dict:
        for key in cfg.get("Route"):
            data = data.get(key)
        return {k: v for k, v in data.items() if k in cfg.get("Columns")}

    def _custom_route(self, name: str, cfg: dict, data: dict) -> dict:
        d = {}
        for key in cfg.get("Route"):
            data = data.get(key)
        for x in range(0, len(cfg.get("Columns"))):
            data_copy = data[x].copy()
            for path in cfg.get("CustomPath"):
                data_copy = data_copy.get(path)
            d[cfg.get("Columns")[x]] = data_copy
        return d

    def parse_response(self, data: dict) -> None:
        df = {"game_pk": data.get("gamePk")}
        for name, cfg in _GAME_ROUTES.items():
            try:
                if cfg.get("Custom"):
                    df[name] = self._custom_route(name, cfg, data)
                else:
                    df[name] = self._route(name, cfg, data)
            except Exception as e:
                continue

        df = pd.json_normalize(df, sep="_")
        df = df.rename(
            columns={c: c.replace(" ", "_").lower() for c in df.columns.values}
        )
        return df

    def _make_api_request(self, game_id):
        resp = requests.get(_GAME_URL.format(game_id))
        df = self.parse_response(resp.json())
        return df

    def get_games(self):
        for game in self.game_list:
            self.df_list.append(self._make_api_request(game))

    def get_games_concurrent(self):
        with tqdm(total=len(self.game_list)) as progress:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self._make_api_request, game_id)
                    for game_id in self.game_list
                }
                for future in concurrent.futures.as_completed(futures):
                    self.df_list.append(future.result())
                    progress.update(1)

    def create_df(self):
        self.df = pd.concat(self.df_list, axis=0, ignore_index=True)
        self.df = self.df.sort_values("game_pk", ascending=True)

    def get_df(self) -> pd.DataFrame:
        return self.df


class Player:
    def __init__(self, player_id: Union[int, list]):
        if isinstance(player_id, int):
            self.player_list = [player_id]
        else:
            self.player_list = player_id
        self.df_list = []
        self.df = None
        if len(self.player_list) >= _CONCURRENT_THRESHOLD:
            self.get_players_concurrent()
        else:
            self.get_players()
        self.create_df()

    def _parse_response(self, data: dict) -> None:
        data = data.get("people")[0]
        data = {k: v for k, v in data.items() if k in _PLAYER_FIELDS}
        df = pd.json_normalize(data, sep="_")
        df = df.rename(
            columns={c: c.replace(" ", "_").lower() for c in df.columns.values}
        )
        return df

    def _make_api_request(self, player_id: int):
        resp = requests.get(_PLAYER_URL.format(player_id))
        df = self._parse_response(resp.json())
        return df

    def get_players(self):
        for player in self.player_list:
            self.df_list.append(self._make_api_request(player_id=player))

    def get_players_concurrent(self):
        with tqdm(total=len(self.player_list)) as progress:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self._make_api_request, player_id)
                    for player_id in self.player_list
                }
                for future in concurrent.futures.as_completed(futures):
                    self.df_list.append(future.result())
                    progress.update(1)

    def create_df(self):
        self.df = pd.concat(self.df_list, axis=0, ignore_index=True)
        self.df = self.df.sort_values("id", ascending=True)

    def get_df(self) -> pd.DataFrame:
        return self.df


class Schedule:
    def __init__(self, start_date: str, end_date: str = None, team: str = None):
        self.start_date = start_date
        self.end_date = end_date if end_date else yesterday()
        self.team = team
        self.team_id = Teams.get(self.team).get("mlb_id")
        self.data = None
        self.df = None
        self._make_request()
        self._create_schedule_df()

    def _make_request(self):
        resp = requests.get(
            _SCHEDULE_URL,
            params={
                "sportId": 1,
                "startDate": self.start_date,
                "endDate": self.end_date,
                "teamId": self.team_id,
            },
        )
        self.data = resp.json()

    def _create_schedule_df(self):
        self.df = pd.DataFrame(
            [
                {
                    "game_pk": game.get("gamePk"),
                    "date": game.get("officialDate"),
                    "away_team": game.get("teams").get("away").get("team").get("name"),
                    "home_team": game.get("teams").get("home").get("team").get("name"),
                    "venue": game.get("venue").get("name"),
                }
                for dates in self.data.get("dates")
                for game in dates.get("games")
            ]
        )

    def get_df(self) -> pd.DataFrame:
        return self.df
