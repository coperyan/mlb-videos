import os
import mimetypes
from typing import Union

from mlb_videos.twitter._constants import ENDPOINTS
from mlb_videos.twitter._helpers import is_video_file


class Tweet:
    def __init__(self, api_client, message: str = None, files: Union[list, str] = None):
        self.api_client = api_client
        self.message = message
        self.files = files
        self.media_ids = []

    def _upload_media(self):
        for file in self.files:
            mimetype = mimetypes.guess_type(file)[0]
            if is_video_file(file):
                self.media_ids.append(
                    self.api_client._chunked_media_upload(file, mimetype)
                )
            else:
                self.media_ids.append(self.api_client._simple_media_upload(file))

    def _post_tweet(self):
        url = ENDPOINTS.get("create_tweet")
        data = {"text": self.message}

        if self.media_ids:
            data["media"] = {"media_ids": self.media_ids}

        resp = self.api_client._make_request(method="POST", url=url, json=data)

    def post(self):
        if self.files:
            self._upload_media()
        self._post_tweet()
