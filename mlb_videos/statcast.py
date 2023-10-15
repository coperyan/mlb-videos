import os
import io
import re
import requests
import pandas as pd
from tqdm import tqdm
import concurrent.futures

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
    def __init__(
        self,
        start_date: str = None,
        end_date: str = None,
        games: list = None,
        batters: list = None,
        pitchers: list = None,
        pitch_types: list = None,
        events: list = None,
        descriptions: list = None,
        save_local: bool = False,
        # enable_cache: bool = False,
        # **kwargs,
    ):
        self.start_date = start_date
        self.end_date = end_date if end_date else yesterday()
        self.games = games
        self.batters = batters
        self.pitchers = pitchers
        self.pitch_types = pitch_types
        self.events = events
        self.descriptions = descriptions
        self.iteration_type = None

        self.save_local = save_local
        self.df_list = []
        # self.enable_cache = enable_cache
        self.df = None

        self._validate_args()
        self.concurrent_requests()
        self.create_df()
        if self.save_local:
            self.save_df()

    def _validate_args(self):
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

    def _build_url(self, iter_val) -> str:
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
            base_url = _REQUEST_URL + "&game_pk=" + str(iter_val)
        elif self.iteration_type == "dates":
            base_url = (
                _REQUEST_URL + "&game_date_gt=" + iter_val + "&game_date_lt=" + iter_val
            )

        if self.pitchers:
            base_url += "".join([f"&pitchers_lookup[]={x}" for x in self.pitchers])

        if self.batters:
            base_url += "".join([f"&batters_lookup[]={x}" for x in self.batters])

        return base_url

    # def initiate_requests(self):
    #     logging.info(f"Getting Statcast data")
    #     if self.enable_cache:
    #         self.cache_dates = []
    #         self.non_cache_dates = []
    #         for dt in self.date_range:
    #             if dt.replace("-", "") in [
    #                 x.replace(".csv", "") for x in os.listdir(_CACHE_PATH)
    #             ]:
    #                 self.cache_dates.append(dt)
    #             else:
    #                 self.non_cache_dates.append(dt)
    #         logging.info(
    #             f"Found {len(self.non_cache_dates)} date(s) not covered by cache"
    #         )
    #         self.get_cached_data()
    #         self.concurrent_requests_specific_dates(self.non_cache_dates)
    #     else:
    #         self.concurrent_requests()

    def _make_request(self, iter_val: str) -> pd.DataFrame:
        resp = requests.get(self._build_url(iter_val), timeout=_REQUEST_TIMEOUT)
        df = pd.read_csv(io.StringIO(resp.content.decode("utf-8")))
        df = parse_df(df)
        if df is not None and not df.empty:
            if "error" in df.columns:
                raise Exception(df["error"].values[0])
            else:
                df = df.sort_values(_DEFAULT_SORT, ascending=True)
        return df

    def concurrent_requests(self) -> None:
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

    # def concurrent_requests_specific_dates(self, date_range: list) -> None:
    #     with tqdm(total=len(date_range)) as progress:
    #         with concurrent.futures.ThreadPoolExecutor() as executor:
    #             futures = {executor.submit(self._make_request, dt) for dt in date_range}
    #             for future in concurrent.futures.as_completed(futures):
    #                 self.df_list.append(future.result())
    #                 progress.update(1)
    #     logging.info(f"Acquired {len(self.df_list)} missing day(s) of data")

    # def get_cached_data(self):
    #     for dt in self.cache_dates:
    #         df = pd.read_csv(f"{_CACHE_PATH}/{dt.replace('-','')}.csv")
    #         df["game_date"] = pd.to_datetime(df["game_date"])
    #         self.df_list.append(df)
    #     logging.info(f"Loaded in {len(self.df_list)} day(s) of cached data")

    def create_df(self) -> None:
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

    def save_df(self):
        self.df.to_csv(
            f"data/statcast/statcast_{self.start_date}_{self.end_date}.csv", index=False
        )

    def get_df(self) -> pd.DataFrame:
        return self.df
