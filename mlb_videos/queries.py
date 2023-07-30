_VIDEO_ROOM_CLIP = """https://fastball-gateway.mlb.com/graphql?query=query clipQuery($ids: [String], $languagePreference: LanguagePreference, $idType: MediaPlaybackIdType, $userId: String!, $withUser: Boolean!) {
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

_VIDEO_ROOM_SEARCH = """https://fastball-gateway.mlb.com/graphql?query=query Search($query: String!, $page: Int, $limit: Int, $feedPreference: FeedPreference, $languagePreference: LanguagePreference, $contentPreference: ContentPreference, $queryType: QueryType = STRUCTURED) {
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

_VIDEO_ROOM_QUERIES = {"Clip": _VIDEO_ROOM_CLIP, "Search": _VIDEO_ROOM_SEARCH}
