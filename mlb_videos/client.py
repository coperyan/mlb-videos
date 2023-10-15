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

from .utils import _PURGE_SUBFOLDERS
from .utils import get_video_info

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
        statcast_params: dict,
        # start_date: str,
        # end_date: str = None,
        # enable_cache: bool = False,
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
        youtube_upload: bool = False,
        youtube_params: dict = {},
        purge_files: bool = False,
    ):
        """MLB Video Client - handles end-to-end

        Parameters
        ----------
            project_name : str
                used for storing project files in specific project dir
            project_path : str
                local path to store project files
            start_date : str
                start date for statcast query
            end_date (str, optional): str, default None
                end date for statcast query (if None, statcast sets to today)
            enable_cache (bool, optional): bool, default False
                Cache statcast data locally for re-use
            game_info (bool, optional): bool, default False
                Expand data model to StatsAPI and gather game info_
            player_info (bool, optional): bool, default False
                Expand data model to MLB.com and gather player info
            team_info (bool, optional): bool, default False
                Expand team info to include abbreviations, hashtags, etc.
            analysis (list, optional): list, default None
                List of analysis functions to apply, transforming dataframe
                    ex. `["umpire_calls","pitch_movement"]`
            queries (list, optional): list, default None
                List of queries to apply to dataframe
                    Each row represents string passed to df.query method
            steps (list, optional): list, default None
                Each element `step` in steps represents a query or rank method applied
            search_filmroom (bool, optional): bool, default False
                Perform search on MLB Film Room site, finding video for each record in dataframe
            filmroom_params (dict, optional): dict, default {}
                Params to pass to MLB Film Room class (feed, download(bool), etc.)
            build_compilation (bool, optional): bool, default False
                Gather clips & consolidate in comp file
            compilation_params (dict, optional): dict, default {}
                **kwargs for compilation class
            youtube_upload (bool, optional): bool, default False
                Upload compilation to Youtube
            youtube_params (dict, optional): dict, default {}
                Parameters for youtube API
                    ex. video title, description, tags, playlist to add to, privacy, thumbnail, etc.
            purge_files (bool, optional): bool, default False
                Purge local store of video clips, compilations, etc.
        """
        self.project_name = project_name
        self.local_path = project_path
        # self.start_date = start_date
        # self.end_date = end_date
        # self.enable_cache = enable_cache
        self.statcast_params = statcast_params

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
        self.youtube_upload = youtube_upload
        self.youtube_params = youtube_params
        self.purge_files = purge_files
        self.missing_videos = []

        # self.statcast_df = Statcast(
        #     start_date=start_date, end_date=end_date, enable_cache=enable_cache
        # ).get_df()
        self.statcast_df = Statcast(**self.statcast_params).get_df()

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
        if youtube_upload:
            self.upload_youtube()

        if purge_files:
            self.purge_project_media()

    def purge_project_media(self):
        """Deletes local store of media files (video, data, etc.)"""
        for subfolder in _PURGE_SUBFOLDERS:
            del_dir = os.path.join(self.local_path, subfolder)
            files = [os.path.join(del_dir, f) for f in os.listdir(del_dir)]
            for f in files:
                os.remove(f)
        logging.info(f"Purged media from project folder..")

    def update_df(self, new_df: pd.DataFrame):
        """Sets DF property within client

        Parameters
        ----------
            new_df : pd.DataFrame
        """
        self.df = new_df

    def add_game_info(self):
        """Add game info from the MLB StatsAPI to statcast dataframe

        Contains attributes for ballpark, umpire, etc.
        """
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
        """Add player info from MLB website to statcast dataframe

        Contains personal info, social media links, etc.
        """
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
        """Add team info from static file to statcast dataframe

        Contains team name abbreviations, hashtags, etc.
        """
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
        """Run each module `(analysis/*)` referenced in class.analysis

        Parameters
        ----------
            mod : Union[list, str]
                list of str or str with module names
        """
        if isinstance(mod, str):
            mod = [mod]
        for md in mod:
            self.df = _ANALYSIS_DICT.get(md)(self.df)
            logging.info(f"Transformed DF: {md}")

    def _perform_filmroom_search(self, pitch: pd.Series, params: dict) -> Tuple:
        """Performs a filmrooom search for given pitch

        Parameters
        ----------
            pitch : pd.Series
                row of data from self.df
            params : dict
                self.filmroom_params

        Returns
        -------
            Tuple
                Information about clip if found
        """
        try:
            clip = FilmRoom(pitch=pitch, local_path=self.local_path, **params)
            return clip.get_file_info()
        except Exception as e:
            logging.warning(f"FilmRoom search failed: {e}\n\n")
            return (None, None)

    def _get_filmroom_videos(
        self, params: dict = {"download": True, "feed": "Optimal"}
    ):
        """Iterates over members of self.df & performs filmroom search for all

        Parameters
        ----------
            params (dict, optional): dict, default {"download": True, "feed": "Optimal"}
                self.filmroom params
        """
        self.search_filmroom = True
        logging.info(f"Starting FilmRoom search for {len(self.df)} pitch(es)..")

        self.df[["video_file_name", "video_file_path"]] = self.df.apply(
            lambda x: self._perform_filmroom_search(x, params),
            axis=1,
            result_type="expand",
        )
        self.df[
            [
                "video_duration",
                "video_width",
                "video_height",
                "video_fps",
                "video_filesize",
            ]
        ] = self.df.apply(
            lambda x: get_video_info(x["video_file_path"])
            if not pd.isnull(x["video_file_path"])
            else (None, None, None, None, None),
            axis=1,
            result_type="expand",
        )

    def sort_df(self, fields: Union[list, str], ascending: Union[list, bool]):
        """Sort dataframe based on multiple fields

        Parameters
        ----------
            fields : Union[list, str]
                list of cols to sort by
            ascending : Union[list, bool]
                list of boolean

        Raises
        ------
            Exception
                If count of fields != ascending, raise exception
        """
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
        """Applies df.query method & resets index

        Parameters
        ----------
            query : str
                Query string to pass to query function
        """
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
        """Rank members of dataframe, multi-column, add field repr

        Parameters
        ----------
            name : str
                Col name to add for rank value
            group_by : Union[list, str]
                List of columns to groupby
            fields : Union[list, str]
                List of columns to rank by
            ascending : Union[list, bool]
                List of boolean
            keep_sort (bool, optional): bool, default False
                Keep values in same order as before

        Raises
        ------
            Exception
                If count of fields != ascending, raise exception
        """
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
        """Get DataFrame

        Returns
        -------
            pd.DataFrame
        """
        return self.df

    def _perform_queries(self):
        """Run all pre-defined queries"""
        for query in self.queries:
            self.query_df(query)

    def _perform_steps(self):
        """Run all pre-defined steps"""
        for step in self.steps:
            if step.get("type") == "query":
                self.query_df(**step.get("params"))
            elif step.get("type") == "rank":
                self.rank_df(**step.get("params"))
            elif step.get("type") == "sort":
                self.sort_df(**step.get("params"))
        self.df = self.df.reset_index(drop=True)

    def create_compilation(self):
        """Init Compilation class, generate file"""
        self.build_compilation = True
        # self._validate_videos()
        comp = Compilation(
            title=self.project_name,
            df=self.df,
            local_path=self.local_path,
            **self.compilation_params,
        )
        self.comp_file = comp.get_comp_path()

    def upload_youtube(self, youtube_params: dict = None):
        """Upload compilation to YouTube

        Parameters
        ----------
            youtube_params (dict, optional): dict, default None
                dictionary of youtube parameters

        Raises
        ------
            Exception
                _description_
            Exception
                _description_
        """
        if not self.comp_file:
            raise Exception("No compilation generated..")

        if not youtube_params and not self.youtube_params:
            raise Exception("Must pass a valid params dict for YT Upload..")
        elif youtube_params and self.youtube_params:
            for k, v in youtube_params.items():
                self.youtube_params[k] = v
        elif youtube_params:
            self.youtube_params = youtube_params

        self.yt_client = YouTube(file_path=self.comp_file, params=self.youtube_params)
