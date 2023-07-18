import os
import logging
import logging.config

# os.chdir(os.path.join(os.path.expanduser("~"), "Desktop/Dev/mlb_videos/mlb_videos"))

os.chdir("mlb_videos")

# Import modules needed
from utils import Date, setup_project
from sources.statcast import Statcast
from models.pitch import Pitches
from models.video import VideoCompilation
from clients.twitter import Tweet
from clients.youtube import Video

# Create logger
logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)

# Dates
TITLE = "202304"
TITLE_2 = "April 2023"
MIN_DT = "2023-04-01"
MAX_DT = "2023-04-30"

# Constants
PROJECT_NAME = "longest_homeruns"
PROJECT_SUFFIX = TITLE
PROJECT_ITER = f"{PROJECT_NAME}_{PROJECT_SUFFIX}"
PROJECT_PURGE = True

# Setup project folder & directory
PROJECT_PATH = setup_project(PROJECT_NAME, PROJECT_SUFFIX, PROJECT_PURGE)

# Creating Statcast Client & Getting DF
sc_client = Statcast(start_dt=MIN_DT, end_dt=MAX_DT, save=True, path=PROJECT_PATH)
sc_df = sc_client.get_df()

# Creating pitches model with statcast DF
pitches = Pitches(sc_df, PROJECT_PATH)

# Save DF
pitches.save_df(name="pitches")

# Remove bad pitches
bad_pitch_ids = ["78384|62|5", "718617|64|3", "", ""]

# Limit to home runs
pitches.df = pitches.df[pitches.df["events"] == "home_run"]
pitches.df = pitches.df[~(pitches.df["pitch_id"].isin(bad_pitch_ids))]
pitches.refresh_index()


##Now, rank longest home runs
pitches.rank_pitches(order_by="hit_distance_sc", ascending=False, name="distance_rank")

# Limit to top 25..
pitches.df = pitches.df[(pitches.df["distance_rank"] <= 30)]
pitches.refresh_index()

# Getting videos
pitches.get_videos()
pitches.df = pitches.df[pitches.df["video_path"].notnull() == True]
pitches.save_df(name="misses")

# Creating compilation
comp_path = pitches.create_compilation(name=PROJECT_ITER)

# # Uploading video to YouTube
# yt_client = Video(
#     fp=comp_path,
#     title=f"Top 25 Worst Calls - {TITLE_2} (MLB Umpires)",
#     desc=(
#         f"Back after a year, will get caught up now.. New video updated for April 2023.\n."
#         + f'These are the top 25 worst called strikes (3" + miss) OR balls (4" + miss).'
#     ),
#     tags=[],
#     privacy="public",
# )

# TWEET STUFF BELOW ...

# ##Adding game, player, team info for tweets..
# pitches.add_game_info()
# pitches.add_player_info(batters = True, pitchers = True, socials = True)
# pitches.add_team_info()
# pitches.save_df(name = 'misses_w_socials')

# ##Now, rank worst misses
# pitches.rank_pitches(
#     order_by = 'total_miss',
#     ascending = False,
#     name = 'total_miss_rank'
# )
# #Keep top 5 misses
# pitches.df = pitches.df[
#     pitches.df['total_miss_rank'] <= 5
# ]
# pitches.refresh_index()

# #Iterate and build tweets
# for index, row in pitches.df.iterrows():
#     p = row.to_dict()
#     tw = Tweet(
#         status = (
#             f'Umpire {p["home_plate_umpire"]}'
#         ),
#         media = p['video_path']
#     )
#     tw.post_tweet()
