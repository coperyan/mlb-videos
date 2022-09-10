import os
import logging
import logging.config

os.chdir(os.path.join(os.path.expanduser("~"), "Desktop/Dev/mlb_videos/mlb_videos"))

# Import modules needed
from sources.statcast import Statcast
from models.pitch import Pitches
from models.video import VideoCompilation

# Create logger
logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)

# Search date
DATE = "2022-05-04"

# Get pitches from yesterday
# Backing up statcast for easy cache?
sc_df = Statcast(start_dt=DATE, end_dt=DATE).get_df()
sc_df.to_csv("data/statcast.csv", index=False)

# Init pitch collection from data grabbed (essentially just a class with a DF)
p = Pitches(sc_df)

# Calculating missed calls
p.calculate_missed_calls()

# Adding criteria, >= 3" strike or >= 4" ball
p.df = p.df[
    ((p.df["total_miss"] >= 3.00) & (p.df["description"] == "called_strike"))
    | ((p.df["total_miss"] >= 4.00) & (p.df["description"] == "ball"))
]

# Adding rank of worst misses
p.rank_pitches(
    partition_by=[], order_by="total_miss", ascending=False, name="total_miss_rank"
)

# Adding rank of worst change in run expectancy
p.rank_pitches(
    partition_by=[],
    order_by="delta_run_exp",
    ascending=True,
    name="total_run_exp_chg_rank",
)

# Get videos
p.get_videos()


# p.rank_pitches(
#     partition_by = ['game_date'], order_by = 'total_miss',
#     ascending = False, name = 'total_miss_rank'
# )
# #Only keeping misses >= 2"
# p.df = p.df[p.df['total_miss'] >= 2].reset_index(drop=True)
# p.df.to_csv('data/misses.csv',index=False)


# p.df = p.df[
#     ((p.df['total_miss'] >= 3) & (p.df['description'] == 'called_strike')) |
#     ((p.df['total_miss'] >= 4) & (p.df['description'] == 'ball')) |
#     (p.df['total_miss_rank'] <= 35)
# ]

# p.df = p.df.sort_values(by='total_miss_rank',ascending=True).reset_index(drop=True)

# Next, grab videos?
# p.get_videos()

# Add more info
p.add_game_info()
p.add_player_info(batters=True, pitchers=True, socials=True)
p.add_team_info()

# Create Video Compilation (test)
# vc = VideoCompilation(p.df,'top_25.mp4')
# vc.create_compilation()

# Generate some captions?
cap_fields = [
    "total_miss_rank",
    "homeplate_ump",
    "batter_fullname",
    "pitch_name",
    "release_speed",
    "video_path",
    "description",
    "des",
    "horizontal_miss",
    "horizontal_miss_type",
    "vertical_miss",
    "vertical_miss_type",
    "total_miss",
    "total_miss_type",
    "home_team_twitter_user",
    "home_team_hashtag",
    "away_team_twitter_user",
    "away_team_hashtag",
]
p.df[cap_fields].to_csv("data/limited.csv", index=False)

# Write to csv
p.df.to_csv("data/full.csv", index=False)
