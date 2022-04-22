import os
import json
import requests
from bs4 import BeautifulSoup

with open('config.json') as f:
    CONFIG = json.load(f)

class Player:
    def __init__(self, id):
        """Initialize player class based on playerID (MLB)
        """
        self.id = id
        self.metadata = {}

    def get_metadata(self):
        """
        """
        r = requests.get(CONFIG['players']['api_url'].format(id = self.id))
        self.metadata = r.json()['people'][0]

    def get_social_media(self):
        """
        """
        ns = self.metadata['nameSlug']
        r = requests.get(CONFIG['players']['site_url'].format(ns = ns))
        soup = BeautifulSoup(r.text)

        try:
            self.twitter = soup.find(
                'li',{'class':'twitter'}
            ).find(
                'a'
            )['href'].replace(
                'https://twitter.com/@',''
            )
        except Exception as e:
            print(f'No valid Twitter Username found for {ns}..')

        try:
            self.instagram = soup.find(
                'li', {'class':'instagram'}
            ).find(
                'a'
            )['href'].replace(
                'https://instagram.com/',''
            )
        except Exception as e:
            print(f'No valid Instagram Username found for {ns}..')

    