import os
import sys
import time
import random
import httplib2

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


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
CLIENT_SECRETS_FILE = 'creds/client_secret.json'

#Oauth Acccess scope
YOUTUBE_UPLOAD_SCOPE = 'https://www.googleapis.com/auth/youtube.upload'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

#Valid privacy statuses
VALID_PRIVACY_STATUSES = ("public","private","unlisted")

def get_authenticated_service(args):
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
        credentials = run_flow(flow, storage, args)
    
    return build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http())
    )

def initialize_upload(youtube, options):
    """
    """
    tags = None
    body = dict(
        snippet = dict(
            title = options['title'],
            description = options['description'],
            tags = tags,
        ),
        status = dict(
            privacyStatus = options['privacyStatus']
        )
    )

    insert_request = youtube.videos().insert(
        part = ','.join(body.keys()),
        body = body,
        media_body = MediaFileUpload(
            options['file'],
            chunksize = -1,
            resumable = True
        )
    )

    resumable_upload(insert_request)

def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0

    while response is None:
        try:
            print('Uploading file...')
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print(f'Video id {response["id"]} was successfully uploaded..')
                else:
                    exit(f'The upload failed with an unexpected response {response}')
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f'A retriable HTTP error {e.resp.status} occured: \n{e.content}'
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f'A retriable error occured {e}'

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry..")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print(f'Sleeping {sleep_seconds} and then retrying..')
            time.sleep(sleep_seconds)


def upload_video(video_data):
    """
    """
    args = argparser.parse_args()
    if not os.path.exists(video_data['file']):
        exit(f'Please specify a valid file using the --file parameter..')

    youtube = get_authenticated_service(args)
    try:
        initialize_upload(youtube, video_data)
    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occured: \n{e.content}')


test_video = {
    'file': 'downloads/final.mp4',
    'title': 'Worst Calls - 4/19/2022 (MLB Umpires)',
    'description': 'Test Upload using YouTube Python API v3',
    'keywords': 'mlb,python,badcalls,api',
    'privacyStatus': 'unlisted'
}

upload_video(test_video)