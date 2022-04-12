import os
import json

def horizontal_break(p):
    """Calculates horizontal break for pitch
    """
    return p.pfx_x * -12.00

def vertical_break(p):
    """Calculates vertical break for pitch
    """
    return p.pfx_z * 12.00

def total_break(p):
    """Calculcates total break
    """
    return p.horizontal_break + p.vertical_break

def total_break_abs(p):
    """Calculates total break (abs)
    """
    return abs(p.horizontal_break) + abs(p.vertical_break)

def add_movement_avgs(df):
    """Calculate movement averages by pitch type
    Add variance cols for each type of movement vs avg
    """
    avg_df = df[['pitch_type','horizontal_break','vertical_break','total_break_abs','total_break']].groupby('pitch_type')
    avg_df = avg_df.mean()
    avg_df = avg_df.reset_index()
    avg_df = avg_df.rename(columns={
        'horizontal_break': 'horizontal_break_avg',
        'vertical_break': 'vertical_break_avg',
        'total_break_abs': 'total_break_abs_avg',
        'total_break': 'total_break_avg'
    })
    new_df = df.merge(avg_df,on='pitch_type')

    new_df['horizontal_break_var'] = new_df.apply(lambda x: x.horizontal_break - x.horizontal_break_avg, axis=1)
    new_df['vertical_break_var'] = new_df.apply(lambda x: x.vertical_break - x.vertical_break_avg, axis=1)
    new_df['total_break_abs_var'] = new_df.apply(lambda x: x.total_break_abs - x.total_break_abs_avg, axis=1)
    new_df['total_break_var'] = new_df.apply(lambda x: x.total_break - x.total_break_avg, axis=1)
    
    return new_df

def add_pitch_movement_cols(df):
    """Function to add pitch movement cols to dataframe
    First, filter out pitches with no pfx data
    """
    df = df[
        (df['pfx_x'].notnull()) & 
        (df['pfx_z'].notnull())
    ]

    df['horizontal_break'] = df.apply(lambda x: horizontal_break(x), axis=1)
    df['vertical_break'] = df.apply(lambda x: vertical_break(x), axis=1)
    df['total_break'] = df.apply(lambda x: total_break(x), axis=1)
    df['total_break_abs'] = df.apply(lambda x: total_break_abs(x), axis=1)
    df = add_movement_avgs(df)

    return df

