from mlb_videos.filmroom._constants import FEED_TYPES


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
            return [x for x in feeds if x == feed][0]
    else:
        print(f"Issue - no valid feeds found..")
        return None


def build_dict_from_nested_path(d: dict, paths: dict) -> dict:
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
