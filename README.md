# mlb-videos

Baseball data, analysis, but automated; with video proof

![Shohei Ohtani Missile](img/MLB_Hardest_Hits_July_2023.gif)

## Background 

As a Giants fan, I was immensely proud of our 2021 season. I spent the rough offseason watching plenty of highlights from the record year, and ended up throwing together a few compilations. After manually collecting & editing a few -- the nagging `you can automate this` voice came into my head. 

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

## Examples

### [worst_calls_yesterday.py](scripts/worst_calls_yesterday.py)

Will add some more context here

### Videos

#### [Hardest Hit Balls of July 2023 (YouTube)](https://youtu.be/xruZbacqlQ8)




## References

- James LeDoux [(pybaseball)](https://github.com/jldbc/pybaseball)
- Todd Roberts [(MLB-StatsAPI)](https://github.com/toddrob99/MLB-StatsAPI)
- [MoviePy](https://github.com/Zulko/moviepy)
