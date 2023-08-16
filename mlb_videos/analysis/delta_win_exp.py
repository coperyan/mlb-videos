import os
import pandas as pd
from typing import Tuple

_DESCRIPTIONS = ["called_strike", "ball"]
_RETURN_COLS = ["batter_delta_win_exp", "pitcher_delta_win_exp"]


def calc_batter_pitcher_delta_win_exp(p: pd.Series) -> Tuple:
    """ """
    return (
        (p.delta_home_win_exp, -1 * p.delta_home_win_exp)
        if p.inning_topbot == "Bot"
        else (-1 * p.delta_home_win_exp, p.delta_home_win_exp)
    )


def get_pitcher_batter_delta_win_exp(df: pd.DataFrame) -> pd.DataFrame:
    df[_RETURN_COLS] = df.swifter.apply(
        lambda x: calc_batter_pitcher_delta_win_exp(x), axis=1, result_type="expand"
    )
    return df
