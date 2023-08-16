import os
import time
import json
import httplib2
import http.client
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

_MAX_RETRIES = 10

_RETRIABLE_EXCEPTIONS = (
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
_RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
_VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

_CLIENT_SECRET_PATH = "credentials/client_secret.json"
_OAUTH_FILE = "credentials/oauth.json"

_YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
_YOUTUBE_API_SERVICE_NAME = "youtube"
_YOUTUBE_API_VERSION = "v3"


class Client:
    def __init__(self, file_path: str, params: dict = None):
        self.file_path = file_path
        self.params = params
        self.thumbnail = self.params.get("thumbnail", None)
        self.flow = None
        self.credentials = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        self.flow = flow_from_clientsecrets(
            _CLIENT_SECRET_PATH, scope=_YOUTUBE_UPLOAD_SCOPE
        )
        storage = Storage(_OAUTH_FILE)
        self.credentials = storage.get()

        if self.credentials is None or self.credentials.invalid:
            self.credentials = run_flow(self.flow, storage)

        self.service = build(
            _YOUTUBE_API_SERVICE_NAME,
            _YOUTUBE_API_VERSION,
            http=self.credentials.authorize(httplib2.Http()),
        )

    def _build_request_body(self):
        if self.params is None:
            self.params = {}
        body = {
            "snippet": {
                "title": self.params.get("title", "Test Video"),
                "description": self.params.get("description", "This is a test video."),
                "tags": self.params.get("tags", ["test", "python", "video"]),
                "defaultLanguage": self.params.get("language", "en_US"),
                "categoryId": self.params.get("category", "22"),
            },
            "status": {
                "privacyStatus": self.params.get("privacy", "unlisted"),
                "selfDeclaredMadeForKids": False,
            },
        }
        return body

    def _set_thumbnail(self, video_id):
        req = self.service.thumbnails().set(
            videoId=video_id, media_body=MediaFileUpload(self.thumbnail)
        )

    def _resumable_upload(self, request):
        response = None
        thumbnail_response = None
        error = None
        retry = 0

        while response is None:
            try:
                _, response = request.next_chunk()
                if "id" in response:
                    video_id = response.get("id")
                    if self.thumbnail:
                        self._set_thumbnail(video_id)
                    break
                else:
                    raise Exception(f"Unexpected response: {response}")
            except HttpError as e:
                if e.resp.status in _RETRIABLE_STATUS_CODES:
                    error = f"Retriable HTTP code: {e.resp.status} - {e.context}"
                else:
                    raise e
            except _RETRIABLE_EXCEPTIONS as e:
                error = f"Retriable error occured: {e}"

            if error is not None:
                print(error)
                retry += 1
                if retry > _MAX_RETRIES:
                    raise Exception(f"Exceeded max retries: {error}")
                print(f"Sleeping 5 seconds and retrying..")
                time.sleep(5)

    def upload(self):
        body = self._build_request_body()
        media = MediaFileUpload(self.file_path, chunksize=-1, resumable=True)
        insert_request = self.service.videos().insert(
            part=",".join(list(body.keys())), body=body, media_body=media
        )
        return self._resumable_upload(insert_request)


##https://github.com/pillargg/youtube-upload/blob/master/youtube_upload/client.py
##https://github.com/coperyan/mlb_videos/blob/main/mlb_videos/clients/youtube.py
