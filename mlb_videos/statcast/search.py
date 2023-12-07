import os
import pandas as pd
from typing import Union, Tuple
from mlb_videos.statcast.api import API

from mlb_videos._helpers import get_date_range, get_date
from mlb_videos.statcast._constants import ENDPOINTS


class Search:
    endpoint = ENDPOINTS.search

    def __init__(self, **kwargs):
        self.api = API()
        self.kwargs = kwargs

        self.iteration_type = None
        self.iterations = []
        self.urls = []

        self._validate_kwargs()
        self._cleanup_kwargs()
        self._identify_iteration_type()

        for itrn in self.iterations:
            self.urls.append(self._build_url(itrn))

    def _validate_kwargs(self) -> bool:
        bad_kwargs = {k for k in self.kwargs.keys() if k not in self.endpoint.kwargs}
        if bad_kwargs:
            raise ValueError(f"Bad kwargs passed to function: {bad_kwargs}")
        else:
            return True

    def _cleanup_kwargs(self):
        for k, v in self.kwargs.items():
            if k not in ["start_date", "end_date"] and not isinstance(v, list):
                self.kwargs[k] = [v]

        if "start_date" in self.kwargs and "end_date" not in self.kwargs:
            self.kwargs["end_date"] = get_date(days_ago=1)

    def _identify_iteration_type(self):
        if self.kwargs.get("game_pks"):
            print(f"Validated args, iterating by games.")
            self.iteration_type = "games"
            self.iterations = self.kwargs.get("game_pks")
        elif self.kwargs.get("start_date"):
            print(f"Validated args, iterating by dates.")
            date_range = get_date_range(
                self.kwargs.get("start_date"), self.kwargs.get("end_date")
            )
            self.iteration_type = "dates"
            self.iterations = date_range
        else:
            raise RuntimeError(
                f"Must pass either start_date or games to API for iterative use."
            )

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
        base_url = self.endpoint.url

        if self.kwargs.get("pitch_types"):
            base_url += "&hfPT=" + "".join(
                [f"{x.upper()}|" for x in self.kwargs.get("pitch_types")]
            )

        if self.kwargs.get("events"):
            base_url += "&hfAB=" + "".join(
                [f"{x}|".replace(" ", "\\.\\.") for x in self.kwargs.get("events")]
            )

        if self.kwargs.get("descriptions"):
            base_url += "&hfPR=" + "".join(
                [
                    f"{x}|".replace(" ", "\\.\\.")
                    for x in self.kwargs.get("descriptions")
                ]
            )

        if self.iteration_type == "games":
            base_url = base_url + "&game_pk=" + str(iter_val)

        elif self.iteration_type == "dates":
            base_url = (
                base_url + "&game_date_gt=" + iter_val + "&game_date_lt=" + iter_val
            )

        if self.kwargs.get("pitcher_ids"):
            base_url += "".join(
                [f"&pitchers_lookup[]={x}" for x in self.kwargs.get("pitcher_ids")]
            )

        if self.kwargs.get("batter_ids"):
            base_url += "".join(
                [f"&batters_lookup[]={x}" for x in self.kwargs.get("batter_ids")]
            )

        ##Handle teams
        if (
            self.iteration_type == "games"
            or self.kwargs.get("pitcher_ids")
            or self.kwargs.get("batter_ids")
        ) and self.kwargs.get("teams"):
            print(
                f"Team parameter passed, but game, pitcher or batter already specified.. Not applying team filter."
            )
        elif self.kwargs.get("teams"):
            (
                base_url
                + "&player_type=pitcher|batter|&hfTeam="
                + "".join([f"{x}|" for x in self.kwargs.get("teams")])
            )

        return base_url

    def execute(self) -> pd.DataFrame:
        df = self.api.run(
            endpoint=self.endpoint,
            urls=self.urls,
        )
        return df
