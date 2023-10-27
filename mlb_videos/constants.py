import os
import re
from datetime import date

_DT_FORMAT = "%Y-%m-%d"

_PLAYLISTS = {
    "Umpires - Worst Calls": "PL80vk26kxQPFETbnOeJ9rVHOZCHNFYd0g",
    "Longest Home Runs": "PL80vk26kxQPHR4iz3yGqqGOW6VXasrvfZ",
    "San Francisco Giants - Team Highlights": "PL80vk26kxQPEUB3XOnss7gdD2dvC_HJAU",
    "San Francisco Giants - Player Highlights": "PL80vk26kxQPH4jqpfixZLVkXUncXoJ7mb",
    "Hardest Hits": "PL80vk26kxQPHQ71k_9iCh0bddq9nE1Gi3",
}

_STANDARD_TAGS = [
    "mlb",
    "baseball",
    "highlights",
    "baseball highlights",
    "mlb highlights",
    "shohei ohtani",
    "mookie betts",
    "freddie freeman",
    "ronald acuna jr",
    "wander franco",
    "corey seager",
    "matt olson",
    "ozzie albies",
    "brett phillips",
    "barry bonds",
    "francisco lindor",
    "max scherzer",
    "ken griffrey jr",
    "tony gwynn",
    "juan soto",
    "kyle tucker",
    "julio rodriguez",
    "elly de la cruz",
    "fernando tatis jr",
]

_SEASON_DATES = {
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
    2022: (date(2022, 4, 7), date(2022, 11, 15)),
    2023: (date(2023, 3, 30), date(2023, 11, 15)),
}


_PITCH_TYPES = {
    "FF": {"Name": "Four-Seam Fastball", "Group": "Fastball"},
    "ST": {"Name": "Sweeper", "Group": "Breaking"},
    "FS": {"Name": "Splitter", "Group": "Offspeed"},
    "SI": {"Name": "Sinker", "Group": "Fastball"},
    "CU": {"Name": "Curveball", "Group": "Breaking"},
    "CH": {"Name": "Change-up", "Group": "Offspeed"},
    "FC": {"Name": "Cutter", "Group": "Fastball"},
    "SL": {"Name": "Slider", "Group": "Breaking"},
    "KC": {"Name": "Knuckle Curve", "Group": "Breaking"},
    "CS": {"Name": "Slow Curve", "Group": "Breaking"},
    "SV": {"Name": "Slurve", "Group": "Breaking"},
    "PO": {"Name": "Pitchout", "Group": "Other"},
    "FA": {"Name": "Fastball", "Group": "Fastball"},
    "EP": {"Name": "Eephus", "Group": "Breaking"},
    "KN": {"Name": "Knuckleball", "Group": "Breaking"},
    "SC": {"Name": "Screwball", "Group": "Offspeed"},
    "AB": {"Name": "Automatic Ball", "Group": "Automatic"},
    "AS": {"Name": "Automatic Strike", "Group": "Automatic"},
    "FO": {"Name": "Forkball", "Group": "Offspeed"},
}

