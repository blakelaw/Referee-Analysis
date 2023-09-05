#Imports
import sqlite3 as sql
import pandas as pd
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import HoverTool, ColumnDataSource
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import statsmodels.api as sm

conn = sql.connect('nba.sqlite') # create connection object to database
df = pd.read_sql('select * from combined_all2', conn)
df.to_csv('df.csv')

home_games = df[['team_abbreviation_home','game_id', 'game_date', 'official_id', 'team_id_home', 'pts_home', 'first_name', 'last_name']].rename(columns={'team_abbreviation_home': 'team_abbreviation','team_id_home': 'team_id', 'pts_home': 'pts'})
away_games = df[['team_abbreviation_away','game_id', 'game_date', 'official_id', 'team_id_away', 'pts_away','first_name', 'last_name']].rename(columns={'team_abbreviation_away': 'team_abbreviation', 'team_id_away': 'team_id', 'pts_away': 'pts'})

combined = pd.concat([home_games, away_games], axis=0)

grouped_df = combined.groupby(['official_id', 'team_abbreviation']).agg(avg_pts=('pts', 'mean'), num_games=('pts', 'size')).reset_index()

expanded_df = grouped_df.merge(combined[['official_id', 'first_name', 'last_name']], on='official_id', how='left')

expanded_df = expanded_df.drop_duplicates()
expanded_df = expanded_df.rename(columns={'avg_pts': 'avg_pts_ref'})


avg = combined.groupby('team_abbreviation')['pts'].mean().reset_index()
avg = avg.rename(columns={'pts': 'avg_score'})

expanded_df = expanded_df.merge(avg, on='team_abbreviation', how='left')

# Rename the 'avg_score' column from 'new_table' to 'avg_team_score'
expanded_df = expanded_df.rename(columns={'avg_score': 'avg_pts_team'})

expanded_df['score_difference'] = expanded_df['avg_pts_ref'] - expanded_df['avg_pts_team']
expanded_df['abs_score_difference'] = expanded_df['score_difference'].abs()

expanded_df_30 = expanded_df[expanded_df['num_games'] > 30].reset_index()
expanded_df_30 = expanded_df_30.sort_values(by='abs_score_difference', ascending=False)

diagram = expanded_df_30.head(10)[['team_abbreviation', 'first_name', 'last_name', 'num_games', 'avg_pts_team', 'avg_pts_ref', 'score_difference', 'abs_score_difference']]
diagram.insert(3, 'Full Name', diagram['first_name'] + ' ' + diagram['last_name'])

diagram = diagram.rename(columns={
    'team_abbreviation': 'Team',
    'num_games': 'Games',
    'avg_pts_team': 'Team Average',
    'avg_pts_ref': 'Ref Average',
    'score_difference': 'Difference',
    'abs_score_difference': 'Absolute Difference'
})
diagram

Ged_Games = combined[(combined['first_name']=='Gediminas') & (combined['team_abbreviation']=='WAS')][['game_date','pts']]
WAS = combined[combined['team_abbreviation']=='WAS'][['game_date','pts']]

Ged_Games = Ged_Games.drop_duplicates()
WAS = WAS.drop_duplicates()

WAS['game_date'] = pd.to_datetime(WAS['game_date'])
Ged_Games['game_date'] = pd.to_datetime(Ged_Games['game_date'])

Ged_Games.to_csv('Ged_Games.csv')
WAS.to_csv('WAS.csv')

diff = expanded_df_30['score_difference'].round().astype(int)


diff.to_csv('diff.csv')

combined['game_date'] = pd.to_datetime(combined['game_date'])
combined['year'] = combined['game_date'].dt.year

avg2 = combined.groupby(['year', 'team_abbreviation'])['pts'].mean().reset_index()
avg2 = avg2.rename(columns={'pts': 'avg_score'})

combined = pd.merge(combined, avg2,  how='left', left_on=['year','team_abbreviation'], right_on = ['year','team_abbreviation'])
combined['score_diff'] = combined['pts'] - combined['avg_score']

avg_diff = combined.groupby(['official_id', 'team_abbreviation'])['score_diff'].mean().reset_index()

