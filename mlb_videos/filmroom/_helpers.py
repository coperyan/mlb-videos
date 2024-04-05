import os
import pandas as pd

from mlb_videos._constants import DATE_FORMAT

from mlb_videos.filmroom._constants import FEED_TYPES
from mlb_videos.filmroom._constants import METADATA_PATHS
from mlb_videos.filmroom._constants import QUERIES
from mlb_videos.filmroom._constants import QUERY_PARAMETERS
from mlb_videos.filmroom._constants import QUERY_SUFFIX


def build_search_url(
    pitch: pd.Series,
    query_params: list = None,
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
    url = QUERIES.get("search").get("query").replace('"query":""', f'"query":"{query}"')
    return url


def get_feeds(clip: dict) -> list:
    feeds = []
    for feed in clip.get("feeds"):
        for playback in feed.get("playbacks"):
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


def get_metadata(clip: dict) -> dict:
    return build_dict_from_nested_path_with_keys(clip, METADATA_PATHS)


def build_filename(d: dict) -> str:
    return (
        f"{d['game_id']}"
        f"{d['inning']}"
        f"{d['date']}_"
        f"{d['slug']}_"
        f"{d['id']}.mp4"
    )


def choose_feed(priority: str, feeds: list) -> dict:
    ##Allowed priorities
    ##Best, Normal, Home, Away
    feed_priority = []
    if priority == "best":
        feed_priority.extend(
            [f.get("id") for f in FEED_TYPES if f.get("quality") == "best"]
        )

    elif priority == "normal":
        feed_priority.extend(
            [f.get("id") for f in FEED_TYPES if f.get("quality") == "normal"]
        )

    elif priority in ["home", "away"]:
        feed_priority.extend(
            [f.get("id") for f in FEED_TYPES if f.get("type") == priority]
        )

    feed_priority.extend(
        f.get("id") for f in FEED_TYPES if f.get("id") not in feed_priority
    )

    for feed in feed_priority:
        if feed in [x.get("id") for x in feeds]:
            return [x for x in feeds if x.get("id") == feed][0]
    else:
        print(f"Issue - no valid feeds found..")
        return None


def build_dict_from_nested_path_with_keys(d: dict, paths: dict) -> dict:
    new_d = {}
    for new_key, path in paths.items():
        d_copy = d.copy()
        for key in path:
            d_copy = d_copy.get(key, {})
        if d_copy:
            new_d[new_key] = d_copy
        else:
            new_d[new_key] = None
    return new_d


def build_dict_from_nested_path(d: dict, path: list) -> dict:
    d_copy = d.copy()
    for k in path:
        d_copy = d_copy.get(k)
    return d_copy
