import os
import io
import csv
import json
import requests


url = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&type=details&game_date_gt=2024-04-03&game_date_lt=2024-04-03"
resp = requests.get(url, timeout=None)

json_resp = list(csv.DictReader(io.StringIO(resp.content.decode("utf-8-sig"))))
