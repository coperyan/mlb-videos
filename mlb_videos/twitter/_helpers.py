import os

from mlb_videos._helpers import get_file_information

from mlb_videos.twitter._constants import VIDEO_TYPES


def read_file_bytes(file: str) -> bytes:
    with open(file, "rb") as f:
        filebytes = f.read()
    return filebytes


def is_video_file(file: str) -> bool:
    if get_file_information(file).get("ext") in VIDEO_TYPES:
        return True
    else:
        return False
