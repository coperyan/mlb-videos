import os
import pandas as pd
from typing import Tuple

_USED_COLS = ["pfx_x", "pfx_z"]
_RETURN_COLS = ["horizontal_break", "vertical_break", "total_break", "total_break_abs"]


def calc_pitch_movement(p: pd.Series) -> Tuple:
    """Calc Pitch Movement

    Horizontal Break: `pfx_x` * -12 (convert to in)
    Vertical Break: `pfx_z` * 12 (convert to in)
    Total Break: Sum of two above
    Total_Break_Abs: ABS of two above

    Parameters
    ----------
        p : pd.Series
            Row of statcast data

    Returns
    -------
        Tuple
            four fields
            `horizontal_break`, `vertical_break`,
            `total_break`, `total_break_abs`
    """
    return (
        p.pfx_x * -12.00,
        p.pfx_z * 12.00,
        (p.pfx_x * -12.00) + (p.pfx_z * 12.00),
        (abs(p.pfx_x * -12.00)) + (abs(p.pfx_z * 12.00)),
    )


def get_pitch_movement(df: pd.DataFrame) -> pd.DataFrame:
    """Get Pitch Movemement

    Adds four fields to dataframe
        `horizontal_break`, `vertical_break`,
        `total_break`, `total_break_abs`

    Parameters
    ----------
        df : pd.DataFrame
            Input statcast dataframe to transform

    Returns
    -------
        pd.DataFrame
            Transformed statcast dataframe
    """
    df[_RETURN_COLS] = df.swifter.apply(
        lambda x: calc_pitch_movement(x)
        if not pd.isnull(x.pfx_x) and not pd.isnull(x.pfx_z)
        else (0.00, 0.00, 0.00, 0.00),
        axis=1,
        result_type="expand",
    )
    return df
