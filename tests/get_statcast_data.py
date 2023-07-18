import os
import logging
import logging.config
import pandas as pd

# os.chdir(os.path.join(os.path.expanduser("~"), "Desktop/Dev/mlb_videos/mlb_videos"))

os.chdir("mlb_videos")

# Import modules needed
from utils import Date, setup_project
from sources.statcast import Statcast
from models.pitch import Pitches

# Create logger
logging.config.fileConfig("logging.ini")
logger = logging.getLogger(__name__)

MIN_DT = "2023-03-30"
MAX_DT = "2023-06-30"

# Creating Statcast Client & Getting DF
sc_client = Statcast(start_dt=MIN_DT, end_dt=MAX_DT, save=False)
sc_df = sc_client.get_df()

sc_df["horizontal_movement"] = sc_df.apply(
    lambda x: x.pfx_x * -12.00 if not pd.isnull(x.pfx_x) else None, axis=1
)
sc_df["vertical_movement"] = sc_df.apply(
    lambda x: x.pfx_z * 12.00 if not pd.isnull(x.pfx_z) else None, axis=1
)

sc_df.to_csv("data/statcast_cache/2023.csv", index=False)
