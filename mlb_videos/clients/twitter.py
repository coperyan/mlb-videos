import os
import json
import time
import requests
import logging
import logging.config
from requests_oauthlib import OAuth1

MEDIA_URL = 'https://upload.twitter.com/1.1/media/upload.json'
TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'

MEDIA_TYPE = 'video/mp4'
MEDIA_CATEGORY = 'tweet_video'

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

class Auth:
    def __init__(self):
        """Initialization generates auth element of class
        """
        self._generate_auth()
    
    def _generate_auth(self):
        """Create oauth1
        """
        with open('../creds/twitter.json') as f:
            creds = json.load(f)

        self.oauth = OAuth1(
            creds['api_key'],
            client_secret = creds['api_key_secret'],
            resource_owner_key = creds['access_token'],
            resource_owner_secret = creds['access_token_secret']
        )

class Media:
    def __init__(self, fp:str = None):
        """Fp is local filepath for media
        Initialization will start upload
        """
        self.file_path = fp
        self.file_name = os.path.basename(fp)
        self.file_bytes = os.path.getsize(fp)
        self.media_id = None
        self.processing_info = None
        self.oauth = Auth()

    def _initialize_upload(self):
        """
        """
        r_data = {
            'command': 'INIT',
            'media_type': MEDIA_TYPE,
            'total_bytes': self.file_bytes,
            'media_category': MEDIA_CATEGORY
        }
        req = requests.post(MEDIA_URL,data = r_data, auth = self.oauth)
        self.media_id = req.json()['media_id']
        logging.info(f'Initialized media upload of {self.file_name}')

    def _iteration_upload(self):
        """Iterative upload of media to twitter
        """
        segment_id = 0
        bytes_sent = 0
        file = open(self.file_path, 'rb')

        while bytes_sent < self.file_bytes:
            chunk = file.read(4*1024*1024)

            r_data = {
                'command': 'APPEND',
                'media_id': self.media_id,
                'segment_index': segment_id
            }
            files = {
                'media': chunk
            }
            req = requests.post(MEDIA_URL, data = r_data, files = files, auth = self.oauth)

            if req.status_code < 200 or req.status_code > 299:
                logging.critical(f'Media Upload Status Code: {req.status_code} - Message: {req.text}')
                raise ValueError('Bad Status Code')

            segment_id += 1
            bytes_sent = file.tell()
            logging.info(f'Segment: {segment_id} - {bytes_sent} of {self.file_bytes} uploaded..')

        logging.info(f'Upload chunks complete..')


    def _finalize_upload(self):
        """Finalize Upload Command
        Check status will be called at end
        """
        r_data = {
            'command': 'FINALIZE',
            'media_id': self.media_id
        }
        req = requests.post(MEDIA_URL, data = r_data, auth = self.oauth)
        self.processing_info = req.json().get('processing_info',None)
        self._check_status()

    def _check_status(self):
        """Recursive function that continually checks status
        of Upload..
        """
        if self.processing_info is None:
            return

        state = self.processing_info['state']
        logging.info(f'Media processing state: {state}')

        if state == u'succeeded':
            return
        
        if state == u'failed':
            logging.critical('Upload Failed..')
            raise Exception('Media Upload Failed..')

        check_after_secs = self.processing_info['check_after_secs']
        logging.info(f'Checking after {check_after_secs} seconds..')
        time.sleep(check_after_secs)

        r_params = {
            'command': 'STATUS',
            'media_id': self.media_id
        }
        req = requests.get(MEDIA_URL, params = r_params, auth = self.oauth)
        self.processing_info = req.json().get('processing_info',None)
        self._check_status()

    def upload(self):
        """
        """
        self._initialize_upload()
        self._iteration_upload()
        self._finalize_upload()
        logging.info(f'Successfully uploaded media: {self.media_id}')
        return self.media_id


class Tweet:
    def __init__(self, status:str = None, media:str = None):
        """Sets status/media params
        Runs validation
        Adds oauth
        """
        self.status = status
        self.media = media
        self._validate()
        self.oauth = Auth()

    def _validate(self):
        """Validates arguments
        """
        if self.status is None and self.media is None:
            logging.warning(f'Need a tweet status or media to post tweet..')
            raise ValueError()

        if self.media is not None and not os.path.isfile(self.media):
            logging.warning(f'Bad file path passed..')
            raise ValueError(self.media)
            
    def _upload_media(self):
        """Initializes media upload 
        Sets media id if valid
        """
        md = Media(self.media)
        self.media_id = md.upload()

    def post_tweet(self):
        """Posts tweet
        """
        r_data = {
            'status': self.status
        }

        if self.media is not None:
            self._upload_media()
            r_data['media_ids'] = self.media_id

        req = requests.post(TWEET_URL, data = r_data, auth = self.oauth)
        logging.info(f'Successfully uploaded tweet!')

    

    

    

