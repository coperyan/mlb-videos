import os
import io
import requests
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from typing import Union, Tuple


from mlb_videos.statcast._constants import ENDPOINTS
from mlb_videos.statcast._constants import REQUEST_TIMEOUT
from mlb_videos.statcast._helpers import parse_df


class API:
    BASE_URL = "https://baseballsavant.mlb.com"

    def __init__(self):
        self.endpoint = None
        self.urls = []
        self.data = []

    def cleanup(self):
        self.endpoint = None
        self.urls = []
        self.data = []

    def _make_request(self, url: str, **kwargs):
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
        return resp.content.decode("utf-8")

    def _concurrent_requests(self, **kwargs):
        print(f"Starting statcast iterations..")
        with tqdm(total=len(self.urls)) as progress:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(self._make_request, url, **kwargs)
                    for url in self.urls
                }
                for future in concurrent.futures.as_completed(futures):
                    self.data.append(future.result())
                    progress.update(1)
        print(f"Completed statcast iterations..")

    def _str_to_df(self) -> pd.DataFrame:
        df_list = []
        for d in self.data:
            df = pd.read_csv(io.StringIO(d))
            df = parse_df(df)
            if df is not None and not df.empty:
                if "error" in df.columns:
                    raise Exception(df["error"].values[0])
                else:
                    df_list.append(df)

        df = pd.concat(df_list, axis=0, ignore_index=True).convert_dtypes(
            convert_string=False
        )
        df = df.sort_values(self.endpoint.sort_keys, ascending=True)
        df[self.endpoint.uuid.name] = df.apply(
            lambda x: self.endpoint.uuid.delimiter.join(
                [str(x.get(col)) for col in self.endpoint.uuid.get("keys")]
            ),
            axis=1,
        )
        df = df[
            [self.endpoint.uuid.name]
            + [col for col in df.columns.values if col != self.endpoint.uuid.name]
        ]
        if self.endpoint.fill_na_cols:
            df[self.endpoint.fill_na_cols] = df[self.endpoint.fill_na_cols].fillna(0)

        return df

    def run(self, endpoint, urls: list, **kwargs) -> pd.DataFrame:
        self.endpoint = endpoint
        self.urls = [f"{self.BASE_URL}{url}" for url in urls]
        self._concurrent_requests(**kwargs)
        if len(self.data) > 0:
            df = self._str_to_df()
        else:
            print(f"No data found.")
        self.cleanup()
        return df
