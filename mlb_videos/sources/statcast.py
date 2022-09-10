import os
import io
import logging
import logging.config
import requests
import pandas as pd
from tqdm import tqdm
import concurrent.futures

import constants
from utils import get_statcast_date_range, parse_statcast_df

logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)

REQUEST_URL = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_dt}&game_date_lt={end_dt}&team=&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"
FILL_COLS = ["plate_x", "plate_z", "sz_bot", "sz_top"]
SORT_VALS = ["game_date", "game_pk", "at_bat_number", "pitch_number"]
DATA_PATH = "data"


class Statcast:
    def __init__(
        self,
        start_dt: str = None,
        end_dt: str = None,
        save: bool = True,
        path: str = None,
        **kwargs,
    ):
        """ """
        self.start_date = start_dt
        self.end_date = constants.Yesterday if not end_dt else end_dt
        self.kwargs = kwargs
        logging.info(
            f"Performing Statcast search for dates: {self.start_date} -> {self.end_date}\n"
            + f"Additional args passed: {kwargs}"
        )

        self.df_list = []
        self.final_df = pd.DataFrame()
        self.date_range = get_statcast_date_range(self.start_date, self.end_date)

        self._handle_requests()
        self._fill_df_cols()
        self._add_pitch_id()
        self._apply_df_filters()
        logging.info(
            f"Completed Statcast search - result: {len(self.final_df)} row(s).."
        )
        if save:
            self.final_df.to_csv(
                os.path.join(path, DATA_PATH, "statcast.csv"), index=False
            )

    def _make_request(self, start_dt: str = None, end_dt: str = None) -> pd.DataFrame:
        """ """
        resp = requests.get(
            REQUEST_URL.format(start_dt=start_dt, end_dt=end_dt), timeout=None
        )
        content = resp.content.decode("utf-8")
        data = pd.read_csv(io.StringIO(content))
        df = parse_statcast_df(data)
        if df is not None and not df.empty:
            if "error" in df.columns:
                raise Exception(df["error"].values[0])
            else:
                df = df.sort_values(SORT_VALS, ascending=True)
        return df

    def _handle_requests(self):
        """ """
        with tqdm(total=len(self.date_range)) as progress:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self._make_request, s_start, s_end)
                    for s_start, s_end in self.date_range
                }
                for future in concurrent.futures.as_completed(futures):
                    self.df_list.append(future.result())
                    progress.update(1)

        if self.df_list:
            self.final_df = pd.concat(
                self.df_list, axis=0, ignore_index=True
            ).convert_dtypes(convert_string=False)
            self.final_df = self.final_df.sort_values(
                ["game_date", "game_pk", "at_bat_number", "pitch_number"],
                ascending=True,
            )
        else:
            self.final_df = pd.DataFrame()

    def _add_pitch_id(self):
        """ """
        self.final_df["pitch_id"] = self.final_df.apply(
            lambda x: f"{x.game_pk}|{x.at_bat_number}|{x.pitch_number}", axis=1
        )

    def _apply_df_filters(self):
        """ """
        if not self.kwargs:
            return

        for key, value in self.kwargs.items():
            if key in self.final_df.columns:
                if type(value) == list:
                    self.final_df = self.final_df[self.final_df[key].isin(value)]
                elif type(value) == str:
                    self.final_df = self.final_df[
                        self.final_df[key].str.lower() == value.lower()
                    ]
                else:
                    self.final_df = self.final_df[self.final_df[key] == value]

    def _fill_df_cols(self):
        """ """
        self.final_df[FILL_COLS] = self.final_df[FILL_COLS].fillna(0)

    def get_df(self):
        """ """
        return self.final_df
