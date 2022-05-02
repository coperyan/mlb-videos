import os
import re
from pathlib import Path
from datetime import date, datetime, timedelta

DateFormat = "%Y-%m-%d"
Yesterday = (date.today() + timedelta(days=-1)).strftime(DateFormat)

def get_query(q):
  """
  """
  with open(f'../queries/{q}.txt') as f:
    query = f.read()
  return query

class DotDict(dict):
    """Dot.Notation access to dict attribs
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class Statcast:
  DateFormats = [
    (re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$'), '%Y-%m-%d'),
    (re.compile(r'^\d{4}-\d{1,2}-\d{1,2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z$'), '%Y-%m-%dT%H:%M:%S.%fZ'),
  ]
  ValidDates = {
    2008: (date(2008, 3, 25), date(2008, 10, 27)),
    2009: (date(2009, 4, 5), date(2009, 11, 4)),
    2010: (date(2010, 4, 4), date(2010, 11, 1)),
    2011: (date(2011, 3, 31), date(2011, 10, 28)),
    2012: (date(2012, 3, 28), date(2012, 10, 28)),
    2013: (date(2013, 3, 31), date(2013, 10, 30)),
    2014: (date(2014, 3, 22), date(2014, 10, 29)),
    2015: (date(2015, 4, 5), date(2015, 11, 1)),
    2016: (date(2016, 4, 3), date(2016, 11, 2)),
    2017: (date(2017, 4, 2), date(2017, 11, 1)),
    2018: (date(2018, 3, 29), date(2018, 10, 28)),
    2019: (date(2019, 3, 20), date(2019, 10, 30)),
    2020: (date(2020, 7, 23), date(2020, 10, 27)),
    2021: (date(2021, 4, 14), date(2021, 11, 2)),
    2022: (date(2022, 4,7), date(2022, 11,15))
  }
  Columns = [
       'pitch_type', 'game_date', 'release_speed', 'release_pos_x',
       'release_pos_z', 'player_name', 'batter', 'pitcher', 'events',
       'description', 'spin_dir', 'spin_rate_deprecated',
       'break_angle_deprecated', 'break_length_deprecated', 'zone', 'des',
       'game_type', 'stand', 'p_throws', 'home_team', 'away_team', 'type',
       'hit_location', 'bb_type', 'balls', 'strikes', 'game_year',
       'pfx_x', 'pfx_z', 'plate_x', 'plate_z', 'on_3b', 'on_2b', 'on_1b',
       'outs_when_up', 'inning', 'inning_topbot', 'hc_x', 'hc_y',
       'tfs_deprecated', 'tfs_zulu_deprecated', 'fielder_2', 'umpire',
       'sv_id', 'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az', 'sz_top', 'sz_bot',
       'hit_distance_sc', 'launch_speed', 'launch_angle',
       'effective_speed', 'release_spin_rate', 'release_extension',
       'game_pk', 'pitcher_1', 'fielder_2_1', 'fielder_3', 'fielder_4',
       'fielder_5', 'fielder_6', 'fielder_7', 'fielder_8', 'fielder_9',
       'release_pos_y', 'estimated_ba_using_speedangle',
       'estimated_woba_using_speedangle', 'woba_value', 'woba_denom',
       'babip_value', 'iso_value', 'launch_speed_angle', 'at_bat_number',
       'pitch_number', 'pitch_name', 'home_score', 'away_score',
       'bat_score', 'fld_score', 'post_away_score', 'post_home_score',
       'post_bat_score', 'post_fld_score', 'if_fielding_alignment',
       'of_fielding_alignment', 'spin_axis', 'delta_home_win_exp',
       'delta_run_exp', 'pitch_id'
  ]

class VideoRoom:
  Parameters = [
    {"Name": "player_id", "Url": "PlayerId", "Ref": None,"Type": "int", "EqCt": 2},
    {"Name": "batter_id", "Url": "BatterId", "Ref": "batter", "Type": "int", "EqCt": 1},
    {"Name": "pitcher_id", "Url": "PitcherId", "Ref": "pitcher", "Type": "int", "EqCt": 1},
    {"Name": "date", "Url": "Date", "Ref": "game_date", "Type": "str", "EqCt": 1},
    {"Name": "date_range", "Url": "Date", "Ref": None, "Type": "str", "EqCt": 1},
    {"Name": "season", "Url": "Season", "Ref": None, "Type": "int", "EqCt": 1},
    {"Name": "team", "Url": "Team", "Ref": None, "Type": "int", "EqCt": 1},
    {"Name": "inning", "Url": "Inning", "Ref": "inning", "Type": "int", "EqCt": 1},
    {"Name": "top_bottom", "Url": "TopBottom", "Ref": None, "Type": "str", "EqCt": 1},
    {"Name": "outs", "Url": "Outs", "Ref": None, "Type": "int", "EqCt": 1},
    {"Name": "balls", "Url": "Balls", "Ref": "balls", "Type": "int", "EqCt": 1},
    {"Name": "strikes", "Url": "Strikes", "Ref": "strikes", "Type": "int", "EqCt": 1},
    {"Name": "hit_result", "Url": "HitResult", "Ref": None, "Type": "str", "EqCt": 1},
    {"Name": "pitch_result", "Url": "PitchResult", "Ref": None, "Type": "str", "EqCt": 1},
    {"Name": "content_tags", "Url": "ContentTags", "Ref": None, "Type": "str", "EqCt": 1},
    {"Name": "pitch_type", "Url": "PitchType", "Ref": "pitch_type", "Type": "str", "EqCt": 1},
    {"Name": "pitch_speed", "Url": "PitchSpeed", "Ref": None, "Type": "int", "EqCt": 1},
    {"Name": "pitch_zone", "Url": "GameDayPitchZone", "Ref": None, "Type": "int", "EqCt": 1}
  ]
  DefaultParameters = [
    "batter_id",
    "pitcher_id",
    "date",
    "pitch_type",
    "inning",
    "balls",
    "strikes",
  ]
  Headers = {
    "Clip": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Origin": "https://www.mlb.com",
        "Referer": "https://www.mlb.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers"
      },
    "Query": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Origin": "https://www.mlb.com",
        "Referer": "https://www.mlb.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers"
      },
    "Download": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Origin": "https://www.mlb.com",
        "Referer": "https://www.mlb.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
      }
  }
  FeedTypes = DotDict({
    "Best": ["CMS_highBit","CMS_mp4Avc","NETWORK_mp4Avc","HOME_mp4Avc","AWAY_mp4Avc"],
    "Optimal": ["CMS_mp4Avc","NETWORK_mp4Avc","HOME_mp4Avc","AWAY_mp4Avc","CMS_highBit"],
    "Home": ["HOME_mp4Avc","NETWORK_mp4Avc","CMS_mp4Avc","AWAY_mp4Avc","CMS_highBit"],
    "Away": ["AWAY_mp4Avc","NETWORK_mp4Avc","CMS_mp4Avc","HOME_mp4Avc","CMS_highBit"],
  })
  Queries = {
    "Query": get_query('Query'),
    "Clip": get_query('Clip')
  }
  Responses = {
    "Query": ["data","search","plays"],
    "Clip": ["data","mediaPlayback"]
  }
  ClipMetadata = {
    "id": ["id"],
    "slug": ["slug"],
    "title": ["title"],
    "short_desc": ["blurb"],
    "long_desc": ["description"],
    "date": ["date"],
    "game_id": ["playInfo","gamePk"],
    "inning": ["playInfo","inning"],
    "outs": ["playInfo","outs"],
    "balls": ["playInfo","balls"],
    "strikes": ["playInfo","strikes"],
    "pitch_speed": ["playInfo","pitchSpeed"],
    "exit_velo": ["playInfo","exitVelocity"],
    "pitcher_id": ["playInfo","players","pitcher","id"],
    "pitcher_name": ["playInfo","players","pitcher","name"],
    "batter_id": ["playInfo","players","batter","id"],
    "batter_name": ["playInfo","players","batter","name"], 
    "home_team": ["playInfo","teams","home","triCode"],
    "away_team": ["playInfo","teams","away","triCode"],
    "batting_team": ["playInfo","teams","batting","triCode"],
    "pitching_team": ["playInfo","teams","pitching","triCode"],
    "feeds": [],
    "feed_choice": ""
  }

class Game:
  Routes = {
    'Info': DotDict({
      'Route': ['gameData','game'],
      'Columns': ['pk','season'],
      'Custom': False,
    }),
    'Dates': DotDict({
      'Route': ['gameData','datetime'],
      'Columns': ['dateTime','officialDate','dayNight','time','ampm'],
      'Custom': False,
    }),
    'AwayTeam': DotDict({
      'Route': ['gameData','teams','away'],
      'Columns': ['name','abbreviation'],
      'Custom': False,
    }),
    'HomeTeam': DotDict({
      'Route': ['gameData','teams','home'],
      'Columns': ['name','abbreviation'],
      'Custom': False,
    }),
    # 'Players': DotDict({
    #   'Route': ['gameData','players'],
    #   'Columns': ['id','fullName','link'],
    #   'Custom': True,
    # }),
    'Venue': DotDict({
      'Route': ['gameData','venue'],
      'Columns': ['name'],
      'Custom': False,
    }),
    'Umpires': DotDict({
      'Route': ['liveData','boxscore','officials'],
      'Columns': ['Home Plate','First Base','Second Base','Third Base'],
      'Custom': True,
    })
  }

class Player:
  Fields = [
    'id',
    'fullName',
    'link',
    'firstName',
    'lastName',
    'useName',
    'nickName',
    'nameSlug',
    'twitter',
    'instagram',
  ]

class Team:
  Data = {
    "SF": {
      "name": "San Francisco Giants",
      "abbreviation": "SF",
      "location": "San Francisco",
      "teamname": "Giants",
      "division": "West",
      "league": "National",
      "twitter_user": "SFGiants",
      "hashtag": "SFGameUp"
    },
    "LAD": {
      "name": "Los Angeles Dodgers",
      "abbreviation": "LAD",
      "location": "Los Angeles",
      "teamname": "Dodgers",
      "division": "West",
      "league": "National",
      "twitter_user": "Dodgers",
      "hashtag": "AlwaysLA"
    },
    "COL": {
      "name": "Colorado Rockies",
      "abbreviation": "COL",
      "location": "Denver",
      "teamname": "Rockies",
      "division": "West",
      "league": "National",
      "twitter_user": "Rockies",
      "hashtag": "Rockies"
    },
    "ARI": {
      "name": "Arizona Diamondbacks",
      "abbreviation": "ARI",
      "location": "Phoenix",
      "teamname": "Diamondbacks",
      "division": "West",
      "league": "National",
      "twitter_user": "Dbacks",
      "hashtag": "Dbacks"
    },
    "SD": {
      "name": "San Diego Padres",
      "abbreviation": "SD",
      "location": "San Diego",
      "teamname": "Padres",
      "division": "West",
      "league": "National",
      "twitter_user": "Padres",
      "hashtag": "TimeToShine"
    },
    "STL": {
      "name": "St. Louis Cardinals",
      "abbreviation": "STL",
      "location": "St. Louis",
      "teamname": "Cardinals",
      "division": "Central",
      "league": "National",
      "twitter_user": "Cardinals",
      "hashtag": "STLCards"
    },
    "CHC": {
      "name": "Chicago Cubs",
      "abbreviation": "CHC",
      "location": "Chicago",
      "teamname": "Cubs",
      "division": "Central",
      "league": "National",
      "twitter_user": "Cubs",
      "hashtag": "ItsDifferentHere"
    },
    "PIT": {
      "name": "Pittsburgh Pirates",
      "abbreviation": "PIT",
      "location": "Pittsburgh",
      "teamname": "Pirates",
      "division": "Central",
      "league": "National",
      "twitter_user": "Pirates",
      "hashtag": "LetsGoBucs"
    },
    "MIL": {
      "name": "Milwaukee Brewers",
      "abbreviation": "MIL",
      "location": "Milwaukee",
      "teamname": "Brewers",
      "division": "Central",
      "league": "National",
      "twitter_user": "Brewers",
      "hashtag": "ThisIsMyCrew"
    },
    "CIN": {
      "name": "Cincinnati Reds",
      "abbreviation": "CIN",
      "location": "Cincinnati",
      "teamname": "Reds",
      "division": "Central",
      "league": "National",
      "twitter_user": "Reds",
      "hashtag": "ATOBTTR"
    },
    "NYM": {
      "name": "New York Mets",
      "abbreviation": "NYM",
      "location": "Flushing",
      "teamname": "Mets",
      "division": "East",
      "league": "National",
      "twitter_user": "Mets",
      "hashtag": "LGM"
    },
    "ATL": {
      "name": "Atlanta Braves",
      "abbreviation": "ATL",
      "location": "Atlanta",
      "teamname": "Braves",
      "division": "East",
      "league": "National",
      "twitter_user": "Braves",
      "hashtag": "ForTheA"
    },
    "WSH": {
      "name": "Washington Nationals",
      "abbreviation": "WSH",
      "location": "Washington",
      "teamname": "Nationals",
      "division": "East",
      "league": "National",
      "twitter_user": "Nationals",
      "hashtag": "NATITUDE"
    },
    "PHI": {
      "name": "Philadelphia Phillies",
      "abbreviation": "PHI",
      "location": "Philadelphia",
      "teamname": "Phillies",
      "division": "East",
      "league": "National",
      "twitter_user": "Phillies",
      "hashtag": "RingTheBell"
    },
    "MIA": {
      "name": "Miami Marlins",
      "abbreviation": "MIA",
      "location": "Miami",
      "teamname": "Marlins",
      "division": "East",
      "league": "National",
      "twitter_user": "Marlins",
      "hashtag": "MakeItMiami"
    },
    "OAK": {
      "name": "Oakland Athletics",
      "abbreviation": "OAK",
      "location": "Oakland",
      "teamname": "Athletics",
      "division": "West",
      "league": "American",
      "twitter_user": "Athletics",
      "hashtag": "DrumTogether"
    },
    "LAA": {
      "name": "Los Angeles Angels",
      "abbreviation": "LAA",
      "location": "Anaheim",
      "teamname": "Angels",
      "division": "West",
      "league": "American",
      "twitter_user": "Angels",
      "hashtag": "GoHalos"
    },
    "SEA": {
      "name": "Seattle Mariners",
      "abbreviation": "SEA",
      "location": "Seattle",
      "teamname": "Mariners",
      "division": "West",
      "league": "American",
      "twitter_user": "Mariners",
      "hashtag": "SeaUsRise"
    },
    "HOU": {
      "name": "Houston Astros",
      "abbreviation": "HOU",
      "location": "Houston",
      "teamname": "Astros",
      "division": "West",
      "league": "American",
      "twitter_user": "astros",
      "hashtag": "LevelUp"
    },
    "TEX": {
      "name": "Texas Rangers",
      "abbreviation": "TEX",
      "location": "Arlington",
      "teamname": "Rangers",
      "division": "West",
      "league": "American",
      "twitter_user": "Rangers",
      "hashtag": "StraightUpTX"
    },
    "CLE": {
      "name": "Cleveland Guardians",
      "abbreviation": "CLE",
      "location": "Cleveland",
      "teamname": "Guardians",
      "division": "Central",
      "league": "American",
      "twitter_user": "CleGuardians",
      "hashtag": "ForTheLand"
    },
    "CWS": {
      "name": "Chicago White Sox",
      "abbreviation": "CWS",
      "location": "Chicago",
      "teamname": "White Sox",
      "division": "Central",
      "league": "American",
      "twitter_user": "whitesox",
      "hashtag": "ChangeTheGame"
    },
    "KC": {
      "name": "Kansas City Royals",
      "abbreviation": "KC",
      "location": "Kansas City",
      "teamname": "Royals",
      "division": "Central",
      "league": "American",
      "twitter_user": "Royals",
      "hashtag": "TogetherRoyal"
    },
    "MIN": {
      "name": "Minnesota Twins",
      "abbreviation": "MIN",
      "location": "Minneapolis",
      "teamname": "Twins",
      "division": "Central",
      "league": "American",
      "twitter_user": "Twins",
      "hashtag": "MNTwins"
    },
    "DET": {
      "name": "Detroit Tigers",
      "abbreviation": "DET",
      "location": "Detroit",
      "teamname": "Tigers",
      "division": "Central",
      "league": "American",
      "twitter_user": "tigers",
      "hashtag": "DetroitRoots"
    },
    "TB": {
      "name": "Tampa Bay Rays",
      "abbreviation": "TB",
      "location": "St. Petersburg",
      "teamname": "Rays",
      "division": "East",
      "league": "American",
      "twitter_user": "RaysBaseball",
      "hashtag": "RaysUp"
    },
    "TOR": {
      "name": "Toronto Blue Jays",
      "abbreviation": "TOR",
      "location": "Toronto",
      "teamname": "Blue Jays",
      "division": "East",
      "league": "American",
      "twitter_user": "BlueJays",
      "hashtag": "NextLevel"
    },
    "NYY": {
      "name": "New York Yankees",
      "abbreviation": "NYY",
      "location": "Bronx",
      "teamname": "Yankees",
      "division": "East",
      "league": "American",
      "twitter_user": "Yankees",
      "hashtag": "RepBX"
    },
    "BOS": {
      "name": "Boston Red Sox",
      "abbreviation": "BOS",
      "location": "Boston",
      "teamname": "Red Sox",
      "division": "East",
      "league": "American",
      "twitter_user": "RedSox",
      "hashtag": "DirtyWater"
    },
    "BAL": {
      "name": "Baltimore Orioles",
      "abbreviation": "BAL",
      "location": "Baltimore",
      "teamname": "Orioles",
      "division": "East",
      "league": "American",
      "twitter_user": "Orioles",
      "hashtag": "Birdland"
    }
  }
