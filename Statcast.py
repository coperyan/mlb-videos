import io
import os
import re
import json
import requests
import pandas as pd
import concurrent.futures
from tqdm import tqdm

from Helpers import get_date_range, parse_statcast_df

with open('config.json') as f:
    CONFIG = json.load(f)

REQ_URL = CONFIG['statcast']['request_url']
FILL_COLS = CONFIG['statcast']['fill_cols']

class StatcastException(Exception):
    def __init__(self, error_msg):
        self.error_msg = error_msg
    def __str__(self):
        return self.error_msg
    
class StatcastClient:
    def __init__(self, start_date, end_date, **kwargs):
        self.start_date = start_date
        self.end_date = end_date
        self.kwargs = kwargs
        self.date_range = get_date_range(start_date,end_date)
        self.df_list = []
        self.handle_requests()
        self.transform_df()

    def make_request(self, start_date, end_date):
        """
        """
        url = REQ_URL.format(start_date = start_date, end_date = end_date)
        content = requests.get(url, timeout=None).content.decode('utf-8')
        data = pd.read_csv(io.StringIO(content))
        df = parse_statcast_df(data)
        if df is not None and not df.empty:
            if 'error' in df.columns:
                raise StatcastException(df['error'].values[0])
            df = df.sort_values(
                ['game_date','game_pk','at_bat_number','pitch_number'],
                ascending=True
            )
        return df

    def handle_requests(self):
        """
        """
        with tqdm(total=len(self.date_range)) as progress:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(
                        self.make_request,
                        s_start,
                        s_end) for s_start, s_end in self.date_range
                }
                for future in concurrent.futures.as_completed(futures):
                    self.df_list.append(future.result())
                    progress.update(1)

        if self.df_list:
            self.final_df = pd.concat(self.df_list,axis=0,ignore_index=True).convert_dtypes(convert_string=False)
            self.final_df = self.final_df.sort_values(
                ['game_date','game_pk','at_bat_number','pitch_number'],
                ascending=True
            )
        else:
            self.final_df = pd.DataFrame()

    def transform_df(self):
        """Adding a handful of items needed for ALL statcast dataframes
        Iterating over kwargs to filter dataframe columns if needed
        """
        #self.final_df = statcast_add_id(self.final_df)
        for key, value in self.kwargs.items():
            if key in self.final_df.columns:
                if type(value) == list:
                    self.final_df = self.final_df[self.final_df[key].isin(value)]
                elif type(value) == str:
                    self.final_df = self.final_df[self.final_df[key].str.lower() == value.lower()]
                else:
                    self.final_df = self.final_df[self.final_df[key] == value]

        self.final_df['pitch_id'] = self.final_df.apply(lambda x: f'{x.game_pk}|{x.at_bat_number}|{x.pitch_number}', axis = 1)
 
        self.final_df[FILL_COLS] = self.final_df[FILL_COLS].fillna(0)

    def get_df(self):
        return self.final_df

