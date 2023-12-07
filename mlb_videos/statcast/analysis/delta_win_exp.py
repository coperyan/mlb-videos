import pandas as pd

REQUIRED_COLUMNS = ["delta_home_win_exp"]
RETURN_COLUMNS = ["batter_delta_win_exp", "pitcher_delta_win_exp"]


def pitcher_batter_delta_win_exp(df: pd.DataFrame) -> pd.DataFrame:
    df[RETURN_COLUMNS] = df.swifter.apply(
        lambda x: (
            (0.00,) * len(RETURN_COLUMNS)
            if any(pd.isnull(x[col]) for col in REQUIRED_COLUMNS)
            else (x.delta_home_win_exp, -1 * x.delta_home_win_exp)
            if x.inning_topbot == "Bot"
            else (-1 * x.delta_home_win_exp, x.delta_home_win_exp)
        ),
        axis=1,
        result_type="expand",
    )
    return df
