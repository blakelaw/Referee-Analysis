#Imports
from scipy.stats import ttest_rel
import numpy as np
import sqlite3 as sql
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LogisticRegression

#Connect to SQL database
conn = sql.connect('nba.sqlite') # create connection object to database
df = pd.read_sql('select * from combined_all2', conn)

#Convert W to 1 and L to 0
df['home_result'] = df['wl_home'].apply(lambda x: 1 if x == 'W' else 0)
df['away_result'] = df['wl_home'].apply(lambda x: 0 if x == 'W' else 1)

#Create year column
df['game_date'] = pd.to_datetime(df['game_date'])
df['year'] = df['game_date'].dt.year

# Calculate home game winning percentage and number of away games each year
home_games_group = df.groupby(['year', 'team_abbreviation_home'])
home_games_stats = home_games_group.agg(
    home_win_percentage_year=('home_result', 'mean'),
    home_games_played=('home_result', 'count')
).reset_index()

# Calculate away game winning percentage and number of away games each year
away_games_group = df.groupby(['year', 'team_abbreviation_away'])
away_games_stats = away_games_group.agg(
    away_win_percentage_year=('away_result', 'mean'),
    away_games_played=('away_result', 'count')
).reset_index()

# Create new columns in the original dataframe to store the calculated statistics
df = df.merge(home_games_stats, how='left', left_on=['year', 'team_abbreviation_home'], right_on=['year', 'team_abbreviation_home'])
df = df.merge(away_games_stats, how='left', left_on=['year', 'team_abbreviation_away'], right_on=['year', 'team_abbreviation_away'])

#Create column for days since first date in new dataframe (01/02/2004)
reference_date = datetime(2004, 1, 2)
df['days_since_reference'] = (df['game_date'] - reference_date).dt.days

#Filter to only seasons with 30+ home and away games (90/3 due to three officials for every game)
df2 = df[(df['home_games_played'] > 90) & (df['away_games_played'] > 90)]

#Create dataframe for propensity score matching
psm_data = df2[['official_id', 'game_id', 'home_win_percentage_year', 'away_win_percentage_year', 'year', 'days_since_reference', 'home_result']].copy()
psm_data.rename(columns={
    'home_win_percentage_year': 'home_pct',
    'away_win_percentage_year': 'away_pct',
    'days_since_reference': 'time',
    'home_result': 'result'
}, inplace=True)
psm_data = psm_data.astype('double')

#Calculate propensity scores with logistic regression
def calculate_propensity_scores(data):
    X = data[['home_pct', 'away_pct', 'time']]
    y = data['result']
    model = LogisticRegression()
    model.fit(X, y)
    propensity_scores = model.predict_proba(X)[:, 1]
    return propensity_scores

# Initialize a new column with NaNs
psm_data['propensity_score'] = None

# Loop over each official_id group and assign the propensity scores directly
for official_id, group_data in psm_data.groupby('official_id'):
    psm_data.loc[group_data.index, 'propensity_score'] = calculate_propensity_scores(group_data)

#Find closest match by matching propensity scores by absolute difference, but ensure the match is another referee and not the same game (since there are multiple referees per game)
def find_closest_match(row):
    valid_matches = psm_data[(psm_data['official_id'] != row['official_id']) & (psm_data['game_id'] != row['game_id'])]
    if valid_matches.empty:
        return pd.Series([None]*len(row), index=['matched_' + col for col in psm_data.columns])
    closest_match = valid_matches.loc[(valid_matches['propensity_score'] - row['propensity_score']).abs().idxmin()]
    return closest_match.add_prefix('matched_')

#Concatenate matches to the row it is being matched to
result_df = psm_data.apply(lambda row: pd.concat([row, find_closest_match(row)]), axis=1)

# Separate original and matched data
original_data = result_df.iloc[:, :len(psm_data.columns)]
matched_data = result_df.iloc[:, len(psm_data.columns):]

# Initialize a dictionary to store the results
effect_sizes = {}

# Loop through each official_id
for official_id in original_data['official_id'].unique():
    # Get the rows for the current official_id from both original and matched data
    original_rows = original_data[original_data['official_id'] == official_id]
    matched_rows = matched_data[original_data['official_id'] == official_id]
    
    # Conduct paired t-test (on 'result' column as an example)
    t_statistic, p_value = ttest_rel(original_rows['result'], matched_rows['matched_result'].dropna())

    # Calculate Cohen's d as the effect size
    cohen_d = (original_rows['result'].mean() - matched_rows['matched_result'].mean()) / np.sqrt(((original_rows['result'].std() ** 2 + matched_rows['matched_result'].std() ** 2) / 2))
    
    # Store the results in the dictionary
    effect_sizes[official_id] = {"t_statistic": t_statistic, "p_value": p_value, "cohen_d": cohen_d}

# Convert the results dictionary to a DataFrame
effect_size_df = pd.DataFrame.from_dict(effect_sizes, orient='index')

# Merge to get the first_name and last_name from the original df
effect_size_df.reset_index(inplace=True)
effect_size_df.rename(columns={'index': 'official_id'}, inplace=True)
df['official_id'] = df['official_id'].astype('float64')
effect_size_df = effect_size_df.merge(df[['official_id', 'first_name', 'last_name']], on='official_id', how='left')
effect_size_df = effect_size_df.drop_duplicates()


# Create a 'Referee' column by combining 'first_name' and 'last_name'
effect_size_df['Referee'] = effect_size_df['first_name'] + " " + effect_size_df['last_name']

# Select top 10 rows based on 'p_value'
top_10_p_value = effect_size_df.nsmallest(10, 'p_value')

# Rename columns
PSM_results = top_10_p_value[['Referee', 'p_value', 't_statistic', 'cohen_d']]
PSM_results.columns = ['Referee', 'p-value', 't statistic', "cohen's d"]
PSM_results.to_csv('Outputs/PSM_Results.csv')

