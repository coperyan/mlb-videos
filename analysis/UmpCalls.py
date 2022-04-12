import os
import json
import pandas as pd
import scipy.stats as stats
from tqdm import tqdm

tqdm.pandas()

with open('config.json') as f:
    CONFIG = json.load(f)

AVG_ERROR = CONFIG['ump_calls']['avg_error']
SAMPLE = CONFIG['ump_calls']['sample']
BALL_RADIUS = CONFIG['ump_calls']['ball_radius']
PROB_REQ = CONFIG['ump_calls']['prob_req']
ZONE_RADIUS = CONFIG['ump_calls']['zone_radius']
CALLS = CONFIG['ump_calls']['calls']
RETURN_COLS = CONFIG['ump_calls']['return_cols']


def get_sample():
    """Generates a sample distribution of 10k to represent the error within data
    Average inaccuracy of statcast pitch monitoring is 0.25"
    """
    lower, upper = -AVG_ERROR, AVG_ERROR
    mu, sigma = AVG_ERROR,AVG_ERROR
    x = stats.truncnorm(
        (lower-mu) / sigma, (upper-mu) / sigma, loc=mu, scale = sigma
    )
    n = stats.norm(loc=mu, scale=sigma)
    return x.rvs(10000)
    #return truncnorm(a=-AVG_ERROR,b=AVG_ERROR,scale=3).rvs(size=SAMPLE)

def get_combined():
    """This returns a list with two tuples per element from above func
    One represents a vertical inaccuracy, one represents horizontal
    """
    return tuple(zip(get_sample(),get_sample()))

def classify_pitch(pd,pb,pt,px,py):
    """Algorithm creates bottom left, upper right bounds of rectangle (zone)
    Compares adjusted px / pz values to see if the call was in or out of the zone
    Returns a boolean value, essentially validating the call
    """
    x1, y1, w = -ZONE_RADIUS,  pb - BALL_RADIUS, ZONE_RADIUS * 2
    x2, y2 = x1 + w, pt + BALL_RADIUS
    x, y = px, py

    ##if in the strike zone and called strike, return True
    if (x1 < x and x < x2) and (y1 < y and y < y2):
        return True if pd == 'called_strike' else False 

    ##if not in the strike zone and called ball, return True
    else:
        return True if pd == 'ball' else False 

def determine_miss(p):
    """This function will determine horizontal & vertical misses
    Will return five columns
    horizontal_miss_type (Inside / Outside)
    horizontal_miss (float)
    vertical_miss_type (High / Low)
    vertical_miss (float)
    total_miss (float)
    """

    if any(v == 0 for v in (p.plate_x, p.plate_z, p.sz_bot, p.sz_top)):
        return '', 0.00, '', 0.00,'', 0.00

    if p.description not in CALLS:
        return '', 0.00, '', 0.00, '', 0.00

    hnd_mult = 1.00 if p.stand == 'R' else -1.00

    #Creating bounding coords for strike zone & actual
    x1, y1, w = -ZONE_RADIUS, p.sz_bot - BALL_RADIUS, ZONE_RADIUS * 2
    x2, y2 = x1 + w, p.sz_top + BALL_RADIUS
    x, y = p.plate_x, p.plate_z

    #Strike misses
    if p.description == 'called_strike':

        if (x < x1):
            horizontal_miss = x1 - x
            horizontal_miss_type = 'inside' if p.stand == 'R' else 'outside'
        elif (x > x2):
            horizontal_miss = x - x2
            horizontal_miss_type = 'outside' if p.stand == 'R' else 'inside'
        else:
            horizontal_miss = 0
            horizontal_miss_type = ''

        if (y < y1):
            vertical_miss = y1 - y
            vertical_miss_type = 'low'
        elif (y > y2):
            vertical_miss = y - y2
            vertical_miss_type = 'high'
        else:
            vertical_miss = 0
            vertical_miss_type = ''

    elif p.description == 'ball':

        ## need to confirm call is within the coords
        ## how do we determine by how much a miss was?
        ## ahh if x is < 0 then we use x1, if x is > 0 then we use x2 (closest)
        ## y is different? get median of zone from sz_bot, sz_top, if y is > then high else low

        if (x1 < x and x < x2) and (y1 < y and y < y2):

            if (x <= 0):
                horizontal_miss = x - x1
                horizontal_miss_type = 'inside' if p.stand == 'R' else 'outside'
            elif (x >= 0):
                horizontal_miss = x2 - x
                horizontal_miss_type = 'outside' if p.stand == 'R' else 'inside'

            if (y <= (p.sz_bot + ((p.sz_top - p.sz_bot)/2))):
                vertical_miss = y - y1
                vertical_miss_type = 'low'
            elif (y >= (p.sz_bot + ((p.sz_top - p.sz_bot)/2))):
                vertical_miss = y2 - y
                vertical_miss_type = 'high'

        else:
            horizontal_miss = 0
            horizontal_miss_type = ''

            vertical_miss = 0
            vertical_miss_type = ''

    #Convert misses to inches
    horizontal_miss = round(horizontal_miss * 12.00,2)
    vertical_miss = round(vertical_miss * 12.00,2)


    total_miss = round(horizontal_miss + vertical_miss if p.description == 'called_strike' else min(horizontal_miss,vertical_miss),2)

    if horizontal_miss > 0 and vertical_miss > 0:
        total_miss_type = 'both'
    elif horizontal_miss > 0:
        total_miss_type = 'horizontal'
    elif vertical_miss > 0:
        total_miss_type = 'vertical'
    else:
        total_miss_type = ''

    return horizontal_miss_type, horizontal_miss, vertical_miss_type, vertical_miss, total_miss_type, total_miss

def classify_pitches(p,s):
    """p is the pitch
    s is the sample of adjustments to mimic error
    """
    if p.description not in CALLS:
        return ''
    
    if any(v == 0 for v in (p.plate_x,p.plate_z,p.sz_bot,p.sz_top)):
        return ''

    check = [
        classify_pitch(
            p.description,
            p.sz_bot,
            p.sz_top,
            p.plate_x + (x[0] / 12.00),
            p.plate_z + (x[1] / 12.00)
        )
        for x in s]

    if (round(check.count(False)/len(check),2)*100) >= PROB_REQ:
        return 'missed'
    else:
        return ''

def check_calls(df):
    """Runs an initial check of called strikes & balls, adds col indicating misses
    """
    s = get_combined()
    df = df[df['description'].isin(CALLS)] 
    print(f'Running call check for {len(df)} calls..')
    #df['call_check'] = df.apply(lambda x: classify_pitches(x,s), axis=1)
    df['call_check'] = df.progress_apply(lambda x: classify_pitches(x,s), axis=1)

    print(f'Found {len(df[df["call_check"] == "missed"])} bad calls.')
    return df

def get_misses(df):
    """
    """
    df[RETURN_COLS] = df.progress_apply(lambda x: determine_miss(x), axis = 1, result_type='expand') 
    return df
