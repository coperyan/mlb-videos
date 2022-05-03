import os
import pandas as pd
import logging
import logging.config
#import scipy.stats as stats
from tqdm import tqdm
from collections import namedtuple

from constants import DotDict

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

AVG_ERROR = 0.25
SAMPLE = 10000
BALL_RADIUS = 0.12
PROB_REQ = 90
ZONE_RADIUS = 0.83
WIDTH = ZONE_RADIUS * 2
X1 = -ZONE_RADIUS
X2 = X1 + WIDTH

CALLS = [
    'called_strike',
    'ball'
]
SRC_COLS = [
    'description',
    'sz_bot',
    'sz_top',
    'plate_x',
    'plate_z',
    'stand',
]
COLS = [
    'horizontal_miss_type',
    'horizontal_miss',
    'vertical_miss_type',
    'vertical_miss',
    'total_miss_type',
    'total_miss'
]

def convert_to_inches(v):
    """Converts to in....
    """
    return round(v*12.00,2)

def handedness_multiplier(s):
    """Multiplier based on handedness
    Relative to lefty/righty
    """
    return 1.00 if s == 'R' else -1.00

def generate_coords(sz_bot, sz_top, plate_x, plate_z):
    """Basic calcs used to determine misses
    Geometry...
    """
    return {
        'W': (ZONE_RADIUS * 2),
        'X1': -ZONE_RADIUS,
        'X2': (-ZONE_RADIUS + (ZONE_RADIUS * 2)),
        'Y1': (sz_bot - BALL_RADIUS),
        'Y2': (sz_top + BALL_RADIUS),
        'X': plate_x,
        'Y': plate_z,
    }

def default_vals():
    return None, 0, None, 0, None, 0

def calc_total_miss_type(hm,vm):
    """Checks vert/horiz misses for classification
    """
    if hm > 0 and vm > 0:
        return 'both'
    elif hm > 0:
        return 'horizontal'
    elif vm > 0:
        return 'vertical'
    else:
        return None

def calculate_strike(d):
    """Calculates called strike miss
    """
    if d.X < d.X1:
        hm = d.X1 - d.X
        hmt = 'inside' if d.stand == 'R' else 'outside'
    elif d.X > d.X2:
        hm = d.X - d.X2
        hmt = 'outside' if d.stand == 'R' else 'inside'
    else:
        hm = 0
        hmt = None

    if d.Y < d.Y1:
        vm = d.Y1 - d.Y
        vmt = 'low'
    elif d.Y > d.Y2:
        vm = d.Y - d.Y2
        vmt = 'high'
    else:
        vm = 0
        vmt = None

    hm, vm = convert_to_inches(hm), convert_to_inches(vm)
    tm = round(hm + vm,2)
    tmt = calc_total_miss_type(hm,vm)

    return hmt,hm,vmt,vm,tmt,tm

def calculate_ball(d):
    """
    """
    if (d.X1 < d.X and d.X < d.X2) and \
        (d.Y1 < d.Y and d.Y < d.Y2):

        if d.X <= 0:
            hm = d.X - d.X1
            hmt = 'inside' if d.stand == 'R' else 'outside'
        elif d.X >= 0:
            hm = d.X2 - d.X
            hmt = 'outside' if d.stand == 'R' else 'inside'

        if (d.Y <= (d.sz_bot + ((d.sz_top - d.sz_bot)/2))):
            vm = d.Y - d.Y1
            vmt = 'low'
        elif (d.Y >= (d.sz_bot + ((d.sz_top - d.sz_bot)/2))):
            vm = d.Y2 - d.Y
            vmt = 'high'
    else:
        hm, hmt, vm, vmt = [0, None, 0, None]

    hm, vm = convert_to_inches(hm), convert_to_inches(vm)
    tm = round(min(hm, vm),2)
    tmt = calc_total_miss_type(hm,vm)

    return hmt,hm,vmt,vm,tmt,tm

def calculate_miss(p):
    """Parameter is a Pitch, named tuple
    Has all of the normal pitch attributes

    First we check for missing vals OR non-calls
    Returns blanks / zeros in that case
    """
    if any(v == 0 for v in (p.plate_x,p.plate_z,p.sz_bot,p.sz_top)) or \
        p.description not in CALLS:
        return default_vals()
    else:
        d = {
            x: getattr(p,x) for x in SRC_COLS
        }
        d.update(
            generate_coords(
                p.sz_bot, p.sz_top, p.plate_x, p.plate_z
            )
        )
        d = DotDict(d)

        if p.description == 'called_strike':
            return calculate_strike(d)
        elif p.description == 'ball':
            return calculate_ball(d)


