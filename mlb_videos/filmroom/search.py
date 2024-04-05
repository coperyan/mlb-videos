import os
import pandas as pd

from mlb_videos.filmroom.api import API

from mlb_videos.filmroom._constants import DEFAULT_PARAMETERS
from mlb_videos.filmroom._constants import QUERIES
from mlb_videos.filmroom._helpers import build_filename, build_search_url, choose_feed, get_feeds, get_metadata


class Search:
    def __init__(
        self,
        pitch: pd.Series,
        query_params: list = DEFAULT_PARAMETERS,
        clip_priority: str = "best",
        download:bool = True,
        save_folder:str = None, 
    ):
        self.api = API()
        self.pitch = pitch
        self.query_params = query_params
        self.clip_priority = clip_priority
        self.download = download
        self.save_folder = save_folder
        self.save_name = None
        self.save_fp = None

        self.plays = None
        self.play = None
        self.clip = None
        self.feeds = None
        self.feed = None

    def _search_plays(self) -> list:
        url = build_search_url(self.pitch, self.query_params)
        results = self.api.get(
            url=url,
            headers=QUERIES.get("search").get("headers"),
            resp_path=QUERIES.get("search").get("resp_path"),
        )

        if len(results) == 0:
            url = self._build_search_url(
                self.pitch, self.query_params, exclude_params=["inning"]
            )
            results = self.api.get(
                url=url,
                headers=QUERIES.get("search").get("headers"),
                resp_path=QUERIES.get("search").get("resp_path"),
            )

        if len(results) > 0:
            return [x.get("mediaPlayback")[0].get("slug") for x in results]
        else:
            print(f"No search results found for pitch: {self.pitch.pitch_id}")
            return None

    def _search_clips(self) -> dict:
        url = QUERIES.get("clip").get("query").replace("slug_id", self.play)
        results = self.api.get(
            url=url,
            headers=QUERIES.get("clip").get("headers"),
            resp_path=QUERIES.get("clip").get("resp_path"),
        )
        if len(results) > 1:
            raise RuntimeError("More than one clip returned..")
        elif len(results) == 0:
            raise RuntimeError("No clips found for play..")
        else;
            return results[0]

    def execute(self):
        self.plays = self._search_plays()
        if self.plays:
            self.play = self.plays[0]
            self.clip = self._search_clips()
            if self.clip:
                self.clip_metadata = get_metadata(self.clip)
                self.feeds = get_feeds(self.clip)
                self.feed = choose_feed(self.priority, self.feeds)
                if self.clip_metadata and self.feed:
                    self.clip_metadata = {**self.clip_metadata, **self.feed}
                    self.save_name = build_filename(self.clip_metadata)
                    self.save_fp = os.path.join(self.save_folder,self.save_name)
                    if self.download:
                        self.api.download(self.clip_metadata.get("url"),self.save_fp)
                
