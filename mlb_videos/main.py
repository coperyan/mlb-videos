import os
import pandas as pd
from typing import Union

import logging
import logging.config

logger = logging.getLogger(__name__)

from .constants import Teams
from .statsapi import Game, Player
from .statcast import Statcast
from .filmroom import Clip
from .analysis.umpire_calls import get_ump_calls
from .analysis.delta_win_exp import get_pitcher_batter_delta_win_exp
from .analysis.pitch_movement import get_pitch_movement


_ANALYSIS_DICT = {
    "umpire_calls": get_ump_calls,
    "pitcher_batter_delta_win_exp": get_pitcher_batter_delta_win_exp,
    "pitch_movement": get_pitch_movement,
}


class Data:
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
        search_clips: bool = False,
        search_and_download_clips: bool = False,
    ):
        self.project_name = project_name
        self.local_path = project_path
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
        if search_and_download_clips:
            self.get_clips(download=True, local_path=self.local_path)
        elif search_clips:
            self.get_clips(download=False)

    def update_df(self, new_df: pd.DataFrame):
        self.df = new_df

    def add_game_info(self):
        games = Game(list(set(self.statcast_df["game_pk"].values.tolist())))
        game_df = games.get_df()
        game_df.rename(
            columns={c: f"game_{c}" for c in game_df.columns.values if c != "game_pk"}
        )
        self.df = self.df.merge(game_df, how="left", on="game_pk")

    def add_player_info(self):
        players = Player(
            list(
                set(
                    self.df["batter"].values.tolist()
                    + self.df["pitcher"].values.tolist()
                )
            )
        )
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

    def get_clips(self, download: bool = False):
        self.df["clip_file_name"] = None
        self.df["clip_file_path"] = None
        clip = []
        for index, row in self.df.iterrows():
            try:
                clip = Clip(pitch=row, download=download, download_path=self.local_path)
                self.df.at[index, "clip_file_name"] = clip.get_clip_filename()
                self.df.at[index, "clip_file_path"] = (
                    clip.get_clip_filepath() if download else None
                )
                clip.append(clip)
            except Exception as e:
                print(f"Error getting clip for {row.pitch_id} -- {e}")

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

    def query_df(self, query: str):
        self.df = self.df.query(query)

    def rank_df(
        self,
        name: str,
        group_by: Union[list, str],
        fields: Union[list, str],
        ascending: Union[list, bool],
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

        self.df = self.df.reset_index(drop=True)

    def get_df(self) -> pd.DataFrame:
        return self.df
