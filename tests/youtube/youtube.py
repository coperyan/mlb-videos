import pytz
from datetime import datetime, timedelta

from mlb_videos import YouTube

publish_at = datetime.now(pytz.timezone("America/Los_Angeles")) + timedelta(days=1)


YouTube.Video(
    file="tests/test_video.mp4",
    title="Test Video",
    description="This is a test, please ignore.",
    playlist="Test",
    thumbnail="tests/test_photo.jpg",
    privacyStatus="private",
    publishAt=publish_at.isoformat(),
)
