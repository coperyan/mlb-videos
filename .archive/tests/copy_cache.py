import os
import pandas as pd

src_dir = "/Users/rcope/Dev/personal_projects/mlb_videos/mlb_videos/data/statcast_cache"
new_dir = "data/statcast/cache"

master_df = pd.DataFrame()
files = [os.path.join(src_dir, f) for f in os.listdir(src_dir)]

for f in files:
    if len(master_df) > 0:
        iter_df = pd.read_csv(f)
        master_df = pd.concat([master_df, iter_df])
    else:
        master_df = pd.read_csv(f)

unique_dates = list(set(master_df["game_date"].to_list()))
for ud in unique_dates:
    iter_df = master_df[master_df["game_date"] == ud]
    iter_df.to_csv(f"{new_dir}/{ud.replace('-','')}.csv", index=False)
