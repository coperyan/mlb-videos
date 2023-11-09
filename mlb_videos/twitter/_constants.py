import os
from platform import python_version


CLIENT_ID = os.environ["TWITTER_API_KEY"]
CLIENT_SECRET = os.environ["TWITTER_API_SECRET"]
ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

SCOPES = ["tweet.read", "users.read", "tweet.write"]
USER_AGENT = f"Python API - v{python_version()}"

ENDPOINTS = {
    "create_tweet": "https://api.twitter.com/2/tweets",
    "media_upload": "https://upload.twitter.com/1.1/media/upload.json",
}


VIDEO_TYPES = [".mp4", ".avi", ".h264"]
IMAGE_TYPES = [".jpg", ".jpeg", ".png", ".gif"]

DEFAULT_CHUNK_SIZE = 1024 * 1024
MAX_CHUNK_SIZE = 5 * 1024 * 1024

PENDING_STATUSES = ("pending", "in_progress")
