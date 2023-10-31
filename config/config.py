import pandas as pd

cols_to_keep = ['play_id', 'week', 'season', 'home_team', 'away_team', 'posteam', 'defteam', 'play_type', 'yards_gained', 'air_yards', 'yards_after_catch',
                'field_goal_result', 'total_home_score', 'total_away_score', 'total_home_rush_wpa', 'total_home_pass_wpa', 'total_away_rush_wpa', 'total_away_pass_wpa',
                'total_home_comp_air_wpa', 'total_away_comp_air_wpa', 'total_home_comp_yac_wpa', 'total_away_comp_yac_wpa', 'third_down_converted', 'third_down_failed', 
                'fourth_down_converted', 'fourth_down_failed', 'interception', 'fumble_forced', 'tackled_for_loss', 'qb_hit', 'rush_attempt', 'pass_attempt', 'sack', 'pass_touchdown',
                'rush_touchdown', 'return_touchdown', 'field_goal_attempt', 'penalty_team', 'penalty_yards', 'spread_line', 'total_line', 
                'defenders_in_box', 'number_of_pass_rushers']

def field_goal_percentage(x):
    """
    Calculate the field goal percentage from a Pandas GroupBy object. 
    """
    denom = x['field_goal_attempt'].sum()
    if denom == 0:
        return 0
    return x['field_goal_result'].sum() / denom

def third_down_conversion(x):
    """
    Calculate the third down conversion percentage from a Pandas GroupBy object. 
    """
    denom = x['third_down_converted'].sum() + x['third_down_failed'].sum()
    if denom == 0:
        return 0
    return x['third_down_converted'].sum() / denom

def fourth_down_conversion(x):
    """
    Calculate the fourth down conversion percentage from a Pandas GroupBy object. 
    """
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