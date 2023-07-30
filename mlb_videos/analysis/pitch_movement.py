import os
import pandas as pd
from typing import Tuple

_USED_COLS = ["pfx_x", "pfx_z"]
_RETURN_COLS = ["horizontal_break", "vertical_break", "total_break", "total_break_abs"]


def calc_pitch_movement(p: pd.Series) -> Tuple:
    return (
        p.pfx_x * -12.00,
        p.pfx_z * 12.00,
        (p.pfx_x * -12.00) + (p.pfx_z * 12.00),
        (abs(p.pfx_x * -12.00)) + (abs(p.pfx_z * 12.00)),
    )


def get_pitch_movement(df: pd.DataFrame) -> pd.DataFrame:
    df[_RETURN_COLS] = df.swifter.apply(
        lambda x: calc_pitch_movement(x)
        if not pd.isnull(x.pfx_x) and not pd.isnull(x.pfx_z)
        else (0.00, 0.00, 0.00, 0.00),
        axis=1,
        result_type="expand",
    )
    return df
