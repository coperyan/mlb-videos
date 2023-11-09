import os
import httplib2
import http.client

from mlb_videos._helpers import DotDict


API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

API_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

CLIENT_SECRET_PATH = os.environ.get("YOUTUBE_API_SECRET", "client_secret.json")
OAUTH_PATH = os.environ.get("YOUTUBE_API_OAUTH", "oauth.json")


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

MAX_RETRIES = 10
RETRY_SLEEP_SECONDS = 10

RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine,
)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

PRIVACY_STATUSES = [
    "unlisted",
    "public",
    "private",
]

PLAYLIST_MAX_RESULTS = 50


ENDPOINTS = DotDict(
    {
        "video_insert": {
            "snippet": {
                "title": None,
                "description": None,
                "tags": None,
                "categoryId": None,
                "defaultLanguage": None,
                "defaultAudioLanguage": None,
            },
            "status": {
                "privacyStatus": None,
                "publishAt": None,
                "selfDeclaredMadeForKids": None,
            },
        },
        "playlist_items_insert": {
            "snippet": {
                "playlistId": None,
                "resourceId": {"kind": "youtube#video", "videoId": None},
            }
        },
    }
)
