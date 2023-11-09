import os
import time

import httplib2
from oauth2client.file import Storage
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.tools import argparser, run_flow
from oauth2client.client import flow_from_clientsecrets

from mlb_videos._helpers import update_nested_dict_multiple_keys
from mlb_videos._helpers import remove_none_values

from mlb_videos.youtube._constants import API_SERVICE_NAME
from mlb_videos.youtube._constants import API_SCOPES
from mlb_videos.youtube._constants import API_VERSION
from mlb_videos.youtube._constants import CLIENT_SECRET_PATH
from mlb_videos.youtube._constants import ENDPOINTS
from mlb_videos.youtube._constants import MAX_RETRIES
from mlb_videos.youtube._constants import OAUTH_PATH
from mlb_videos.youtube._constants import PLAYLIST_MAX_RESULTS
from mlb_videos.youtube._constants import RETRIABLE_EXCEPTIONS
from mlb_videos.youtube._constants import RETRIABLE_STATUS_CODES
from mlb_videos.youtube._constants import RETRY_SLEEP_SECONDS


class API:
    def __init__(self):
        self.service = None
        self._authenticate()

    def _authenticate(self):
        flow = flow_from_clientsecrets(CLIENT_SECRET_PATH, scope=API_SCOPES)
        storage = Storage(OAUTH_PATH)
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage)

        self.service = build(
            API_SERVICE_NAME, API_VERSION, http=credentials.authorize(httplib2.Http())
        )

    def _build_api_body(self, endpoint: str, **kwargs):
        body = ENDPOINTS.get(endpoint)
        body = update_nested_dict_multiple_keys(body, **kwargs)
        body = remove_none_values(body)
        return body

    def _resumable_media_upload(self, request) -> str:
        response = None
        error = None
        retries = 0

        while response is None:
            try:
                _, response = request.next_chunk()
                if "id" in response:
                    video_id = response.get("id")
                    print(f"Successfully uploaded YouTube video ID: {video_id}")
                    return video_id
                else:
                    raise Exception(f"Unexpected response: {response}")
            except HttpError as e:
                if e.resp_status in RETRIABLE_STATUS_CODES:
                    error = f"Retriable status code: {e.resp_status}: {e.context}"
                else:
                    raise e

            except RETRIABLE_EXCEPTIONS as e:
                error = f"Retriable exception: {e}"

            if error is not None:
                print(error)
                retries += 1
                if retries >= MAX_RETRIES:
                    raise Exception(f"Exceeded max retries: {error}")
                else:
                    time.sleep(RETRY_SLEEP_SECONDS)

    def video_insert(self, file: str, **kwargs) -> str:
        media = MediaFileUpload(file, chunksize=-1, resumable=True)
        request_body = self._build_api_body("video_insert", **kwargs)
        request = self.service.videos().insert(
            part=",".join(list(request_body.keys())),
            body=request_body,
            media_body=media,
        )
        video_id = self._resumable_media_upload(request)
        return video_id

    def thumbnails_set(self, video_id: str, thumbnail: str):
        request = self.service.thumbnails().set(videoId=video_id, media_body=thumbnail)
        try:
            request.execute()
        except Exception as e:
            raise Exception(f"Thumbnail set command failed: {str(e)}")

    def playlists_list(
        self, max_results: int = PLAYLIST_MAX_RESULTS, search_str: str = None
    ) -> list:
        request = self.service.playlists().list(
            part="snippet,contentDetails", maxResults=max_results, mine=True
        )
        try:
            response = request.execute()
            if search_str:
                result = next(
                    (
                        p
                        for p in response.get("items")
                        if p.get("snippet").get("title") == search_str
                    ),
                    None,
                )
                return result
            else:
                return response
        except Exception as e:
            raise Exception(f"Error getting channel playlists: {e}")

    def playlist_items_insert(self, video_id: str, playlist: str):
        playlist_id = self.playlists_list(search_str=playlist).get("id")
        if playlist_id is None:
            raise Exception(f"Invalid Playlist ID parameter: {playlist}")

        request_body = self._build_api_body(
            "playlist_items_insert", playlistId=playlist_id, videoId=video_id
        )

        request = self.service.playlistItems().insert(
            part=",".join(list(request_body.keys())),
            body=request_body,
        )

        try:
            request.execute()
        except Exception as e:
            raise Exception(f"Playlist items insert command failed: {str(e)}")
