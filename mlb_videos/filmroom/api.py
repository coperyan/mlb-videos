import os
import requests
import pandas as pd

from mlb_videos._constants import DATE_FORMAT

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

from mlb_videos.filmroom._helpers import build_dict_from_nested_path, choose_feed


class API:
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

    def download(self, url: str, local_path: str):
        resp = self.context.get(url)
        if resp.status_code >= 400:
            raise RuntimeError(f"Bad request - status {resp.status_code} - {resp.text}")
        else:
            with open(local_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)

    def _build_search_url(
        self,
        pitch: pd.Series,
        query_params: list = DEFAULT_PARAMETERS,
        exclude_params: list = None,
    ) -> str:
        query = ""

        if exclude_params:
            query_params = [x for x in query_params if x not in exclude_params]

        for param in query_params:
            param_ref = next(filter(lambda x: x.get("Name") == param, QUERY_PARAMETERS))
            param_val = pitch.get(param_ref["Ref"], {})
            if param == "date":
                param_val = param_val.strftime(DATE_FORMAT)
            eq_sep = "=" * param_ref["EqCt"]
            sp_pad = r"\"" if param_ref["Type"] == "str" else ""

            sparam_str = f"{param_ref['Url']} {eq_sep} [{sp_pad}{param_val}{sp_pad}]"

            if query == "":
                query = sparam_str
            else:
                query += f" AND {sparam_str}"

        query = f"{query} {QUERY_SUFFIX}"
        url = (
            QUERIES.get("search")
            .get("query")
            .replace('"query":""', f'"query":"{query}"')
        )
        return url

    def _get_feeds(self, clip: dict) -> list:
        feeds = []
        for feed in clip.get("feeds"):
            for playback in clip.get("playbacks"):
                if ".mp4" in os.path.basename(playback.get("url")).lower():
                    feeds.append(
                        {
                            "id": f"{feed.get('type')}_{playback.get('name')}",
                            "type": feed.get("type"),
                            "name": playback.get("name"),
                            "url": playback.get("url"),
                        }
                    )
        return feeds

    def search_plays(
        self,
        pitch: pd.Series,
        query_params: list = DEFAULT_PARAMETERS,
    ) -> list:
        url = self._build_search_url(pitch, query_params)
        results = self._get(
            url=url,
            headers=QUERIES.get("search").get("headers"),
            resp_path=QUERIES.get("search").get("resp_path"),
        )

        if len(results) == 0:
            url = self._build_search_url(pitch, query_params, exclude_params=["inning"])
            results = self._get(
                url=url,
                headers=QUERIES.get("search").get("headers"),
                resp_path=QUERIES.get("search").get("resp_path"),
            )

        if len(results) > 0:
            return [x.get("mediaPlayback")[0].get("slug") for x in results]
        else:
            print(f"No search results found for pitch: {pitch.pitch_id}")
            return []

    def search_clips(self, play_id: str, priority: str = "best") -> dict:
        url = QUERIES.get("clip").replace("slug_id", play_id)
        results = self._make_request(
            url=url,
            headers=QUERIES.get("clip").get("headers"),
            resp_path=QUERIES.get("clip").get("resp_path"),
        )
        clip = results[0]
        clip_metadata = build_dict_from_nested_path(clip, METADATA_PATHS)
        clip_feeds = self._get_feeds(clip)
        clip_feed = choose_feed(priority, clip_feeds)
        clip_metadata["file_name"] = (
            f"{clip_metadata['game_id']}"
            f"{clip_metadata['inning']}"
            f"{clip_metadata['date']}_"
            f"{clip_metadata['slug']}_"
            f"{clip_feed['id']}.mp4"
        )
        if clip_feed and clip_metadata:
            return {**clip_metadata, **clip_feed}
        else:
            return None
