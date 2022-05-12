import os
import sys
import time
import random
import httplib2
import logging
import logging.config

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

#Explicitly tell underlying HTTP transport library not to retry
#Handling retry logic ourselves
httplib2.RETRIES = 1

#Max number of times to retry before giving up
MAX_RETRIES = 10

#Always retry when these types of exceptions are raised
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

#Always retry when an apiclient.errors.HttpError with 
#one of these codes is raised..
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
CLIENT_SECRETS_FILE = '../creds/client_secret.json'

#Oauth Acccess scope
YOUTUBE_UPLOAD_SCOPE = 'https://www.googleapis.com/auth/youtube.upload'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

#Valid privacy statuses
VALID_PRIVACY_STATUSES = ("public","private","unlisted")

#Defaults
DEFAULT_PRIVACY = 'unlisted'
DEFAULT_LANGUAGE = 'en_US'

class Service:
    def __init__(self, args):
        """
        """
        self.args = args
        return self.get_service()

    def get_service(self):
        """
        """
        flow = flow_from_clientsecrets(
            CLIENT_SECRETS_FILE,
            scope = YOUTUBE_UPLOAD_SCOPE,
            message = None
        )
        storage = Storage(f'{sys.argv[0]}-oauth2.json')
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, self.args)

        return build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            http = credentials.authorize(httplib2.Http())
        )

class Video:
    def __init__(self, fp:str = None, title:str = None,
                desc:str = None, tags:list = None,
                privacy = DEFAULT_PRIVACY):
        self.file = fp
        self.title = title
        self.desc = desc
        self.tags = ','.join(tags)
        self.privacy = privacy
        self.service = Service(argparser.parse_args())

    def video_upload(self):
        """Called by main upload function
        """
        body = dict(
            snippet = dict(
                title = self.title,
                description = self.desc,
                tags = None,#self.tags,
                defaultLanguage = 'en_US'
            ),
            status = dict(
                privacyStatus=self.privacy
            )
        )

        insert_req = self.service.videos().insert(
            part = ','.join(body.keys()),
            body = body,
            media_body = MediaFileUpload(
                self.file,
                chunksize = -1,
                resumable = True
            )
        )

        resp = self.resumable_upload(insert_req)
        return resp        
    
    def resumable_upload(self, req):
        """Called by video upload function
        Uploads in chunks
        Max retry functionality
        """
        response = None
        error = None
        retry = 0

        while response is None:
            try:
                status, response = req.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print(f'YT Video {response["id"]} successfully uploaded..')
                    else:
                        print('No valid response.. Failed')
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = f'A retriable HTTP error {e.resp.status} occured: \n{e.content}'
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = f'A retriable error occured {e}'

            if error is not None:
                logging.warning(f'Error uploading video: {error}')
                retry += 1
                if retry > MAX_RETRIES:
                    logging.critical('Reached max retries..')

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                logging.info(f'Sleeping {sleep_seconds} and then retrying..')
                time.sleep(sleep_seconds)

    def upload(self):
        """Calls video upload function
        Checks for Http Errors
        """
        try:
            self.video_upload()
        except HttpError as e:
            logging.critical(f'Http Error with Upload: {e.resp.status} \n {e.content}')
