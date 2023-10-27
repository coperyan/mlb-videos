import os
import io
import re
import requests
import pandas as pd
from tqdm import tqdm
import concurrent.futures
from typing import Union

from .utils import yesterday, get_date_range

import logging
import logging.config

logger = logging.getLogger(__name__)

# _REQUEST_URL = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={0}&game_date_lt={0}&team=&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"

_REQUEST_URL = (
    "https://baseballsavant.mlb.com/statcast_search/csv?all=true&type=details"
)
_FILLNA_COLS = ["plate_x", "plate_z", "sz_bot", "sz_top"]
_DEFAULT_SORT = ["game_date", "game_pk", "at_bat_number", "pitch_number"]

_UNIQUE_IDENTIFIER_COLS = ["game_pk", "at_bat_number", "pitch_number"]
_UNIQUE_IDENTIFIER_NAME = "pitch_id"
_UNIQUE_IDENTIFIER_DELIMITER = "|"

_REQUEST_TIMEOUT = None
_CACHE_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/cache/statcast"

_STATCAST_DATE_FORMATS = [
    (re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$"), "%Y-%m-%d"),
    (
        re.compile(r"^\d{4}-\d{1,2}-\d{1,2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z$"),
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ),
]


def parse_df(df: pd.DataFrame) -> pd.DataFrame:
    """Parse Statcast Dataframe

    Parameters
    ----------
        df : pd.DataFrame
            Dataframe -- result of statcast API request

    Returns
    -------
        pd.DataFrame
            Cleaned, parsed, normalized dataframe
    """
    str_cols = [dt[0] for dt in df.dtypes.items() if str(dt[1]) in ["object", "string"]]

    for strcol in str_cols:
        fvi = df[strcol].first_valid_index()
        if fvi is None:
            continue
        fv = df[strcol].loc[fvi]

        if str(fv).endswith("%") or strcol.endswith("%"):
            df[strcol] = (
                df[strcol].astype(str).str.replace("%", "").astype(float) / 100.0
            )
        else:
            for date_regex, date_format in _STATCAST_DATE_FORMATS:
                if isinstance(fv, str) and date_regex.match(fv):
                    df[strcol] = df[strcol].apply(
                        pd.to_datetime, errors="ignore", format=date_format
                    )
                    df[strcol] = df[strcol].convert_dtypes(convert_string=False)
                    break

    df.rename(
        columns={col: col.replace(".", "_") for col in df.columns.values if "." in col},
        inplace=True,
    )
    return df


class Statcast:
    CleanupArgs = [
        "games",
        "batters",
        "pitchers",
        "teams",
        "pitch_types",
        "events",
        "descriptions",
    ]

    """Statcast API Client"""

    def __init__(
        self,
        start_date: str = None,
        end_date: str = None,
        games: Union[list, int] = None,
        batters: Union[list, int] = None,
        pitchers: Union[list, int] = None,
        teams: Union[list, str] = None,
        # batter_teams: Union[list, str] = None,
        # pitcher_teams: Union[list, str] = None,
        pitch_types: Union[list, str] = None,
        events: Union[list, str] = None,
        descriptions: Union[list, str] = None,
        save_local: bool = False,
    ):
        """Initialize Statcast API Client

        Validates arguments, starts the concurrent requests,
        Parses the results, sets to self.df

        Parameters
        ----------
            start_date (str, optional): str, default None
                Minimum date to collect (i.e. "2023-01-01")
            end_date (str, optional): str, default None
                Maximum date to collect (i.e. "2023-01-01")
                Defaults to today-1 if not provided
            games (list, optional): list, default None
                List of game_pk's to iterate over
            batters (list, optional): list, default None
                List of MLB player IDs to filter hitters
            pitchers (list, optional): list, default None
                List of MLB player IDs to filter pitchers
            pitch_types (list, optional): list, default None
                List of pitch_types to filter
                i.e. SL, FB
            events (list, optional): list, default None
                List of events to filter
                i.e. strikeout, double play
            descriptions (list, optional): list, default None
                Description of pitch
                i.e. called strike, ball, hit_into_play
        """
        self.start_date = start_date
        self.end_date = end_date if end_date else yesterday()
        self.games = games
        self.batters = batters
        self.pitchers = pitchers
        self.teams = teams
        # self.batter_teams = batter_teams
        # self.pitcher_teams = pitcher_teams
        self.pitch_types = pitch_types
        self.events = events
        self.descriptions = descriptions
        self.iteration_type = None

        self.save_local = save_local
        self.df_list = []
        self.df = None

        self._validate_args()
        self._cleanup_args()
        self.concurrent_requests()
        self.create_df()

    def _validate_args(self):
        """Class Argument Validation

        Class must have a start_date or game_pk value to proceed.

        Raises
        ------
            ValueError
                Will raise exception if one of the mandatory args is not passed.
        """
        if self.games is not None:
            self.iteration_type = "games"
            self.iterations = self.games
            logging.info(f"Validated args, iterating by games.")
        elif self.start_date is not None:
            self.iteration_type = "dates"
            self.iterations = get_date_range(self.start_date, self.end_date)
            logging.info(f"Validated args, iterating by dates.")
        else:
            raise ValueError(
                f"Must pass either start_date or games to API for iterative use."
            )

    def _cleanup_args(self):
        """Cleanup Args

        Iterates over statcast params that can be list or single elements
        Converts them to type list in case they were passed as a single x

        """
        for arg in self.CleanupArgs:
            if (
                not isinstance(getattr(self, arg), list)
                and getattr(self, arg) is not None
            ):
                setattr(self, arg, [getattr(self, arg)])

    def _build_url(self, iter_val) -> str:
        """Build Statcast API Request URL

        For each of the main parameters in this class's init --
            Format, add to the URL's params

        Parameters
        ----------
                Value being iterated over for the current iteration
                i.e. 2023-09-01, 2023-09-02, etc.

        Returns
        -------
            str
                Request URL for self._make_request()
        """
        base_url = f"{_REQUEST_URL}"

        if self.pitch_types:
            base_url += "&hfPT=" + "".join([f"{x.upper()}|" for x in self.pitch_types])

        if self.events:
            base_url += "&hfAB=" + "".join(
                [f"{x}|".replace(" ", "\\.\\.") for x in self.events]
            )

        if self.descriptions:
            base_url += "&hfPR=" + "".join(
                [f"{x}|".replace(" ", "\\.\\.") for x in self.descriptions]
            )

        if self.iteration_type == "games":
            base_url = base_url + "&game_pk=" + str(iter_val)
        elif self.iteration_type == "dates":
            base_url = (
                base_url + "&game_date_gt=" + iter_val + "&game_date_lt=" + iter_val
            )

        if self.pitchers:
            base_url += "".join([f"&pitchers_lookup[]={x}" for x in self.pitchers])

        if self.batters:
            base_url += "".join([f"&batters_lookup[]={x}" for x in self.batters])

        ##Handle teams
        if (
            self.iteration_type == "games"
            or self.pitchers
            or self.batters
            and self.teams
        ):
            logging.warning(
                f"Team parameter passed, but game, pitcher or batter already specified.. Not applying team filter."
            )
        elif self.teams:
            (
                base_url
                + "&player_type=pitcher|batter|&hfTeam="
                + "".join([f"{x}|" for x in self.teams])
            )

        return base_url

    def _make_request(self, iter_val: str) -> pd.DataFrame:
        """Make Request to Statcast API

        Parameters
        ----------
            iter_val : str
                Value being iterated over for the current iteration
                i.e. 2023-09-01, 2023-09-02, etc.

        Raises
        ------
            Exception
                Can raise exception if the request fails for any reason.

        Returns
        -------
            pd.DataFrame
                Dataframe for the iteration
        """
        resp = requests.get(self._build_url(iter_val), timeout=_REQUEST_TIMEOUT)
        logging.info(f"Performed request for: {resp.url}")
        df = pd.read_csv(io.StringIO(resp.content.decode("utf-8")))
        df = parse_df(df)
        if df is not None and not df.empty:
            if "error" in df.columns:
                raise Exception(df["error"].values[0])
            else:
                df = df.sort_values(_DEFAULT_SORT, ascending=True)
        return df

    def concurrent_requests(self) -> None:
        """Concurrent Requests -> Statcast API

        Based on the iterator used (either day-by-day or game-by-game)
        Iterate over each value, collect the results
        """
        logging.info(f"Starting statcast iterations..")
        with tqdm(total=len(self.iterations)) as progress:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self._make_request, iter_val)
                    for iter_val in self.iterations
                }
                for future in concurrent.futures.as_completed(futures):
                    self.df_list.append(future.result())
                    progress.update(1)
        logging.info(f"Completed statcast iterations..")

    def create_df(self) -> None:
        """Create Statcast DataFrame

        Creates a consolidated statcast dataframe (self.df) --
            based on the list of dataframes returned by the iterative process

        """
        if self.df_list:
            self.df = pd.concat(self.df_list, axis=0, ignore_index=True).convert_dtypes(
                convert_string=False
            )

            self.df = self.df.sort_values(_DEFAULT_SORT, ascending=True)

            self.df[_UNIQUE_IDENTIFIER_NAME] = self.df.apply(
                lambda x: _UNIQUE_IDENTIFIER_DELIMITER.join(
                    [str(x.get(col)) for col in _UNIQUE_IDENTIFIER_COLS]
                ),
                axis=1,
            )

    # def save_df(self):
    #     self.df.to_csv(
    #         f"data/statcast/statcast_{self.start_date}_{self.end_date}.csv", index=False
    #     )

    def get_df(self) -> pd.DataFrame:
        """Get Dataframe

        Returns
        -------
            pd.DataFrame
                Statcast dataframe
        """
        return self.df
