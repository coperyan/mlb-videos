import os
import pandas as pd

from mlb_videos.filmroom import Clip


df_list = []
for f in ["20230429", "20230430"]:
    df_list.append(pd.read_csv(f"mlb_videos/cache/statcast/{f}.csv"))
df = pd.concat(df_list, ignore_index=True).reset_index(drop=True)
df = df.query("game_pk in (718368,718384)")
df = df.query("events=='home_run'")
df["game_date"] = pd.to_datetime(df["game_date"])
