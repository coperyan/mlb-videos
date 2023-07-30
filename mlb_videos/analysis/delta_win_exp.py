import os
import pandas as pd

_DESCRIPTIONS = ["called_strike", "ball"]


def calc_adj_delta_win_exp(p: pd.Series) -> float:
    """
    This is normally set to the change in win expectancy to the HOME team
    We are going to use this in the context of a bad call

    For a called ball
        If benefits home (bottom of inning and positive win % change)
        It benefits away (top of inning and negative win % change)

    For a called strike
        If benefits home (top of inning and positive win % change)
        It benefits away (bottom of inning and negative win % change)
    """
    if p.description == "ball":
        if p.inning_topbot == "Bot" and p.delta_home_win_exp > 0:
            return abs(p.delta_home_win_exp)
        elif p.inning_topbot == "Top" and p.delta_home_win_exp < 0:
            return abs(p.delta_home_win_exp)
        else:
            return 0.00

    elif p.description == "called_strike":
        if p.inning_topbot == "Top" and p.delta_home_win_exp > 0:
            return abs(p.delta_home_win_exp)
        elif p.inning_topbot == "Bot" and p.delta_home_win_exp < 0:
            return abs(p.delta_home_win_exp)
        else:
            return 0.00

    else:
        return 0.00


def get_adj_delta_win_exp(df: pd.DataFrame) -> pd.DataFrame:
    df["adj_delta_win_exp"] = df.swifter.apply(
        lambda x: calc_adj_delta_win_exp(x) if x.description in _DESCRIPTIONS else 0.00,
        axis=1,
    )
    return df
