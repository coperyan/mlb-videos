import os
import logging
import logging.config
from xml.dom import NotFoundErr
import pandas as pd

# import scipy.stats as stats
from tqdm import tqdm
from collections import namedtuple

from constants import DotDict

logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)

COLS = ["horizontal_break", "vertical_break", "total_break", "total_break_abs"]


def pitch_movement(p):
    """Simple function with pitch as param:
    Returns four numbers:
        horizontal_break
        vertical_break
        total_break
        total_break_abs
    """
    return (
        p.pfx_x * -12.00,
        p.pfx_z * 12.00,
        (p.pfx_x * -12.00) + (p.pfx_z * 12.00),
        (abs(p.pfx_x * -12.00)) + (abs(p.pfx_z * 12.00)),
    )


def calculate_movement(p):
    """Validates necessary fields
    Calculates movement items, returns in tuple
    """
    if not pd.isnull(p.pfx_x) and not pd.isnull(p.pfx_z):
        return pitch_movement(p)
    else:
        return (0, 0, 0, 0)


def get_cached_data():
    file_list = [
        os.path.join("data/statcast_cache", x)
        for x in os.listdir("data/statcast_cache")
    ]
    df = pd.concat(map(pd.read_csv, file_list), ignore_index=True)
    df = df[(df["pfx_x"].notnull() == True) & (df["pfx_z"].notnull() == True)]
    return df


def get_pitch_movement_avgs(df: pd.DataFrame, group_by: list = []):
    """Pass dataframe with pitches
    Per pitch we will use cached data to compare with avg
    Returns dataframe
    """
    cached_df = get_cached_data()
    cached_df = cached_df.groupby(group_by)[
        "horizontal_movement", "vertical_movement"
    ].reset_index()
    cached_df.rename(
        columns={
            "horizontal_movement": "horizontal_movement_avg",
            "vertical_movement": "vertical_movement_avg",
        },
        inplace=True,
    )
    df = df.merge(cached_df, how="left", on=group_by)
    return df


def calculate_pitch_movement_avgs(df: pd.DataFrame):
    """Pass dataframe with multiple pitches
    Per pitch, we will compare movement with average
        (Depending on list of fields to group by - i.e. pitch_type)
    """
    avg_cols = ["horizontal_movement_avg", "vertical_movement_avg", "movement_avg_ct"]
    cached_df = get_cached_data()
    for index, row in df.iterrows():
        if any(
            map(
                pd.isnull,
                [
                    row["pfx_x"],
                    row["pfx_z"],
                    row["release_pos_y"],
                    row["release_extension"],
                    row["pitch_type"],
                    row["release_speed"],
                ],
            )
        ):
            for col in avg_cols:
                df.at[index, col] = 0
        else:
            iter_cache_df = cached_df[
                (cached_df["release_speed"] >= row["release_speed"] - 2)
                & (cached_df["release_speed"] <= row["release_speed"] + 2)
                & (cached_df["release_extension"] >= row["release_extension"] - 0.5)
                & (cached_df["release_extension"] <= row["release_extension"] + 0.5)
                & (cached_df["release_pos_y"] >= row["release_pos_y"] - 0.5)
                & (cached_df["release_pos_y"] <= row["release_pos_y"] + 0.5)
                & (cached_df["pitch_type"] == row["pitch_type"])
            ]
            avgs = iter_cache_df[["horizontal_movement", "vertical_movement"]].mean()
            df.at[index, "horizontal_movement_avg"] = avgs.get("horizontal_movement")
            df.at[index, "vertical_movement_avg"] = avgs.get("vertical_movement")
            df.at[index, "movement_avg_ct"] = len(iter_cache_df)

    return df
