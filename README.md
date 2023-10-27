# mlb_videos

Baseball data, analysis, but automated; with video proof

![Shohei Ohtani Missile](img/MLB_Hardest_Hits_July_2023.gif)

## Background 

As a Giants fan, I was immensely proud of our 2021 season. I spent the rough offseason watching plenty of highlights from the record year, and ended up throwing together a few compilations. After manually collecting & editing a few -- the nagging `you can automate this` voice came into my head. 

This solution provides all of the necessary resources to gather, analysis/transform, and visualize your data through video.

## Overview

### Data

The baseline for the dataset is Statcast, specifically pitches. I utilize some additional data sources (statsapi, mlb.com, etc.) to add game/player-specific attributes to the data.

### Transformation

On top of the data, there is the option to add some additional transformation (such as missed calls, pitch movement, etc.), as well as aggregation or ranked fields for analysis.

### Video Search

Next, using some key attributes unique to each pitch, I utilize the MLB's Video Room to find & download clips of the pitches I've filtered to. Each pitch has a short clip from the home/away feeds, but some of the more significant ones have 1080p+, replays, etc. 

### Compilation

From here, I use the `moviepy` package to create a compilation of these clips. I've also added the option to overlay a relevant attribute of each clip (i.e. batter/pitcher name, exit velocity, hit distance).

### YouTube

Finally, I use the YouTube API to upload the compilation. I've been able to add in some useful features here, categorizing compilations into playlists, adding relevant tags & thumbnails to improve the content quality.

## Configuration

Most of the configuration can be managed by passing parameters to the [`MLBVideoClient`](mlb_videos/client.py) class.

### Execution

- Use the client wrapper [`MLBVideoClient`](mlb_videos.client.py) to pass all necessary paramters in one initialization
- Import resources individually (i.e. [`Statcast`](mlb_videos.statcast.py), [`YouTube`](mlb_videos.youtube.py) to customize & build your own solution

## Installation

### Package

Install via PIP:

```shell
pip install mlb_videos
```

Install directly from the repository:

```shell
git clone https://github.com/coperyan/mlb_videos
cd mlb_videos
pip install -e .
```

### Other Dependencies

#### FFMPEG

FFMPEG is software used to handle everything video-related. It's used by `moviepy` when generating compilations, and is also useful for a ton of other cases.

Visit FFMpeg's [website](https://ffmpeg.org/download.html) for the latest download link. 

To verify correct installation & reference in your OS path, you can type `ffmpeg` in the terminal.

#### ImageMagick

This is a dependency for the [moviepy](https://github.com/Zulko/moviepy/tree/master) package (specifically used for adding text to the compilations)

For it to work correctly, you must add an environment variable, like so:

- Name: `IMAGEMAGICK_BINARY`
- Value: `C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe` or `/path/to/install/magick.exe`

#### YouTube API Credentials

If you want to utilize the YouTube API in this package, you will need to setup API credentials in the Google Cloud Console for your YouTube account. 

Reference Step #1 in the [YouTube API quickstart for Python](https://developers.google.com/youtube/v3/quickstart/python). 

Once you download the client_secret credentials, `mlb_videos` can reference it one of two ways:

- It is in your working directory, stored as `credentials.json`
- It is stored anywhere, with an environment variable declaring the path:
  - Name: `YOUTUBE_API_SECRET`
  - Value: `path/to/youtube/api/secret.json`

## Examples

### [Longest Home Runs (Last Month)](examples/longest_homers_last_month.py)

As an example, let's use the client to gather data & create a compilation of the longest home runs last month:

First, import the packages needed. Next, identify last month & your project title/date:

```python
# Import video client
from mlb_videos import MLBVideoClient

# Import utils, logging
import logging
import logging.config
from mlb_videos.utils import x_months_ago, setup_project2

# Get last month
last_month = x_months_ago(1)
project_title = "longest_homeruns"
project_date = f"{last_month.get('month_name')}_{last_month.get('year')}"
```

Create your project directory & configure the logger. You can create/set your own local folder instead of using the function, too:

```python
# Setup project path (creates neat subfolders) & logger
project_path = setup_project2("longest_homeruns", "september_2023")
logging.config.fileConfig(
    "logging.ini",
    defaults={
        "project_name": project_title,
        "project_date": project_date,
    },
)
logger = logging.getLogger(__name__)
```

Initialize the MLBVideoClient - for now, we will only pass the project title and project path.
You should recieve a warning - the statcast data was not grabbed due to missing parameters in the request.

Add valid parameters and run the statcast download:

```python
client.get_statcast_df(
    statcast_params={
        "start_date": last_month.get("start_date"),
        "end_date": last_month.get("end_date"),
        "events": "home run",
        "teams": ["SF"],
    }
)
client.df.head()
```

Once you have statcast data, run the `rank_df` function, filter on the top10:
```python
# Rank each home run based on the distance
client.rank_df(name="hr_distance_rank", fields="hit_distance_sc", ascending=False)

# Now filter on the top 10 ranked homers
client.query_df("hr_distance_rank <= 10")
```


Now that we're filtered down to the top 10 -- it's time to perform a search of the FilmRoom for clips:

```python
#Feed refers to `mlb_videos.filmroom._FILMROOM_FEED_TYPES`
client._get_filmroom_videos(params={"download": True, "feed": "Best"})
```

You should now be able to see each clip in your project subfolder. Create the compilation next:

```python
client.compilation_params = {
    "use_intro": False,
    "add_transitions": True,
    "transition_padding": 0.5,
    "max_clip_length": 60,
}
client.create_compilation()
```

### Videos

#### [Hardest Hit Balls of July 2023 (YouTube)](https://youtu.be/xruZbacqlQ8)

## To-Do
- Replace MoviePy with Adobe Premiere API
- Expand statcast parameters
- Start capturing additional data points (i.e. errors, catcher throwing runners out, etc.)

## Contribution

If you have any questions, comments, concerns -- please feel free to reach out to me. Cheers!