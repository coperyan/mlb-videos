import os
import time
import requests
import mimetypes
from typing import Union
from requests_oauthlib import OAuth1

from mlb_videos.twitter._helpers import read_file_bytes

from mlb_videos.twitter._constants import ACCESS_TOKEN
from mlb_videos.twitter._constants import ACCESS_TOKEN_SECRET
from mlb_videos.twitter._constants import CONSUMER_KEY
from mlb_videos.twitter._constants import CONSUMER_SECRET
from mlb_videos.twitter._constants import DEFAULT_CHUNK_SIZE
from mlb_videos.twitter._constants import ENDPOINTS
from mlb_videos.twitter._constants import MAX_CHUNK_SIZE
from mlb_videos.twitter._constants import PENDING_STATUSES
from mlb_videos.twitter._constants import SCOPES
from mlb_videos.twitter._constants import USER_AGENT
from mlb_videos.twitter._constants import VIDEO_TYPES

from mlb_videos.twitter.tweet import Tweet


class API:
    def __init__(self):
        self.session = None
        self.oauth1 = None
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def _get_auth(self):
        return OAuth1(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=ACCESS_TOKEN,
            resource_owner_secret=ACCESS_TOKEN_SECRET,
            decoding=None,
        )

    def _make_request(self, method: str, url: str, **kwargs) -> dict:
        auth = self._get_auth()
        resp = self.session.request(method=method, url=url, **kwargs, auth=auth)
        print(f"Url: {url} Status: {resp.status_code}")
        if resp.status_code >= 400:
            print(resp.text)
            print(resp.json())
        try:
            return resp.json()
        except Exception as e:
            print(e)
            return {}

    def _simple_media_upload(self, file: str) -> str:
        resp = self._make_request(
            method="POST",
            url=ENDPOINTS.get("media_upload"),
            files={"media": read_file_bytes(file)},
        )
        if "media_id" in resp:
            return str(resp.get("media_id"))
        else:
            pass

    def _chunked_media_upload(
        self,
        file: str,
        file_type: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        wait_for_processing: bool = True,
    ) -> str:
        fp = open(file, "rb")
        start = fp.tell()
        fp.seek(0, 2)
        file_size = fp.tell() - start
        fp.seek(start)

        min_chunk_size, remainder = divmod(file_size, 1000)
        min_chunk_size += bool(remainder)

        chunk_size = max(min(chunk_size, MAX_CHUNK_SIZE), min_chunk_size)

        segments, remainder = divmod(file_size, chunk_size)
        segments += bool(remainder)

        media_id = self._chunked_media_upload_initialize(
            file_size=file_size, file_type=file_type
        )

        for segment_index in range(segments):
            self._chunked_media_upload_append(
                media_id=media_id,
                media=(file, fp.read(chunk_size)),
                segment_index=segment_index,
            )

        fp.close()
        media = self._chunked_media_upload_finalize(media_id)

        if wait_for_processing and "processing_info" in media:
            while media.get("processing_info").get(
                "state"
            ) in PENDING_STATUSES and "error" not in media.get("processing_info"):
                time.sleep(media.get("processing_info").get("check_after_secs"))
                media = self._get_media_upload_status(media.get("media_id"))

        return str(media.get("media_id"))

    def _chunked_media_upload_initialize(self, file_size: float, file_type: str) -> str:
        resp = self._make_request(
            method="POST",
            url=ENDPOINTS.get("media_upload"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "command": "INIT",
                "total_bytes": file_size,
                "media_type": file_type,
            },
        )
        print(resp)
        if "media_id" in resp:
            return str(resp.get("media_id"))
        else:
            pass

    def _chunked_media_upload_append(self, media_id: str, media, segment_index):
        self._make_request(
            method="POST",
            url=ENDPOINTS.get("media_upload"),
            data={
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": segment_index,
            },
            files={"media": media},
        )

    def _chunked_media_upload_finalize(self, media_id: str) -> dict:
        resp = self._make_request(
            method="POST",
            url=ENDPOINTS.get("media_upload"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"command": "FINALIZE", "media_id": media_id},
        )
        print(f"Finalize check: {resp}")
        return resp

    def _get_media_upload_status(self, media_id: str) -> dict:
        resp = self._make_request(
            method="GET",
            url=ENDPOINTS.get("media_upload"),
            params={"command": "STATUS", "media_id": media_id},
        )
        print(f"Status check: {resp}")
        return resp

    def post_tweet(self, message: str = None, files: list = None):
        return Tweet(api_client=self, message=message, files=files).post()


# test = API()
# test.post_tweet(message="TESTING API")