num_games = combined.groupby(['official_id', 'team_abbreviation']).size().reset_index(name='num_games')

referee_names = combined[['official_id', 'first_name', 'last_name']].drop_duplicates()
referee_names['referee_name'] = referee_names['first_name'] + ' ' + referee_names['last_name']
referee_names = referee_names[['official_id', 'referee_name']].drop_duplicates()

avg_diff = pd.merge(avg_diff, num_games,  how='left', on=['official_id', 'team_abbreviation'])
avg_diff = pd.merge(avg_diff, referee_names, how='left', on='official_id')
avg_diff['abs_score_difference'] = avg_diff['score_diff'].abs()

combined[(combined['team_abbreviation'] == 'NJN') & (combined['official_id'] == '202049')]

avg_diff_30 = avg_diff[avg_diff['num_games'] > 30]
avg_diff_30 = avg_diff_30.sort_values(by='abs_score_difference', ascending=False)


avg_diff_30

diagram2 = avg_diff_30.head(10)[['team_abbreviation', 'referee_name', 'num_games', 'score_diff', 'abs_score_difference']]

diagram2 = diagram2.rename(columns={
    'team_abbreviation': 'Team',
    'num_games': 'Games',
    'score_diff': 'Difference',
    'abs_score_difference': 'Absolute Difference'
})
diagram2

diagram2.to_csv('diagram2.csv')

Ayotte_Games = combined[(combined['first_name']=='Mark') & (combined['last_name']=='Ayotte') & ((combined['team_abbreviation']=='NYK'))][['game_date','pts']]
NYK = combined[combined['team_abbreviation']=='NYK'][['game_date','pts']]

Ayotte_Games = Ayotte_Games.drop_duplicates()
NYK = NYK.drop_duplicates()

NYK['game_date'] = pd.to_datetime(NYK['game_date'])
Ayotte_Games['game_date'] = pd.to_datetime(Ayotte_Games['game_date'])


Ayotte_Games.to_csv('Ayotte_Games.csv')
NYK.to_csv('NYK.csv')


H = combined[(combined['last_name']=='Haskill')][['game_date','pts','official_id','first_name','last_name']]


# Load the data
data = pd.read_csv('combined_all3.csv')


# List of columns that contain statistics
stats_columns = ['fgm', 'fg_pct', 'fg3m', 'fg3_pct', 'ftm', 'ft_pct', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts']

# Group by referee and aggregate the original data
aggregated_raw_data = data.groupby(['first_name', 'last_name', 'official_id']).agg({**{col: 'mean' for col in stats_columns}, 'game_date': 'count'}).reset_index()
aggregated_raw_data = aggregated_raw_data.rename(columns={'game_date': 'num_games'})

aggregated_raw_data



# Normalize the aggregated data
aggregated_raw_data[stats_columns] = (aggregated_raw_data[stats_columns] - aggregated_raw_data[stats_columns].mean()) / aggregated_raw_data[stats_columns].std()

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


stats_columns

data[(data['last_name']=='Bernhardt')]

PCA = remaining_rows[remaining_rows['num_games'] > 100]

PCA.to_csv('PCA.csv')

pca_results = pd.read_csv('pca_results.csv')

pca_results['full_name'] = pca_results['first_name'] + " " + pca_results['last_name']
pca_results = pca_results.drop(columns=['X'])


X = pca_results.drop(['official_id', 'first_name', 'last_name', 'num_games', 'full_name'], axis=1)  # Include all variables except the target
y = pca_results['num_games']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = xgb.XGBRegressor()
model.fit(X_train, y_train)

feature_importances = model.feature_importances_



plt.bar(X.columns, feature_importances)
plt.ylabel('Importance Score')
plt.xlabel('Feature')
plt.title('Feature Importance Analysis')
plt.xticks(rotation=90)
plt.show()



X = pca_results[['fg3m', 'oreb', 'dreb', 'reb', 'ast']]
y = pca_results['num_games']

X = sm.add_constant(X)

model = sm.OLS(y, X).fit()

r_squared = model.rsquared
print('R-squared:', r_squared)
print(model.summary())

