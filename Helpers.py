import io
import os
import re
import json
import shutil
import requests
import pandas as pd
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta

with open('config.json') as f:
    CONFIG = json.load(f)

TEAMS = pd.read_csv('data/teams.csv')
PLAYERS = CONFIG['helpers']['players_url']
LOCAL_PLAYERS = CONFIG['helpers']['players_path']
PLAYER_COLS = CONFIG['helpers']['player_cols']
STATCAST_VALID_DATES = {
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
    2021: (date(2021, 4, 14), date(2021, 11, 2))
}
DATE_FORMAT = CONFIG['helpers']['date_format']
DATE_FORMATS = [
    (re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$'), '%Y-%m-%d'),
    (re.compile(r'^\d{4}-\d{1,2}-\d{1,2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z$'), '%Y-%m-%dT%H:%M:%S.%fZ'),
]

def get_player_name(id):
    """
    """
    req = requests.get(CONFIG['players']['api_url'].format(id = id))
    name = req.json()['players'][0]['fullName']
    return name

def get_player_twitter(id):
    """
    """
    api_req = requests.get(CONFIG['players']['api_url'].format(id = id))
    ns = api_req.json()['players'][0]['nameSlug']
    site_req = requests.url(CONFIG['players']['site_url'].format(ns = ns))
    soup = BeautifulSoup(site_req.text)
    try:
        twitter = soup.find('li',{'class':'twitter'}).find('a')['href'].replace('https://twitter.com/@','')
        return twitter
    except:
        print(f'No valid twitter found for {ns}..')
        return None

def get_team_attribute(t,a):
    """
    """
    d = TEAMS[TEAMS['Abbreviation'] == t.upper()].iloc[0].to_dict()
    return d[a]

def get_season_dates(year):
    """
    """
    return STATCAST_VALID_DATES.get(year)

def get_range_seasons(start_date,end_date):
    """
    """
    start_date = datetime.strptime(start_date,DATE_FORMAT).date()
    end_date = datetime.strptime(end_date,DATE_FORMAT).date()
    years = [x for x in range(start_date.year, end_date.year+1)]
    return years

def get_players():
    """Get Players from Chadwick Register
    """
    r = requests.get(PLAYERS).content
    df = pd.read_csv(io.StringIO(r.decode('utf-8')), usecols=PLAYER_COLS)
    df.dropna(how='all',subset=['key_mlbam'],inplace=True)
    df['PLAYERNAME'] = df.apply(lambda x: f'{x.name_first} {x.name_last}', axis=1)
    df['key_mlbam'] = df['key_mlbam'].astype(int)
    df.to_csv(LOCAL_PLAYERS,index=False)

def player_lookup(player_name=None,active='Y'):
    """Get Player's PlayerID based on name
    """
    if player_name:
        df = pd.read_csv(LOCAL_PLAYERS)
        df['match_rank'] = df.apply(lambda x: fuzz.ratio(x.PLAYERNAME,player_name),axis=1)
        df = df.sort_values(by='match_rank',ascending=False)
        return df.iloc[0]['key_mlbam']
    else:
        raise ValueError('Must pass valid player name to function.')

def get_date_range(start_date,end_date):
    """
    """
    start_date = datetime.strptime(start_date,DATE_FORMAT).date()
    end_date = datetime.strptime(end_date,DATE_FORMAT).date()
    dates = []
    start = start_date
    
    while start <= end_date:
        date_span = start.replace(month=3, day=15), start.replace(month=11,day=15)
        season_start, season_end = STATCAST_VALID_DATES.get(start.year,date_span)
        
        if start < season_start:
            start = season_start
        elif start > season_end:
            start, _ = STATCAST_VALID_DATES.get(start.year + 1, (date(month=3,day=15,year=start.year + 1), None))

        if start > end_date:
            break
        
        end = min(start + timedelta(0), end_date)
        dates.append((start,end))
        start += timedelta(days=1)

    return dates

def parse_statcast_df(df):
    data_copy = df.copy()

    string_columns = [
        dtype_tuple[0] for dtype_tuple in data_copy.dtypes.items() if str(dtype_tuple[1]) in ["object","string"]
    ]

    for column in string_columns:
        # Only check the first value of the column and test that;
        # this is faster than blindly trying to convert entire columns
        first_value_index = data_copy[column].first_valid_index()
        if first_value_index is None:
            # All nulls
            continue
        first_value = data_copy[column].loc[first_value_index]

        if str(first_value).endswith('%') or column.endswith('%'):
            data_copy[column] = data_copy[column].astype(str).str.replace("%", "").astype(float) / 100.0
        else:
            # Doing it this way as just applying pd.to_datetime on
            # the whole dataframe just tries to gobble up ints/floats as timestamps
            for date_regex, date_format in DATE_FORMATS:
                if isinstance(first_value, str) and date_regex.match(first_value):
                    data_copy[column] = data_copy[column].apply(pd.to_datetime, errors='ignore', format=date_format)
                    data_copy[column] = data_copy[column].convert_dtypes(convert_string=False)
                    break

    return data_copy

def create_project_folder(dir):
    """
    """
    os.mkdir(dir)

def copy_videos(old_dir,new_dir):
    """
    """
    file_list = sorted([os.path.join(old_dir,x) for x in os.listdir(old_dir)], key=os.path.getmtime)
    for file in file_list:
        new_path = os.path.join(new_dir,os.path.basename(file))
        shutil.copy(file,new_path)

def delete_files(dir):
    """
    """
    for file in os.listdir(dir):
        os.remove(os.path.join(dir,file))