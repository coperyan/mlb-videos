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

CALLS = ["called_strike", "swinging_strike"]
SRC_COLS = [
    "description",
    "sz_bot",
    "sz_top",
    "plate_x",
    "plate_z",
    "stand",
]
COLS = [
    "horizontal_miss_type",
    "horizontal_miss",
    "vertical_miss_type",
    "vertical_miss",
    "total_miss_type",
    "total_miss",
]


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
        (p.pfx_x * -12.00)
        + (p.pfx_z * 12.00)(abs(p.pfx_x * -12.00))
        + (abs(p.pfx_z * 12.00)),
    )


def calculate_movement(p):
    """Validates necessary fields
    Calculates movement items, returns in tuple
    """
    if p.pfx_x.notnull() and p.pfx_z.notnull():
        return pitch_movement(p)
    else:
        return (0, 0, 0, 0)


def calculate_movement_avgs(df: pd.DataFrame, gb: list = []):
    """Pass dataframe with multiple pitches
    Per pitch, we will compare movement with average
        (Depending on list of fields to group by - i.e. pitch_type)
    """
    return None
