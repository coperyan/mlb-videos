import os
import json
import time
import requests
from requests_oauthlib import OAuth1

with open('config.json') as f:
    CONFIG = json.load(f)
    
with open('creds/twitter.json') as f:
    CREDS = json.load(f)

MEDIA_ENDPOINT_URL = CONFIG['twitter']['media_endpoint_url']
POST_TWEET_URL = CONFIG['twitter']['post_tweet_url']

class VideoTweet:
    def __init__(self, fp, t):
        """Initialize class with filepath & tweet text
        Will start the upload
        """
        self.file_path = fp
        self.tweet_text = t
        self.file_name = os.path.basename(self.file_path)
        self.file_bytes = os.path.getsize(self.file_path)
        self.media_id = None
        self.processing_info = None
        self.gen_oauth()
        self.initialize_upload()
        self.upload_iter()
        self.upload_finalize()
        self.post_tweet()

    def gen_oauth(self):
        """Create OAUTH for reference later
        """
        self.oauth = OAuth1(
            CREDS['api_key'],
            client_secret = CREDS['api_key_secret'],
            resource_owner_key = CREDS['access_token'],
            resource_owner_secret = CREDS['access_token_secret']
        )

    def initialize_upload(self):
        """
        """
        req_data = {
            'command': 'INIT',
            'media_type': 'video/mp4',
            'total_bytes': self.file_bytes,
            'media_category': 'tweet_video'
        }
        req = requests.post(
            url = MEDIA_ENDPOINT_URL,
            data = req_data,
            auth = self.oauth
        )
        self.media_id = req.json()['media_id']

        print(f'Initialized media upload..')

    def upload_iter(self):
        """
        """
        segment_id = 0
        bytes_sent = 0
        file = open(self.file_path, 'rb')

        while bytes_sent < self.file_bytes:
            chunk = file.read(4*1024*1024)

            req_data = {
                'command': 'APPEND',
                'media_id': self.media_id,
                'segment_index': segment_id
            }

            files = {
                'media': chunk
            }

            req = requests.post(
                url = MEDIA_ENDPOINT_URL,
                data = req_data,
                files = files,
                auth = self.oauth
            )

            if req.status_code < 200 or req.status_code > 299:
                print(f'Media Upload Status Code: {req.status_code} - Message: {req.text}')
                return
            
            segment_id += 1
            bytes_sent = file.tell()

            print(f'{bytes_sent} of {self.file_bytes} uploaded..')
        
        print(f'Upload chunks complete..')

    def upload_finalize(self):
        """
        """
        req_data = {
            'command': 'FINALIZE',
            'media_id': self.media_id
        }
        req = requests.post(
            url = MEDIA_ENDPOINT_URL,
            data = req_data,
            auth = self.oauth
        )
        self.processing_info = req.json().get('processing_info',None)
        self.check_status()

    def check_status(self):
        """
        """
        if self.processing_info is None:
            return

        state = self.processing_info['state']
        print(f'Media processing status: {state}')

        if state == u'succeeded':
            return
        
        if state == u'failed':
            print('FAILED')
            return

        check_after_secs = self.processing_info['check_after_secs']
        print(f'Checking after {check_after_secs} secs..')
        time.sleep(check_after_secs)

        req_params = {
            'command': 'STATUS',
            'media_id': self.media_id
        }
        req = requests.get(
            url = MEDIA_ENDPOINT_URL,
            params = req_params,
            auth = self.oauth
        )
        
        self.processing_info = req.json().get('processing_info',None)
        self.check_status()

    def post_tweet(self):
        """
        """
        req_data = {
            'status': self.tweet_text,
            'media_ids': self.media_id
        }
        req = requests.post(
            url = POST_TWEET_URL,
            data = req_data,
            auth = self.oauth
        )





# test_video = 'downloads/test.mp4'
# tweet_text = (
#     f'Umpire John Libka was responsible for the largest miss yesterday. This pitch to ' +
#     (f'Jason Heyward') + f' missed by ' +
#     f'5.76 inches.\n\n ' +
#     f'#ItsDifferentHere #RaysUp #CHCvsTB #TBvsCHC'
# )

# test = VideoTweet(
#     fp = test_video,
#     t = tweet_text
# )
