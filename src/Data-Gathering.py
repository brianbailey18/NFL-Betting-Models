import nfl_data_py as nfl

def load_pbp_data(seasons):
    # Load play by play data for the specified seasons
    play_by_play_data = nfl.import_pbp_data(seasons)
    return play_by_play_data

def load_weekly_data(seasons):
    # load play by play data for the specified seasons
    weekly_data = nfl.import_weekly_data(seasons)
    return weekly_data

# # Load data for the 2022 NFL season
# data = load_nfl_data([2023])
# data = load_pbp_data([2023])

# print(data.head(5))

# # Print the first 5 rows of the data
for col in nfl.see_pbp_cols():
    print(col, "\n")
