import os
import pandas as pd
from typing import Union, Tuple

import logging
import logging.config

logger = logging.getLogger(__name__)

from .constants import Teams
from .statsapi import Game, Player
from .statcast import Statcast
from .filmroom import FilmRoom
from .compilation import Compilation
from .youtube import YouTube

from .util import setup_project, purge_project_files

from .analysis.umpire_calls import get_ump_calls
from .analysis.delta_win_exp import get_pitcher_batter_delta_win_exp
from .analysis.pitch_movement import get_pitch_movement


_ANALYSIS_DICT = {
    "umpire_calls": get_ump_calls,
    "pitcher_batter_delta_win_exp": get_pitcher_batter_delta_win_exp,
    "pitch_movement": get_pitch_movement,
}


class MLBVideoClient:
    def __init__(
        self,
        project_name: str,
        project_path: str,
        start_date: str,
        end_date: str = None,
        enable_cache: bool = False,
        game_info: bool = False,
        player_info: bool = False,
        team_info: bool = False,
        analysis: list = None,
        queries: list = None,
        steps: list = None,
        search_filmroom: bool = False,
        filmroom_params: dict = {},
        build_compilation: bool = False,
        compilation_params: dict = {},
        upload_youtube: bool = False,
        youtube_params: dict = {},
        purge_files: bool = False,
    ):
        self.project_name = project_name
        self.local_path = project_path
        self.start_date = start_date
        self.end_date = end_date
        self.enable_cache = enable_cache
        self.game_info = game_info
        self.player_info = player_info
        self.team_info = team_info
        self.analysis = analysis
        self.queries = queries
        self.steps = steps
        self.search_filmroom = search_filmroom
        self.filmroom_params = filmroom_params
        self.build_compilation = build_compilation
        self.compilation_params = compilation_params
        self.upload_youtube = upload_youtube
        self.youtube_params = youtube_params
        self.purge_files = purge_files
        self.missing_videos = []

        # self._setup_project()

        self.statcast_df = Statcast(
            start_date=start_date, end_date=end_date, enable_cache=enable_cache
        ).get_df()
        self.df = self.statcast_df.copy()

        if game_info:
            self.add_game_info()
        if player_info:
            self.add_player_info()
        if team_info:
            self.add_team_info()
        if analysis:
            for mod in self.analysis:
                self.transform_statcast(mod)

        if queries:
            self._perform_queries()

        if steps:
            self._perform_steps()

        if self.search_filmroom:
            self._get_filmroom_videos(params=self.filmroom_params)

        if build_compilation:
            self.create_compilation()
        if upload_youtube:
            self.upload_youtube()

        if purge_files:
            self.purge_files()

    def _setup_project(self):
        setup_project(self.project_name)

    def purge_files(self):
        purge_project_files(self.project_name)

    def update_df(self, new_df: pd.DataFrame):
        self.df = new_df

    def add_game_info(self):
        game_list = list(set(self.statcast_df["game_pk"].values.tolist()))
        logging.info(f"Getting game info for {len(game_list)} game(s)..")
        games = Game(game_list)
        game_df = games.get_df()
        game_df.rename(
            columns={c: f"game_{c}" for c in game_df.columns.values if c != "game_pk"}
        )
        self.df = self.df.merge(game_df, how="left", on="game_pk")
        logging.info(f"Added game info.")

    def add_player_info(self):
        player_list = list(
            set(self.df["batter"].values.tolist() + self.df["pitcher"].values.tolist())
        )
        logging.info(f"Getting player info for {len(player_list)} player(s)..")
        players = Player(player_list)
        player_df = players.get_df()

        self.df = self.df.merge(
            player_df.rename(
                columns={
                    c: "batter" if c == "id" else f"batter_{c}"
                    for c in player_df.columns.values
                }
            ),
            how="left",
            on="batter",
        )
        self.df = self.df.merge(
            player_df.rename(
                columns={
                    c: "pitcher" if c == "id" else f"pitcher_{c}"
                    for c in player_df.columns.values
                }
            ),
            how="left",
            on="pitcher",
        )
        logging.info(f"Added player info.")

    def add_team_info(self):
        team_df = pd.json_normalize([v for _, v in Teams.items()])
        self.df = self.df.merge(
            team_df.rename(
                columns={
                    c: "home_team" if c == "abbreviation" else f"home_team_{c}"
                    for c in team_df.columns.values
                }
            ),
            how="left",
            on="home_team",
        )
        self.df = self.df.merge(
            team_df.rename(
                columns={
                    c: "away_team" if c == "abbreviation" else f"away_team_{c}"
                    for c in team_df.columns.values
                }
            ),
            how="left",
            on="away_team",
        )

    def transform_statcast(self, mod: Union[list, str]):
        if isinstance(mod, str):
            mod = [mod]
        for md in mod:
            self.df = _ANALYSIS_DICT.get(md)(self.df)
            logging.info(f"Transformed DF: {md}")

    def _perform_filmroom_search(self, pitch: pd.Series, params: dict) -> Tuple:
        try:
            clip = FilmRoom(pitch=pitch, local_path=self.project_path, **params)
            return clip.get_file_info()
        except Exception as e:
            logging.warning(f"FilmRoom search failed: {e}\n\n")
            return (None, None)

    def _get_filmroom_videos(
        self, params: dict = {"download": True, "feed": "Optimal"}
    ):
        self.search_filmroom = True
        logging.info(f"Starting FilmRoom search for {len(self.df)} pitch(es)..")

        self.df[["video_file_name", "video_file_path"]] = self.df.apply(
            lambda x: self._perform_filmroom_search(x), axis=1, result_type="expand"
        )

    def sort_df(self, fields: Union[list, str], ascending: Union[list, bool]):
        if isinstance(fields, str) and isinstance(ascending, bool):
            fields = [fields]
            ascending = [ascending]
        elif isinstance(fields, list) and isinstance(ascending, list):
            pass
        else:
            raise Exception("Mismatch in Parameter Count")

        self.df = self.df.sort_values(by=fields, ascending=ascending).reset_index(
            drop=True
        )
        logging.info(f"Sorted df: {fields}")

    def query_df(self, query: str):
        self.df = self.df.query(query)
        self.df = self.df.reset_index(drop=True)
        logging.info(f"Applied query to DF: {query}")

    def rank_df(
        self,
        name: str,
        group_by: Union[list, str],
        fields: Union[list, str],
        ascending: Union[list, bool],
        keep_sort: bool = False,
    ):
        if isinstance(group_by, str):
            group_by = [group_by]
        if isinstance(fields, str) and isinstance(ascending, bool):
            fields = [fields]
            ascending = [ascending]
        elif isinstance(fields, list) and isinstance(ascending, list):
            pass
        else:
            raise Exception("Mismatch in Parameter Count")
        self.df = self.df.sort_values(by=fields, ascending=ascending)
        self.df[name] = 1
        if group_by:
            self.df[name] = self.df.groupby(group_by)[name].cumsum()
        else:
            self.df[name] = self.df[name].cumsum()

        if keep_sort:
            self.df = self.df.sort_values(by=["pitch_id"], ascending=True)
        self.df = self.df.reset_index(drop=True)
        logging.info(f"Added rank field: {name} to DF")

    def get_df(self) -> pd.DataFrame:
        return self.df

    def _perform_queries(self):
        for query in self.queries:
            self.query_df(query)

    def _perform_steps(self):
        for step in self.steps:
            if step.get("type") == "query":
                self.query_df(**step.get("params"))
            elif step.get("type") == "rank":
                self.rank_df(**step.get("params"))
        self.df = self.df.reset_index(drop=True)

    # def _validate_videos(self):
    #     before_len = len(self.df)
    #     null_pitches = [
    #         (x.pitch_id, x.game_pk)
    #         for _, x in self.df[self.df["clip_file_path"].notnull() == False].iterrows()
    #     ]
    #     self.df = self.df[self.df["clip_file_path"].notnull() == True]
    #     new_len = len(self.df)
    #     if new_len < before_len:
    #         logging.info(
    #             f"Dropped {new_len-before_len} pitches due to missing video: \n {null_pitches}"
    #         )

    def create_compilation(
        self, metric_caption: str = None, player_caption: str = None
    ):
        self.build_compilation = True
        # self._validate_videos()
        if metric_caption:
            self.compilation_params["metric_caption"] = metric_caption
        if player_caption:
            self.compilation_params["player_caption"] = player_caption
        self.compilation = Compilation(
            name=self.project_name,
            df=self.df,
            local_path=self.local_path,
            **self.compilation_params,
        )

    def upload_youtube(self, youtube_params: dict = None):
        if not self.compilation:
            raise Exception("No compilation generated..")

        if not youtube_params and not self.youtube_params:
            raise Exception("Must pass a valid params dict for YT Upload..")
        elif youtube_params and self.youtube_params:
            for k, v in youtube_params.items():
                self.youtube_params[k] = v
        elif youtube_params:
            self.youtube_params = youtube_params

        self.yt_client = YouTube(
            file_path=self.compilation.comp_file, params=self.youtube_params
        )
