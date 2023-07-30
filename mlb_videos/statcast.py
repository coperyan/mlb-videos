import os
import io
import re
import requests
import pandas as pd
from tqdm import tqdm
import concurrent.futures

from .util import yesterday, get_date_range

# from constants import _STATCAST_DATE_FORMATS

_REQUEST_URL = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={0}&game_date_lt={0}&team=&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"
_FILLNA_COLS = ["plate_x", "plate_z", "sz_bot", "sz_top"]
_DEFAULT_SORT = ["game_date", "game_pk", "at_bat_number", "pitch_number"]

_UNIQUE_IDENTIFIER_COLS = ["game_pk", "at_bat_number", "pitch_number"]
_UNIQUE_IDENTIFIER_NAME = "pitch_id"
_UNIQUE_IDENTIFIER_DELIMITER = "|"

_REQUEST_TIMEOUT = None
_CACHE_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/data/statcast/cache"

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
        start_date: str,
        end_date: str = None,
        save_local: bool = False,
        enable_cache: bool = False,
        **kwargs,
    ):
        self.start_date = start_date
        self.end_date = end_date if end_date else yesterday()
        self.save_local = save_local
        self.kwargs = kwargs
        self.date_range = get_date_range(start_date, end_date)
        self.df_list = []
        self.enable_cache = enable_cache
        self.df = None
        self.initiate_requests()
        self.create_df()
        if self.save_local:
            self.save_df()

    def initiate_requests(self):
        if self.enable_cache:
            self.cache_dates = []
            self.non_cache_dates = []
            for dt in self.date_range:
                if dt.replace("-", "") in [
                    x.replace(".csv", "") for x in os.listdir(_CACHE_PATH)
                ]:
                    self.cache_dates.append(dt)
                else:
                    self.non_cache_dates.append(dt)
            print(f"Found {len(self.non_cache_dates)} date(s) not covered by cache")
            self.get_cached_data()
            self.concurrent_requests_specific_dates(self.non_cache_dates)
        else:
            self.concurrent_requests()

    def _make_request(self, dt: str) -> pd.DataFrame:
        resp = requests.get(_REQUEST_URL.format(dt), timeout=_REQUEST_TIMEOUT)
        df = pd.read_csv(io.StringIO(resp.content.decode("utf-8")))
        df = parse_df(df)
        if df is not None and not df.empty:
            if "error" in df.columns:
                raise Exception(df["error"].values[0])
            else:
                df = df.sort_values(_DEFAULT_SORT, ascending=True)
        return df

    def concurrent_requests(self) -> None:
        with tqdm(total=len(self.date_range)) as progress:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self._make_request, dt) for dt in self.date_range
                }
                for future in concurrent.futures.as_completed(futures):
                    self.df_list.append(future.result())
                    progress.update(1)

    def concurrent_requests_specific_dates(self, date_range: list) -> None:
        with tqdm(total=len(date_range)) as progress:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(self._make_request, dt) for dt in date_range}
                for future in concurrent.futures.as_completed(futures):
                    self.df_list.append(future.result())
                    progress.update(1)
        print(f"Acquired {len(self.df_list)} missing day(s) of data")

    def get_cached_data(self):
        for dt in self.cache_dates:
            df = pd.read_csv(f"{_CACHE_PATH}/{dt.replace('-','')}.csv")
            self.df_list.append(df)
        print(f"Loaded in {len(self.df_list)} day(s) of cached data")

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


# test = Statcast(
#     start_date="2023-07-01", end_date="2023-07-01", transform=["umpire_calls"]
# )
