import os
import swifter
import pandas as pd
from typing import Tuple

_AVG_ERROR = 0.25
_SAMPLE = 10000
_BALL_RADIUS = 0.12
_PROB_REQ = 90
_ZONE_RADIUS = 0.83
_ZONE_WIDTH = _ZONE_RADIUS * 2
X1 = -_ZONE_RADIUS
X2 = X1 + _ZONE_WIDTH

_DESCRIPTIONS = ["called_strike", "ball"]
_USED_COLS = [
    "description",
    "sz_bot",
    "sz_top",
    "plate_x",
    "plate_z",
    "stand",
]
_RETURN_COLS = [
    "horizontal_miss_type",
    "horizontal_miss",
    "vertical_miss_type",
    "vertical_miss",
    "total_miss_type",
    "total_miss",
]


def generate_coords(sz_bot, sz_top, plate_x, plate_z):
    """Basic calcs used to determine misses
    Geometry...
    """
    return {
        "W": (_ZONE_WIDTH),
        "X1": -_ZONE_RADIUS,
        "X2": (-_ZONE_RADIUS + (_ZONE_WIDTH)),
        "Y1": (sz_bot - _BALL_RADIUS),
        "Y2": (sz_top + _BALL_RADIUS),
        "X": plate_x,
        "Y": plate_z,
    }


def calc_strike_miss(p: dict) -> Tuple:
    if p.get("X") < p.get("X1"):
        horizontal_miss = round((p.get("X1") - p.get("X")) * 12.00, 2)
        horizontal_miss_type = "inside" if p.get("stand") == "R" else "outside"
    elif p.get("X") > p.get("X2"):
        horizontal_miss = round((p.get("X") - p.get("X2")) * 12.00, 2)
        horizontal_miss_type = "outside" if p.get("stand") == "R" else "inside"
    else:
        horizontal_miss = 0.00
        horizontal_miss_type = None

    if p.get("Y") < p.get("Y1"):
        vertical_miss = round((p.get("Y1") - p.get("Y")) * 12.00, 2)
        vertical_miss_type = "low"
    elif p.get("Y") > p.get("Y2"):
        vertical_miss = round((p.get("Y") - p.get("Y2")) * 12.00, 2)
        vertical_miss_type = "high"
    else:
        vertical_miss = 0
        vertical_miss_type = None

    total_miss = round(horizontal_miss + vertical_miss, 2)
    total_miss_type = (
        "both"
        if horizontal_miss > 0 and vertical_miss > 0
        else horizontal_miss_type
        if horizontal_miss > 0
        else vertical_miss_type
        if vertical_miss > 0
        else None
    )
    return (
        horizontal_miss_type,
        horizontal_miss,
        vertical_miss_type,
        vertical_miss,
        total_miss_type,
        total_miss,
    )


def calc_ball_miss(p: dict) -> Tuple:
    if (p.get("X1") < p.get("X") and p.get("X") < p.get("X2")) and (
        p.get("Y1") < p.get("Y") and p.get("Y") < p.get("Y2")
    ):
        if p.get("X") <= 0:
            horizontal_miss = round((p.get("X") - p.get("X1")) * 12.00, 2)
            horizontal_miss_type = "inside" if p.get("stand") == "R" else "outside"
        elif p.get("X") >= 0:
            horizontal_miss = round((p.get("X2") - p.get("X")) * 12.00, 2)
            horizontal_miss_type = "outside" if p.get("stand") == "R" else "inside"

        if p.get("Y") <= (p.get("sz_bot") + ((p.get("sz_top") - p.get("sz_bot")) / 2)):
            vertical_miss = round((p.get("Y") - p.get("Y1")) * 12.00, 2)
            vertical_miss_type = "low"
        elif p.get("Y") >= (
            p.get("sz_bot") + ((p.get("sz_top") - p.get("sz_bot")) / 2)
        ):
            vertical_miss = round((p.get("Y2") - p.get("Y")) * 12.00, 2)
            vertical_miss_type = "high"

    else:
        horizontal_miss, horizontal_miss_type, vertical_miss, vertical_miss_type = [
            0,
            None,
            0,
            None,
        ]

    total_miss = round(min(horizontal_miss, vertical_miss), 2)
    total_miss_type = (
        "both"
        if horizontal_miss > 0 and vertical_miss > 0
        else horizontal_miss_type
        if horizontal_miss > 0
        else vertical_miss_type
        if vertical_miss > 0
        else None
    )
    return (
        horizontal_miss_type,
        horizontal_miss,
        vertical_miss_type,
        vertical_miss,
        total_miss_type,
        total_miss,
    )


def calculate_miss(p: pd.Series) -> Tuple:
    if any(pd.isnull(v) for v in (p.plate_x, p.plate_z, p.sz_bot, p.sz_top)):
        return [None, 0.00] * 3
    elif any(v == 0 for v in (p.plate_x, p.plate_z, p.sz_bot, p.sz_top)):
        return [None, 0.00] * 3
    elif p.description not in _DESCRIPTIONS:
        return [None, 0.00] * 3
    else:
        d = {x: getattr(p, x) for x in _USED_COLS}
        d.update(generate_coords(p.sz_bot, p.sz_top, p.plate_x, p.plate_z))

        if p.description == "called_strike":
            return calc_strike_miss(d)
        elif p.description == "ball":
            return calc_ball_miss(d)


def get_ump_calls(df: pd.DataFrame) -> pd.DataFrame:
    df[_RETURN_COLS] = df.swifter.apply(
        lambda x: calculate_miss(x), axis=1, result_type="expand"
    )
    return df