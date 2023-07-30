import os
import pandas as pd
from typing import Union

from .constants import Teams
from .statsapi import Game, Player
from .statcast import Statcast
from .filmroom import Video
from .util import setup_project
from .analysis.umpire_calls import get_ump_calls
from .analysis.delta_win_exp import get_adj_delta_win_exp
from .analysis.pitch_movement import get_pitch_movement

_ANALYSIS_DICT = {
    "umpire_calls": get_ump_calls,
    "adj_delta_win_exp": get_adj_delta_win_exp,
    "pitch_movement": get_pitch_movement,
}


class Data:
    def __init__(
        self,
        project_name: str,
        start_date: str,
        end_date: str = None,
        enable_cache: bool = False,
        game_info: bool = False,
        player_info: bool = False,
        team_info: bool = False,
        analysis: list = None,
        search_videos: bool = False,
        search_and_download_videos: bool = False,
    ):
        self.project_name = project_name
        self.local_path = setup_project(project_name)
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
        if search_and_download_videos:
            self.get_videos(download=True, local_path=self.local_path)
        elif search_videos:
            self.get_videos(download=False)

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

    def get_videos(self, download: bool = False):
        self.df["video_file_name"] = None
        self.df["video_file_path"] = None
        videos = []
        for index, row in self.df.iterrows():
            try:
                video = Video(
                    pitch=row, download=download, download_path=self.local_path
                )
                self.df.at[index, "video_file_name"] = video.get_clip_filename()
                self.df.at[index, "video_file_path"] = (
                    video.get_clip_filepath() if download else None
                )
                videos.append(video)
            except Exception as e:
                print(f"Error getting video for {row.pitch_id} -- {e}")

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
