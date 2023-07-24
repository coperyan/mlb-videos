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
TITLE = "Camilo Doval 2023"
TITLE_2 = "Camilo Doval 2023"
MIN_DT = "2023-04-01"
MAX_DT = "2023-07-17"

# Constants
PROJECT_NAME = "nasty_pitches"
PROJECT_SUFFIX = TITLE
PROJECT_ITER = f"{PROJECT_NAME}_{PROJECT_SUFFIX}"
PROJECT_PURGE = True

# Setup project folder & directory
PROJECT_PATH = setup_project(PROJECT_NAME, PROJECT_SUFFIX, PROJECT_PURGE)

# Creating Statcast Client & Getting DF
sc_client = Statcast(start_dt=MIN_DT, end_dt=MAX_DT, save=True, path=PROJECT_PATH)
sc_df = sc_client.get_df()
sc_df = sc_df[sc_df["pitcher"] == 666808]

# Creating pitches model with statcast DF
pitches = Pitches(sc_df, PROJECT_PATH)

# Calculate missed calls
pitches.calculate_movement()
pitches.df = pitches.df[
    pitches.df["description"].isin(["swinging_strike", "swinging_strike_blocked"])
]


pitches.rank_pitches(
    partition_by=["pitch_type"],
    order_by="horizontal_break",
    ascending=False,
    name="horizontal_break_rank",
)
pitches.rank_pitches(
    partition_by=["pitch_type"],
    order_by="vertical_break",
    ascending=False,
    name="vertical_break_rank",
)
