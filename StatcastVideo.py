import os
import json
import time
import requests
from math import ceil, floor

with open('config.json') as f:
    CONFIG = json.load(f)

with open(CONFIG['videos']['query_path']) as f:
    QUERY_URL = f.read()

with open(CONFIG['videos']['clip_path']) as f:
    CLIP_URL = f.read()

CHUNK_SIZE = CONFIG['videos']['chunk_size']

##Video Client Class
class VideoClient:
    """Used to make requests to URLs
    Reply with content & download things
    """
    def __init__(self, url = None, req_type = None):
        self._url = url
        self._req_type = req_type
        self._resp = None
        self._resp_code = None
        self._resp_json = None
        self.save_path = ''
        self.set_headers()
        self.make_request()
        
    def set_headers(self):
        """Sets headers based on the request type
        """
        try:
            self._headers = CONFIG['videos']['headers'][f'{self._req_type}']
        except Exception as e:
            raise Exception(f'Invalid request type found when assigning headers: {e}')

    def make_request(self):
        """Perform requests.get, checks for OK response code
        """
        self._resp = requests.get(url = self._url, headers = self._headers)
        self._resp_code = self._resp.status_code
        if self._resp_code != 200:
            raise Exception(f'Bad request, status code: {self._resp_code}, response text: {self._resp.text}')

    def get_json(self):
        """Returns JSON of response, trims based on config (if applicable)
        """
        resp_json = self._resp.json()
        try:
            for key in CONFIG['videos']['responses'][self._req_type]['keys']:
                resp_json = resp_json.get(key,{})
        except:
            print('Issue parsing JSON, returning full..')
        
        self._resp_json = resp_json
        return self._resp_json       

    def download_video(self,play,feed):
        """Downloads video from request content stream
        """
        self.save_path = os.path.join(
            CONFIG['videos']['local_save_dir'],
            f'{play["date"]}_{play["slug"]}_{feed["feed_id"]}.mp4')
        with open(self.save_path,'wb') as f:
            for chunk in self._resp.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