Teams = {
    "ARI": {
        "name": "Arizona Diamondbacks",
        "abbreviation": "ARI",
        "location": "Phoenix",
        "teamname": "Diamondbacks",
        "division": "West",
        "league": "National",
        "twitter_user": "Dbacks",
        "hashtag": "Dbacks",
        "mlb_id": "109",
    },
    "ATL": {
        "name": "Atlanta Braves",
        "abbreviation": "ATL",
        "location": "Atlanta",
        "teamname": "Braves",
        "division": "East",
        "league": "National",
        "twitter_user": "Braves",
        "hashtag": "ForTheA",
        "mlb_id": "144",
    },
    "BAL": {
        "name": "Baltimore Orioles",
        "abbreviation": "BAL",
        "location": "Baltimore",
        "teamname": "Orioles",
        "division": "East",
        "league": "American",
        "twitter_user": "Orioles",
        "hashtag": "Birdland",
        "mlb_id": "110",
    },
    "BOS": {
        "name": "Boston Red Sox",
        "abbreviation": "BOS",
        "location": "Boston",
        "teamname": "Red Sox",
        "division": "East",
        "league": "American",
        "twitter_user": "RedSox",
        "hashtag": "DirtyWater",
        "mlb_id": "111",
    },
    "CHC": {
        "name": "Chicago Cubs",
        "abbreviation": "CHC",
        "location": "Chicago",
        "teamname": "Cubs",
        "division": "Central",
        "league": "National",
        "twitter_user": "Cubs",
        "hashtag": "ItsDifferentHere",
        "mlb_id": "112",
    },
    "CIN": {
        "name": "Cincinnati Reds",
        "abbreviation": "CIN",
        "location": "Cincinnati",
        "teamname": "Reds",
        "division": "Central",
        "league": "National",
        "twitter_user": "Reds",
        "hashtag": "ATOBTTR",
        "mlb_id": "113",
    },
    "CLE": {
        "name": "Cleveland Guardians",
        "abbreviation": "CLE",
        "location": "Cleveland",
        "teamname": "Guardians",
        "division": "Central",
        "league": "American",
        "twitter_user": "CleGuardians",
        "hashtag": "ForTheLand",
        "mlb_id": "114",
    },
    "COL": {
        "name": "Colorado Rockies",
        "abbreviation": "COL",
        "location": "Denver",
        "teamname": "Rockies",
        "division": "West",
        "league": "National",
        "twitter_user": "Rockies",
        "hashtag": "Rockies",
        "mlb_id": "115",
    },
    "CWS": {
        "name": "Chicago White Sox",
        "abbreviation": "CWS",
        "location": "Chicago",
        "teamname": "White Sox",
        "division": "Central",
        "league": "American",
        "twitter_user": "whitesox",
        "hashtag": "ChangeTheGame",
        "mlb_id": "145",
    },
    "DET": {
        "name": "Detroit Tigers",
        "abbreviation": "DET",
        "location": "Detroit",
        "teamname": "Tigers",
        "division": "Central",
        "league": "American",
        "twitter_user": "tigers",
        "hashtag": "DetroitRoots",
        "mlb_id": "116",
    },
    "HOU": {
        "name": "Houston Astros",
        "abbreviation": "HOU",
        "location": "Houston",
        "teamname": "Astros",
        "division": "West",
        "league": "American",
        "twitter_user": "astros",
        "hashtag": "LevelUp",
        "mlb_id": "117",
    },
    "KC": {
        "name": "Kansas City Royals",
        "abbreviation": "KC",
        "location": "Kansas City",
        "teamname": "Royals",
        "division": "Central",
        "league": "American",
        "twitter_user": "Royals",
        "hashtag": "TogetherRoyal",
        "mlb_id": "118",
    },
    "LAA": {
        "name": "Los Angeles Angels",
        "abbreviation": "LAA",
        "location": "Anaheim",
        "teamname": "Angels",
        "division": "West",
        "league": "American",
        "twitter_user": "Angels",
        "hashtag": "GoHalos",
        "mlb_id": "108",
    },
    "LAD": {
        "name": "Los Angeles Dodgers",
        "abbreviation": "LAD",
        "location": "Los Angeles",
        "teamname": "Dodgers",
        "division": "West",
        "league": "National",
        "twitter_user": "Dodgers",
        "hashtag": "AlwaysLA",
        "mlb_id": "119",
    },
    "MIA": {
        "name": "Miami Marlins",
        "abbreviation": "MIA",
        "location": "Miami",
        "teamname": "Marlins",
        "division": "East",
        "league": "National",
        "twitter_user": "Marlins",
        "hashtag": "MakeItMiami",
        "mlb_id": "146",
    },
    "MIL": {
        "name": "Milwaukee Brewers",
        "abbreviation": "MIL",
        "location": "Milwaukee",
        "teamname": "Brewers",
        "division": "Central",
        "league": "National",
        "twitter_user": "Brewers",
        "hashtag": "ThisIsMyCrew",
        "mlb_id": "158",
    },
    "MIN": {
        "name": "Minnesota Twins",
        "abbreviation": "MIN",
        "location": "Minneapolis",
        "teamname": "Twins",
        "division": "Central",
        "league": "American",
        "twitter_user": "Twins",
        "hashtag": "MNTwins",
        "mlb_id": "142",
    },
    "NYM": {
        "name": "New York Mets",
        "abbreviation": "NYM",
        "location": "Flushing",
        "teamname": "Mets",
        "division": "East",
        "league": "National",
        "twitter_user": "Mets",
        "hashtag": "LGM",
        "mlb_id": "121",
    },
    "NYY": {
        "name": "New York Yankees",
        "abbreviation": "NYY",
        "location": "Bronx",
        "teamname": "Yankees",
        "division": "East",
        "league": "American",
        "twitter_user": "Yankees",
        "hashtag": "RepBX",
        "mlb_id": "147",
    },
    "OAK": {
        "name": "Oakland Athletics",
        "abbreviation": "OAK",
        "location": "Oakland",
        "teamname": "Athletics",
        "division": "West",
        "league": "American",
        "twitter_user": "Athletics",
        "hashtag": "DrumTogether",
        "mlb_id": "133",
    },
    "PHI": {
        "name": "Philadelphia Phillies",
        "abbreviation": "PHI",
        "location": "Philadelphia",
        "teamname": "Phillies",
        "division": "East",
        "league": "National",
        "twitter_user": "Phillies",
        "hashtag": "RingTheBell",
        "mlb_id": "143",
    },
    "PIT": {
        "name": "Pittsburgh Pirates",
        "abbreviation": "PIT",
        "location": "Pittsburgh",
        "teamname": "Pirates",
        "division": "Central",
        "league": "National",
        "twitter_user": "Pirates",
        "hashtag": "LetsGoBucs",
        "mlb_id": "134",
    },
    "SD": {
        "name": "San Diego Padres",
        "abbreviation": "SD",
        "location": "San Diego",
        "teamname": "Padres",
        "division": "West",
        "league": "National",
        "twitter_user": "Padres",
        "hashtag": "TimeToShine",
        "mlb_id": "135",
    },
    "SEA": {
        "name": "Seattle Mariners",
        "abbreviation": "SEA",
        "location": "Seattle",
        "teamname": "Mariners",
        "division": "West",
        "league": "American",
        "twitter_user": "Mariners",
        "hashtag": "SeaUsRise",
        "mlb_id": "136",
    },
    "SF": {
        "name": "San Francisco Giants",
        "abbreviation": "SF",
        "location": "San Francisco",
        "teamname": "Giants",
        "division": "West",
        "league": "National",
        "twitter_user": "SFGiants",
        "hashtag": "SFGameUp",
        "mlb_id": "137",
    },
    "STL": {
        "name": "St. Louis Cardinals",
        "abbreviation": "STL",
        "location": "St. Louis",
        "teamname": "Cardinals",
        "division": "Central",
        "league": "National",
        "twitter_user": "Cardinals",
        "hashtag": "STLCards",
        "mlb_id": "138",
    },
    "TB": {
        "name": "Tampa Bay Rays",
        "abbreviation": "TB",
        "location": "St. Petersburg",
        "teamname": "Rays",
        "division": "East",
        "league": "American",
        "twitter_user": "RaysBaseball",
        "hashtag": "RaysUp",
        "mlb_id": "139",
    },
    "TEX": {
        "name": "Texas Rangers",
        "abbreviation": "TEX",
        "location": "Arlington",
        "teamname": "Rangers",
        "division": "West",
        "league": "American",
        "twitter_user": "Rangers",
        "hashtag": "StraightUpTX",
        "mlb_id": "140",
    },
    "TOR": {
        "name": "Toronto Blue Jays",
        "abbreviation": "TOR",
        "location": "Toronto",
        "teamname": "Blue Jays",
        "division": "East",
        "league": "American",
        "twitter_user": "BlueJays",
        "hashtag": "NextLevel",
        "mlb_id": "141",
    },
    "WSH": {
        "name": "Washington Nationals",
        "abbreviation": "WSH",
        "location": "Washington",
        "teamname": "Nationals",
        "division": "East",
        "league": "National",
        "twitter_user": "Nationals",
        "hashtag": "NATITUDE",
        "mlb_id": "120",
    },
}


