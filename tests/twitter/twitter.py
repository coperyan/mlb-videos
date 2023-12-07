import os
import requests
from requests_oauthlib import OAuth1

from mlb_videos import Twitter

twitter_api = Twitter.API()
twitter_api.post_tweet("It's that time of year. #BandOfBrothers")

# from mlb_videos.twitter.api import API

# CONSUMER_KEY = os.environ["TWITTER_CONSUMER_KEY"]
# CONSUMER_SECRET = os.environ["TWITTER_CONSUMER_SECRET"]
# ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
# ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

# create_tweet = "https://api.twitter.com/2/tweets"
# media_upload = "https://upload.twitter.com/1.1/media/upload.json"
# test_video = (
#     "/Users/rcope/dev/personal_projects/mlb-videos-dev/tests/media/test_small_video.mp4"
# )
# test_photo = (
#     "/Users/rcope/dev/personal_projects/mlb-videos-dev/tests/media/test_photo.jpg"
# )
# auth = OAuth1(
#     CONSUMER_KEY,
#     client_secret=CONSUMER_SECRET,
#     resource_owner_key=ACCESS_TOKEN,
#     resource_owner_secret=ACCESS_TOKEN_SECRET,
#     decoding=None,
# )

# resp = requests.post(create_tweet, json={"text": "This is a test."}, auth=auth)

# with open(test_photo, "rb") as f:
#     filebytes = f.read()

# files = {"media": filebytes}

# resp = requests.post(media_upload, files=files, auth=auth)

"""
                try:
                resp = self.session.request(
                    method, url, params=params, headers=headers,
                    data=post_data, files=files, json=json_payload,
                    timeout=self.timeout, auth=auth, proxies=self.proxy
                )
            except Exception as e:
                raise TweepyException(f'Failed to send request: {e}').with_traceback(sys.exc_info()[2])

"""
