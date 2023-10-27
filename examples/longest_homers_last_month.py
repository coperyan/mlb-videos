# Import video client
from mlb_videos import MLBVideoClient

# Import utils, logging
import logging
import logging.config
from mlb_videos.utils import x_months_ago, setup_project2

# Get last month
last_month = x_months_ago(1)
project_title = "longest_homeruns"
project_date = f"{last_month.get('month_name')}_{last_month.get('year')}"

# Setup project path (creates neat subfolders) & logger
project_path = setup_project2("longest_homeruns", "september_2023")
logging.config.fileConfig(
    "logging.ini",
    defaults={
        "project_name": project_title,
        "project_date": project_date,
    },
)
logger = logging.getLogger(__name__)

# Initialize the client
client = MLBVideoClient(project_name=project_title, project_path=project_path)

# Get statcast data between start/end of month, homeruns only
client.get_statcast_df(
    statcast_params={
        "start_date": last_month.get("start_date"),
        "end_date": last_month.get("end_date"),
        "events": "home run",
        "teams": ["SF"],
    }
)
client.df.head()

# Rank each home run based on the distance
client.rank_df(name="hr_distance_rank", fields="hit_distance_sc", ascending=False)

# Now filter on the top 10 ranked homers
client.query_df("hr_distance_rank <= 10")

# Now, let's go perform a video search, downloading the clips
client._get_filmroom_videos(params={"download": True, "feed": "Best"})

# If you travel to your project path, you can see we have a clip for each homer now
# Next, you want to consider some compilation parameters
client.compilation_params = {
    "use_intro": False,
    "add_transitions": True,
    "transition_padding": 0.5,
    "max_clip_length": 60,
}
client.create_compilation()