_FILMROOM_CLIP = """https://fastball-gateway.mlb.com/graphql?query=query clipQuery($ids: [String], $languagePreference: LanguagePreference, $idType: MediaPlaybackIdType, $userId: String!, $withUser: Boolean!) {
  mediaPlayback(ids: $ids, languagePreference: $languagePreference, idType: $idType) {
    ...MediaPlaybackFields
    __typename
  }
  userInfo(userId: $userId) @include(if: $withUser) {
    firstName
    nickName
    userId
    __typename
  }
}

fragment MediaPlaybackFields on MediaPlayback {
  id
  slug
  title
  blurb
  description
  date
  canAddToReel
  feeds {
    type
    duration
    closedCaptions
    playbacks {
      name
      url
      segments
      __typename
    }
    image {
      altText
      templateUrl
      cuts {
        aspectRatio
        width
        height
        src
        __typename
      }
      __typename
    }
    __typename
  }
  keywordsDisplay {
    slug
    displayName
    __typename
  }
  translationId
  playInfo {
    balls
    strikes
    outs
    inning
    inningHalf
    pitchSpeed
    pitchType
    exitVelocity
    hitDistance
    launchAngle
    spinRate
    scoreDifferential
    gamePk
    runners {
      first
      second
      third
      __typename
    }
    teams {
      away {
        name
        shortName
        triCode
        __typename
      }
      home {
        name
        shortName
        triCode
        __typename
      }
      batting {
        name
        shortName
        triCode
        __typename
      }
      pitching {
        name
        shortName
        triCode
        __typename
      }
      __typename
    }
    players {
      pitcher {
        id
        name
        lastName
        playerHand
        __typename
      }
      batter {
        id
        name
        lastName
        playerHand
        __typename
      }
      __typename
    }
    __typename
  }
  __typename
}
&operationName=clipQuery&variables={"ids":"slug_id","languagePreference":"EN","idType":"SLUG","userId":"","withUser":false}"""

