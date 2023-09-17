import pandas as pd

# Load the data including more metrics: blocks, steals, 3p%, etc. for each referee
data = pd.read_csv('Outputs/stats.csv')

# List of columns that contain statistics
stats_columns = ['fgm', 'fg_pct', 'fg3m', 'fg3_pct', 'ftm', 'ft_pct', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov',
                 'pf', 'pts']

# Group by referee and aggregate the original data
aggregated_raw_data = data.groupby(['first_name', 'last_name', 'official_id']).agg(
    {**{col: 'mean' for col in stats_columns}, 'game_date': 'count'}).reset_index()
aggregated_raw_data = aggregated_raw_data.rename(columns={'game_date': 'num_games'})
# Normalize the aggregated data
aggregated_raw_data[stats_columns] = (aggregated_raw_data[stats_columns] - aggregated_raw_data[stats_columns].mean()) / \
                                     aggregated_raw_data[stats_columns].std()

# Create a dataframe for means and standard deviations
means = data[stats_columns].mean()
stds = data[stats_columns].std()
mean_std_df = pd.DataFrame({
    'first_name': ['MEAN', 'STD_DEV'],
    'last_name': ['', ''],
    'official_id': ['', ''],
    **{col: [means[col], stds[col]] for col in stats_columns},
    'num_games': ['', '']
})

# Concatenate the mean_std_df with the aggregated raw data to create the final table
final_table_corrected = pd.concat([mean_std_df, aggregated_raw_data], ignore_index=True)

# Split the dataframe
top_rows = final_table_corrected.iloc[:2]
remaining_rows = final_table_corrected.iloc[2:]

sorted_remaining_rows = remaining_rows.sort_values(by='num_games', ascending=False).reset_index(drop=True)

final_table_sorted = pd.concat([top_rows, sorted_remaining_rows], ignore_index=True)

#Create dataset for PCA analysis in R
PCA = remaining_rows[remaining_rows['num_games'] > 100]
PCA.to_csv('Outputs/PCA.csv')

