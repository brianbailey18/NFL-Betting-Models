import nfl_data_py as nfl
import pandas as pd
import numpy as np
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, '../config')
sys.path.append(config_path)
from config import cols_to_keep, aggregation_dict

def load_pbp_data(seasons):
    """
    Load play-by-play data for the specified seasons.
    
    Parameters:
        seasons (list): List of seasons for which to load data.
        
    Returns:
        pd.DataFrame: Loaded data in a DataFrame.
    """
    play_by_play_data = nfl.import_pbp_data(seasons)
    df = pd.DataFrame(play_by_play_data)
    return df

def filter_columns(df, cols_to_keep):
    """
    Filter DataFrame to keep only specified columns.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to filter.
        cols_to_keep (list): List of column names to keep.
        
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    return df[cols_to_keep]

def remove_unwanted_plays(df):
    """
    Filter DataFrame to keep only specified plays.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to filter.
        
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    
    df = df[df['play_type'].notna()]
    df = df[df['play_type'] != 'no_play']
    df = df[~df['play_type'].isin(['qb_kneel', 'qb_spike'])]
    df = df.drop(df[(df['play_type'] != 'pass') & (~df['number_of_pass_rushers'].isna())].index)
    df = df.drop(df[((df['play_type'] == 'run') | (df['play_type'] == 'pass')) & (df['defenders_in_box'].isna())].index)
    return df

def zero_fill(df): 
    """
    Zero fill values in a DataFrame to simplify creating week-by-week data.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to fill.
        
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    df.loc[(df['play_type'] == 'run') & (df['air_yards'].isna()), 'air_yards'] = 0
    df.loc[(df['play_type'] == 'run') & (df['yards_after_catch'].isna()), 'yards_after_catch'] = 0
    df.loc[(df['penalty_team'].isna()), 'penalty_team'] = 0
    df.loc[(df['penalty_yards'].isna()), 'penalty_yards'] = 0
    df.loc[(df['field_goal_result'].isna()), 'field_goal_result'] = 0
    df.loc[(df['play_type'] == 'pass') & (df['air_yards'].isna()), 'air_yards'] = 0
    df.loc[(df['play_type'] == 'pass') & (df['yards_after_catch'].isna()), 'yards_after_catch'] = 0
    return df

def filter_special_teams_values(df):
    """
    Zero fill values, specifically to account for special teams plays, in a DataFrame to simplify creating week-by-week data.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to fill.
        
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    special_teams_plays = ['kickoff', 'punt', 'field_goal', 'extra_point']

    offensive_stats = ['air_yards', 'yards_after_catch']

    for play in special_teams_plays:
        for stat in offensive_stats:
            df.loc[(df['play_type'] == play) & (df[stat].isna()), stat] = 0

    return df

def add_new_stats(df):
    """
    Creates some new stats, including rushing and passing yards, in a DataFrame to simplify creating week-by-week data.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to fill.
        
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    df['field_goal_result'] = df['field_goal_result'].replace({'made': 1, 'missed': 0, 'blocked': 0})
    df = df.copy()
    df['calculated_passing_yards'] = df.apply(lambda row: row['yards_gained'] if row['play_type'] == 'pass' else 0, axis=1)
    df['calculated_rushing_yards'] = df.apply(lambda row: row['yards_gained'] if row['play_type'] == 'run' else 0, axis=1)
    return df

def clean_dataframe(df, cols_to_keep):
    """
    Complete all data cleaning required to later create week-by-week data. This includes filtering the columns, dropping 
    unnecessary rows, zero filling some NaN values, and creating rushing and passing yard totals.

    Parameters: 
        df (pd.DataFrame): The DataFrame to clean.
        cols_to_keep (list): List of column names to keep.

    Returns: 
        pd.DataFrame: a cleaned DataFrame.
    """
    #filter the columns 
    df = filter_columns(df, cols_to_keep)

    #remove unwanted plays
    df = remove_unwanted_plays(df)

    #zero fill NaN values
    df = zero_fill(df)

    #remove unnecessary NaN values in special teams plays
    df = filter_special_teams_values(df)

    #add required stats
    df = add_new_stats(df)

    return df

def aggregate_data(df, aggregation_dict):
    """
    Complete all data aggregation required to later create week-by-week rolling average data. This includes creating weekly
    stats, aggregating each category in the correct manner.

    Parameters: 
        df (pd.DataFrame): The DataFrame to aggregate.

    Returns: 
        pd.DataFrame: a cleaned DataFrame.
    """
    aggregated_data = pd.DataFrame()

    for (season, week, home_team), group_data in df[df['posteam'] == df['home_team']].groupby(['season', 'week', 'home_team']):

        aggregated_row = {}
        aggregated_row['season'] = season
        aggregated_row['week'] = week
        aggregated_row['home_team'] = home_team

        for column, agg_func in aggregation_dict.items():
            if callable(agg_func):  # If the value is a function, call it
                aggregated_row[column] = agg_func(group_data)
            elif agg_func == 'sum':
                aggregated_row[column] = group_data[column].sum()
            elif agg_func == 'max':
                aggregated_row[column] = group_data[column].max()
            elif agg_func == 'mean':
                aggregated_row[column] = group_data[column].mean()

        aggregated_data = pd.concat([aggregated_data, pd.DataFrame([aggregated_row])], ignore_index=True)

    return aggregated_data

if __name__ == "__main__":  
    pbp_data = load_pbp_data([2022])
    cleaned_data = clean_dataframe(pbp_data, cols_to_keep)
    aggregated_data = aggregate_data(cleaned_data, aggregation_dict)
    print(aggregated_data.head())