_FILMROOM_SEARCH = """https://fastball-gateway.mlb.com/graphql?query=query Search($query: String!, $page: Int, $limit: Int, $feedPreference: FeedPreference, $languagePreference: LanguagePreference, $contentPreference: ContentPreference, $queryType: QueryType = STRUCTURED) {
  search(query: $query, limit: $limit, page: $page, feedPreference: $feedPreference, languagePreference: $languagePreference, contentPreference: $contentPreference, queryType: $queryType) {
    plays {
      mediaPlayback {
        id
        slug
        blurb
        date
        description
        title
        canAddToReel
        feeds {
          type
          duration
          image {
            altText
            templateUrl
            cuts {
              width
              src
              __typename
            }
            __typename
          }
          playbacks {
            name
            segments
            __typename
          }
          __typename
        }
        playInfo {
          balls
          strikes
          outs
          inning
          inningHalf
          pitchSpeed
          pitchType
          exitVelocity
          hitDistance
          launchAngle
          spinRate
          scoreDifferential
          gamePk
          runners {
            first
            second
            third
            __typename
          }
          teams {
            away {
              name
              shortName
              triCode
              __typename
            }
            home {
              name
              shortName
              triCode
              __typename
            }
            batting {
              name
              shortName
              triCode
              __typename
            }
            pitching {
              name
              shortName
              triCode
              __typename
            }
            __typename
          }
          players {
            pitcher {
              id
              name
              lastName
              playerHand
              __typename
            }
            batter {
              id
              name
              lastName
              playerHand
              __typename
            }
            __typename
          }
          __typename
        }
        keywordsDisplay {
          slug
          displayName
          __typename
        }
        __typename
      }
      __typename
    }
    total
    __typename
  }
}
&operationName=Search&variables={"queryType":null,"query":"","limit":125,"page":0,"languagePreference":"EN","contentPreference":"CMS_FIRST"}"""

_FILMROOM_QUERIES = {"Clip": _FILMROOM_CLIP, "Search": _FILMROOM_SEARCH}
