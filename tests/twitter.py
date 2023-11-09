from mlb_videos.twitter import *

twitter_api = Twitter.API()
twitter_api._initialize_session()


test_video = "/Users/rcope/dev/personal_projects/mlb_videos/projects/worst_calls_specific_game/718260/compilations/worst_calls_yesterday.mp4"

twitter_api._create_tweet(text="Terribly called game.", files=[test_video])
