import os

from mlb_videos import Statcast, FilmRoom, YouTube, Twitter


statcast = Statcast.Search(
    start_date="2024-04-03",
    end_date="2024-04-03",
    events=["home_run"],
    batter_ids=["624585"],
)

df = statcast.execute()

## Need a better way to systematically do the below
filmroom = FilmRoom.API()
search_plays = filmroom.search_plays(df.iloc[0])
search_clips = filmroom.search_clips(search_plays[0])
download_clip = filmroom.download(
    search_clips.get("url"), local_path="tests/pipeline/test.mp4"
)

twitter = Twitter.API()
twitter.post_tweet(
    message="MLB wont post it but I will. #SolerBomb", files=["tests/pipeline/test.mp4"]
)
