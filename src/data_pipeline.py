import nfl_data_py as nfl
import pandas as pd
import numpy as np

def load_pbp_data(seasons):
    # Load play by play data for the specified seasons
    play_by_play_data = nfl.import_pbp_data(seasons)
    df = pd.DataFrame(play_by_play_data)
    return df

cols_to_keep = ['play_id', 'week', 'season', 'home_team', 'away_team', 'posteam', 'defteam', 'play_type', 'yards_gained', 'air_yards', 'yards_after_catch',
                'field_goal_result', 'total_home_score', 'total_away_score', 'total_home_rush_wpa', 'total_home_pass_wpa', 'total_away_rush_wpa', 'total_away_pass_wpa',
                'total_home_comp_air_wpa', 'total_away_comp_air_wpa', 'total_home_comp_yac_wpa', 'total_away_comp_yac_wpa', 'third_down_converted', 'third_down_failed', 
                'fourth_down_converted', 'fourth_down_failed', 'interception', 'fumble_forced', 'tackled_for_loss', 'qb_hit', 'rush_attempt', 'pass_attempt', 'sack', 'pass_touchdown',
                'rush_touchdown', 'return_touchdown', 'field_goal_attempt', 'penalty_team', 'penalty_yards', 'spread_line', 'total_line', 
                'defenders_in_box', 'number_of_pass_rushers']

def field_goal_percentage(x):
    denom = x['field_goal_attempt'].sum()
    if denom == 0:
        return 0
    return x['field_goal_result'].sum() / denom

def third_down_conversion(x):
    denom = x['third_down_converted'].sum() + x['third_down_failed'].sum()
    if denom == 0:
        return 0
    return x['third_down_converted'].sum() / denom

def fourth_down_conversion(x):
    denom = x['fourth_down_converted'].sum() + x['fourth_down_failed'].sum()
    if denom == 0:
        return 0
    return x['fourth_down_converted'].sum() / denom

aggregation_dict = {
    'yards_gained': 'sum',
    'air_yards': 'sum',
    'yards_after_catch': 'sum',
    'total_home_score': 'max',
    'total_away_score': 'max',
    'total_home_rush_wpa': 'sum',
    'total_home_pass_wpa': 'sum',
    'interception': 'sum',
    'fumble_forced': 'sum',
    'tackled_for_loss': 'sum',
    'qb_hit': 'sum',
    'rush_attempt': 'sum',
    'pass_attempt': 'sum',
    'sack': 'sum',
    'pass_touchdown': 'sum',
    'rush_touchdown': 'sum',
    'return_touchdown': 'sum',
    'penalty_yards': 'sum',
    'defenders_in_box': 'mean',
    'number_of_pass_rushers': 'mean',
    'calculated_passing_yards': 'sum',
    'calculated_rushing_yards': 'sum',
    'field_goal_result': field_goal_percentage,
    'third_down_converted': third_down_conversion,
    'fourth_down_converted': fourth_down_conversion
}

if __name__ == "__main__":  
    pbp_data = load_pbp_data([2022])
    pbp_data = pbp_data[cols_to_keep]
    pbp_data = pbp_data[pbp_data['play_type'].notna()]
    pbp_data = pbp_data[pbp_data['play_type'] != 'no_play']
    pbp_data['field_goal_result'] = pbp_data['field_goal_result'].replace({'made': 1, 'missed': 0, 'blocked': 0})
    pbp_data = pbp_data[~pbp_data['play_type'].isin(['qb_kneel', 'qb_spike'])]
    pbp_data.loc[(pbp_data['play_type'] == 'run') & (pbp_data['air_yards'].isna()), 'air_yards'] = 0
    pbp_data.loc[(pbp_data['play_type'] == 'run') & (pbp_data['yards_after_catch'].isna()), 'yards_after_catch'] = 0
    pbp_data.loc[(pbp_data['penalty_team'].isna()), 'penalty_team'] = 0
    pbp_data.loc[(pbp_data['penalty_yards'].isna()), 'penalty_yards'] = 0
    pbp_data.loc[(pbp_data['field_goal_result'].isna()), 'field_goal_result'] = 0
    pbp_data = pbp_data.copy()
    pbp_data['calculated_passing_yards'] = pbp_data.apply(lambda row: row['yards_gained'] if row['play_type'] == 'pass' else 0, axis=1)
    pbp_data['calculated_rushing_yards'] = pbp_data.apply(lambda row: row['yards_gained'] if row['play_type'] == 'run' else 0, axis=1)
    pbp_data.loc[(pbp_data['play_type'] == 'pass') & (pbp_data['air_yards'].isna()), 'air_yards'] = 0
    pbp_data.loc[(pbp_data['play_type'] == 'pass') & (pbp_data['yards_after_catch'].isna()), 'yards_after_catch'] = 0
    special_teams_plays = ['kickoff', 'punt', 'field_goal', 'extra_point']

    offensive_stats = ['air_yards', 'yards_after_catch']

    for play in special_teams_plays:
        for stat in offensive_stats:
            pbp_data.loc[(pbp_data['play_type'] == play) & (pbp_data[stat].isna()), stat] = 0
            
    pbp_data = pbp_data.drop(pbp_data[(pbp_data['play_type'] != 'pass') & (~pbp_data['number_of_pass_rushers'].isna())].index)
    pbp_data = pbp_data.drop(pbp_data[((pbp_data['play_type'] == 'run') | (pbp_data['play_type'] == 'pass')) & (pbp_data['defenders_in_box'].isna())].index)

    aggregated_data = pd.DataFrame()

    for (season, week, home_team), group_data in pbp_data[pbp_data['posteam'] == pbp_data['home_team']].groupby(['season', 'week', 'home_team']):

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