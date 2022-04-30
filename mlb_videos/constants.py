import os
import re
from datetime import date, datetime, timedelta

STATCAST_VALID_DATES = {
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

STATCAST_DATE_FORMAT = "%Y-%m-%d"
STATCAST_DATE_FORMATS = [
    (re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$'), '%Y-%m-%d'),
    (re.compile(r'^\d{4}-\d{1,2}-\d{1,2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z$'), '%Y-%m-%dT%H:%M:%S.%fZ'),
]

TEAMS = {
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