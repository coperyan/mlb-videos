import pandas as pd

COLUMNS = ["batter_delta_win_exp", "pitcher_delta_win_exp"]


def pitcher_batter_delta_win_exp(df: pd.DataFrame) -> pd.DataFrame:
    df[COLUMNS] = df.swifter.apply(
        lambda x: (
            (x.delta_home_win_exp, -1 * x.delta_home_win_exp)
            if x.inning_topbot == "Bot"
            else (-1 * x.delta_home_win_exp, x.delta_home_win_exp)
        ),
        axis=1,
        result_type="expand",
    )
