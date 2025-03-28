import os
import requests
import pandas as pd

from mlb_videos.constants import DATE_FORMAT

from mlb_videos.filmroom._constants import DEFAULT_DOWNLOAD
from mlb_videos.filmroom._constants import DEFAULT_FEED
from mlb_videos.filmroom._constants import DEFAULT_HEADERS
from mlb_videos.filmroom._constants import DEFAULT_PARAMETERS
from mlb_videos.filmroom._constants import DOWNLOAD_CHUNK_SIZE
from mlb_videos.filmroom._constants import DOWNLOAD_SAVE_SUBFOLDER
from mlb_videos.filmroom._constants import METADATA_PATHS
from mlb_videos.filmroom._constants import QUERIES
from mlb_videos.filmroom._constants import QUERY_PARAMETERS
from mlb_videos.filmroom._constants import QUERY_SUFFIX

from mlb_videos.filmroom._helpers import build_dict_from_nested_path
from mlb_videos.filmroom._helpers import build_dict_from_nested_path_with_keys
from mlb_videos.filmroom._helpers import build_filename
from mlb_videos.filmroom._helpers import build_search_url
from mlb_videos.filmroom._helpers import choose_feed
from mlb_videos.filmroom._helpers import get_feeds
from mlb_videos.filmroom._helpers import get_metadata


class FilmRoom:
    def __init__(self):
        self.context = requests.Session()
        self.context.headers.update(DEFAULT_HEADERS)

    def _get(self, **kwargs) -> dict:
        if "resp_path" in kwargs:
            resp_path = kwargs.get("resp_path")
            kwargs.pop("resp_path")
        resp = self.context.get(**kwargs)
        if resp.status_code >= 400:
            raise RuntimeError(f"Bad request - status {resp.status_code} - {resp.text}")
        else:
            resp_json = resp.json()
            if resp_path:
                resp_json = build_dict_from_nested_path(resp_json, resp_path)
            return resp_json

    def _download(self, url: str, local_path: str):
        resp = self.context.get(url)
        if resp.status_code >= 400:
            raise RuntimeError(f"Bad request - status {resp.status_code} - {resp.text}")
        else:
            with open(local_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)

    def _search_plays(self, pitch: pd.Series, query_params: list) -> list:
        url = build_search_url(pitch, query_params)
        results = self._get(
            url=url,
            headers=QUERIES.get("search").get("headers"),
            resp_path=QUERIES.get("search").get("resp_path"),
        )

        if len(results) == 0:
            url = build_search_url(pitch, query_params, exclude_params=["inning"])
            results = self._get(
                url=url,
                headers=QUERIES.get("search").get("headers"),
                resp_path=QUERIES.get("search").get("resp_path"),
            )

        if len(results) > 0:
            return [x.get("mediaPlayback")[0].get("slug") for x in results][0]
        else:
            print(f"No search results found for pitch: {pitch.pitch_id}")
            return None

    def _search_clips(self, play, priority) -> dict:
        url = QUERIES.get("clip").get("query").replace("slug_id", play)
        results = self._get(
            url=url,
            headers=QUERIES.get("clip").get("headers"),
            resp_path=QUERIES.get("clip").get("resp_path"),
        )
        if len(results) > 1:
            raise RuntimeError("More than one clip returned..")
        elif len(results) == 0:
            raise RuntimeError("No clips found for play..")
        else:
            clip = results[0]
            clip_metadata = get_metadata(clip)
            clip_feeds = get_feeds(clip)
            clip_feed = choose_feed(priority, clip_feeds)
            clip_metadata["file_name"] = build_filename(clip_metadata)
            if clip_feed and clip_metadata:
                return {**clip_metadata, **clip_feed}

    def search(
        self,
        pitch: pd.Series,
        query_params: list = DEFAULT_PARAMETERS,
        clip_priority: str = "best",
        return_fields: list = None,
        download: bool = True,
        save_folder: str = DOWNLOAD_SAVE_SUBFOLDER,
    ):
        play = self._search_plays(pitch=pitch, query_params=query_params)
        clip = self._search_clips(play, clip_priority)
        if download:
            clip["save_path"] = os.path.join(save_folder, clip["file_name"])
            self._download(clip["url"], clip["save_path"])
        if return_fields:
            return {f: clip.get(f) for f in return_fields}
        return
