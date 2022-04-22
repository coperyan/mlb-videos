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

API_KEY = CREDS['api_key']
API_KEY_SECRET = CREDS['api_key_secret']
ACCESS_TOKEN = CREDS['access_token']
ACCESS_TOKEN_SECRET = CREDS['access_token_secret']

test_video = 'downloads/test.mp4'
tweet_text = (
    f'Umpire John Libka was responsible for the largest miss yesterday. This pitch to ' +
    (f'Jason Heyward') + f' missed by ' +
    f'5.76 inches.\n\n ' +
    f'#ItsDifferentHere #RaysUp #CHCvsTB #TBvsCHC'
)

oauth = OAuth1(
    API_KEY,
    client_secret = API_KEY_SECRET,
    resource_owner_key = ACCESS_TOKEN,
    resource_owner_secret = ACCESS_TOKEN_SECRET
)

file_name = os.path.basename(test_video)
total_bytes = os.path.getsize(test_video)
media_id = None
processing_info = None

request_data = {
    'command': 'INIT',
    'media_type': 'video/mp4',
    'total_bytes': total_bytes,
    'media_category': 'tweet_video'
}
req = requests.post(url = MEDIA_ENDPOINT_URL, data = request_data, auth = oauth)
media_id = req.json()['media_id']

segment_id = 0
bytes_sent = 0
file = open(test_video, 'rb')

while bytes_sent < total_bytes:
    chunk = file.read(4*1024*1024)

    request_data = {
        'command': 'APPEND',
        'media_id': media_id,
        'segment_index': segment_id
    }

    files = {
        'media': chunk
    }

    req = requests.post(url = MEDIA_ENDPOINT_URL, data = request_data, files = files, auth = oauth)

    if req.status_code < 200 or req.status_code > 299:
        print(req.status_code)
        print(req.text)
        break

    segment_id += 1
    bytes_sent = file.tell()

request_data = {
    'command': 'FINALIZE',
    'media_id': media_id
}

req = requests.post(url = MEDIA_ENDPOINT_URL, data = request_data, auth = oauth)
processing_info = req.json().get('processing_info',None)

states = ['succeeded','failed']
state = processing_info['state']
check_after_secs = processing_info['check_after_secs']

while state not in states:
    request_params = {
        'command': 'STATUS',
        'media_id': media_id
    }
    req = requests.get(url = MEDIA_ENDPOINT_URL, params = request_params, auth = oauth)
    processing_info = req.json().get('processing_info',None)
    state = processing_info['state']
    check_after_secs = processing_info['check_after_secs']
    time.sleep(check_after_secs)

request_data = {
    'status': tweet_text,
    'media_ids': media_id
}

req = requests.post(url = POST_TWEET_URL, data = request_data, auth = oauth)
print(req.json())

