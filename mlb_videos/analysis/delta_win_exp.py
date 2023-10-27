import os
import pandas as pd
from typing import Tuple

_DESCRIPTIONS = ["called_strike", "ball"]
_RETURN_COLS = ["batter_delta_win_exp", "pitcher_delta_win_exp"]


def calc_batter_pitcher_delta_win_exp(p: pd.Series) -> Tuple:
    """Calc Batter Pitcher Delta Win Exp

    Calculates win exp change for batter & pitcher from
    field `delta_home_win_exp` -- If bottom of inning, home is batting
    If not, home is pitching

    Parameters
    ----------
        p : pd.Series
            row of dataFrame

    Returns
    -------
        Tuple
            Batter Delta Win Exp, Pitcher Delta Win Exp
    """
    return (
        (p.delta_home_win_exp, -1 * p.delta_home_win_exp)
        if p.inning_topbot == "Bot"
        else (-1 * p.delta_home_win_exp, p.delta_home_win_exp)
    )


def get_pitcher_batter_delta_win_exp(df: pd.DataFrame) -> pd.DataFrame:
    """Get Pitcher/Batter Delta Win Exp

    Parameters
    ----------
        df : pd.DataFrame
            Statcast data to parse

    Returns
    -------
        pd.DataFrame
            Statcast data with batter/pitcher delta_win_exp added
    """
    df[_RETURN_COLS] = df.swifter.apply(
        lambda x: calc_batter_pitcher_delta_win_exp(x), axis=1, result_type="expand"
    )
    return df