##Video Search Class
class VideoSearch:
    """
    """
    def __init__(self,feed='opt',dl=False,**kwargs):
        """
        """
        self.feed = feed
        self.kwargs = kwargs
        self.kwargs_list = list(kwargs.keys())
        self.request_url = ''
        self.query_json = {}
        self.play_list = []
        self.clip_list = []
        self.file_list = []
        self.build_query()
        self.request_query()
        self.process_query_clips()
        if dl:
            self.download_all_clips()

    def build_query(self):
        """Builds query string with parameters passed in initialization of class
        """
        query_str = ''

        for kwarg in self.kwargs_list:

            ## Loading search parameters & assigning some formatting variables
            sparam = next(filter(lambda x: x['param_name'] == kwarg, CONFIG['videos']['params']))
            eq_sep = '=' * sparam['equalsct']
            sp_pad = r'\"' if sparam['type'] == 'str' else ''

            ##Special formatting for date range kwarg
            if kwarg == 'date_range':
                sparam_str = f'{sparam["param_url"]} ' + \
                    f'{eq_sep} ' + \
                    f'{{{{ {sp_pad}{self.kwargs[kwarg][0]}{sp_pad}, ' + \
                    f'{sp_pad}{self.kwargs[kwarg][1]}{sp_pad} }}}}'
            ##add pitch speed?
            else:
                sparam_str = f'{sparam["param_url"]} ' + \
                    f'{eq_sep} ' + \
                    f'[{sp_pad}{self.kwargs[kwarg]}{sp_pad}]'

            if query_str == '':
                query_str = sparam_str
            else:
                query_str = f'{query_str} AND {sparam_str}'

        query_str = f'{query_str} {CONFIG["videos"]["query_suffix"]}'
        self.request_url = QUERY_URL.replace('"query":""', f'"query":"{query_str}"')

    def request_query(self):
        """Creates instance of the Client class, adds query URL to get plays
        """
        query_client = VideoClient(url = self.request_url, req_type = 'query')
        self.query_json = query_client.get_json()
        self.clip_ct = len(self.query_json)

    def process_query_clips(self):
        """Parses the query response to get all returned plays
        Iterates over each play and processes the "clip"
        """
        clip_ctr = 0
        for play in self.query_json:
            clip_ctr += 1
            play_id = play['mediaPlayback'][0]['slug']
            print(f'Processing clip {play_id} - ({clip_ctr}/{self.clip_ct}) {round((clip_ctr/self.clip_ct)*100,2)}%')
            self.play_list.append(play_id)
            self.process_clip(play_id)

    def process_clip(self,play_id):
        """Creates a URL & instance of client to gather feed information & metadata for any given play
        """
        clip_url = CLIP_URL.replace('slug_id',play_id)
        clip_client = VideoClient(url = clip_url, req_type = 'clip')
        clip_json = clip_client.get_json()
        clip_json = clip_json[0]

        #Get ALL the info
        clip_dict = {
            'id': clip_json['id'], 'slug': clip_json['slug'], 'title': clip_json['title'],
            'short_desc': clip_json['blurb'], 'long_desc': clip_json['description'],
            'date': clip_json['date'], 'game_id': clip_json['playInfo']['gamePk'],
            'inning': clip_json['playInfo']['inning'], 'outs': clip_json['playInfo']['outs'],
            'balls': clip_json['playInfo']['balls'], 'strikes': clip_json['playInfo']['strikes'],
            'pitch_speed': clip_json['playInfo']['pitchSpeed'], 'exit_velo': clip_json['playInfo']['exitVelocity'],
            'pitcher_id': clip_json['playInfo']['players']['pitcher']['id'], 'pitcher_name': clip_json['playInfo']['players']['pitcher']['name'],
            'batter_id': clip_json['playInfo']['players']['batter']['id'], 'batter_name': clip_json['playInfo']['players']['batter']['name'], 
            'home_team': clip_json['playInfo']['teams']['home']['triCode'], 'away_team': clip_json['playInfo']['teams']['away']['triCode'],
            'batting_team': clip_json['playInfo']['teams']['batting']['triCode'], 'pitching_team': clip_json['playInfo']['teams']['pitching']['triCode'],
            'feeds': [], 'feed_choice': ''
        }

        #Get feeds
        for clip_feed in clip_json['feeds']:
            for playback in clip_feed['playbacks']:
                if os.path.splitext(os.path.basename(playback['url']))[1] == '.mp4':
                    clip_dict['feeds'].append(
                        {
                            'feed_id': f'{clip_feed["type"]}_{playback["name"]}',
                            'feed_type': clip_feed['type'],
                            'feed_name': playback['name'],
                            'feed_url': playback['url']
                        }
                    )

        #Pick feed we want
        feed_choices = [
            {d['feed_id']: d for d in clip_dict['feeds']}[i] \
            for i in CONFIG['videos']['feed_types'][self.feed] \
            if i in {d['feed_id']: d for d in clip_dict['feeds']}
        ]

        if len(feed_choices) > 0:
            feed_choice = feed_choices[0]
            clip_dict['feed_choice'] = feed_choice
            ##self.download_clip(clip_dict)
        else:
            print('No feeds found')

        self.clip_list.append(clip_dict)

    def download_all_clips(self):
        """
        """
        for clip in self.clip_list:
            try:
                self.download_clip(clip)
            except Exception as e:
                print(e)
                continue

    def download_clip(self,clip_dict):
        """Creates instance of client to grab the .mp4 feed URL, add to local save in chunks
        """
        dl_client = VideoClient(url = clip_dict['feed_choice']['feed_url'], req_type = 'download')
        dl_client.download_video(play = clip_dict, feed = clip_dict['feed_choice'])
        self.file_list.append(dl_client.save_path)
    
    def get_downloaded_files(self):
        """
        """
        return self.file_list


class StatcastVideos:
    def __init__(self, feed = 'best', dl = False, statcast_df = None):
        self.feed = feed
        self.dl = dl
        self.statcast_df = statcast_df
        self.statcast_len = len(statcast_df)
        self.video_searches = []
        self.downloaded_files = []
        self.perform_all_searches()

    def perform_search(self,pitch):
        """Performs video search based on attributes of pitch in statcast data
        Might need to add some improvements here.. Pitch results are helpful, but differ
        Pitch speed & spin rate would both be huge values that don't vary much and are exact on both ends
        """
        srch = VideoSearch(
            feed = self.feed,
            dl = self.dl,
            batter_id = pitch.batter,
            pitcher_id = pitch.pitcher,
            date = pitch.game_date.strftime('%Y-%m-%d'),
            pitch_type = pitch.pitch_type,
            inning = pitch.inning,
            balls = pitch.balls,
            strikes = pitch.strikes,
            #pitch_result = pitch.description,
            #pitch_speed = (floor(pitch.release_speed), ceil(pitch.release_speed)),
            #pitch_zone = pitch.zone,
        )
        dl_files = srch.get_downloaded_files()
        dl_files = [os.path.basename(x) for x in dl_files]
        if len(dl_files) > 1:
            print('More than 2 clips found..')
        elif len(dl_files) == 1:
            return dl_files[0]
        else:
            return ''

    def perform_all_searches(self):
        """
        """
        self.statcast_df['save_path'] = ''
        for index, row in self.statcast_df.iterrows():
            dl_path = self.perform_search(row)
            self.statcast_df.at[index,'save_path'] = dl_path
            time.sleep(1)

    def get_df(self):
        """
        """
        return self.statcast_df
