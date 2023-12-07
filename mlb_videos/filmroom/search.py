import os
import pandas as pd

from mlb_videos.filmroom._constants import DEFAULT_PARAMETERS


class Search:
    def __init__(self, pitch: pd.Series, query_params: list = DEFAULT_PARAMETERS):
        self.pitch = pitch
        self.query_params = query_params
