#Imports
import sqlite3 as sql
import pandas as pd

# create connection object to database
conn = sql.connect('nba.sqlite') 
df = pd.read_sql('select * from combined_all2', conn)

home_games = df[['team_abbreviation_home','game_id', 'game_date', 'official_id', 'team_id_home', 'pts_home', 'first_name', 'last_name']].rename(columns={'team_abbreviation_home': 'team_abbreviation','team_id_home': 'team_id', 'pts_home': 'pts'})
away_games = df[['team_abbreviation_away','game_id', 'game_date', 'official_id', 'team_id_away', 'pts_away','first_name', 'last_name']].rename(columns={'team_abbreviation_away': 'team_abbreviation', 'team_id_away': 'team_id', 'pts_away': 'pts'})
combined = pd.concat([home_games, away_games], axis=0)

#Dataframe for referees showing average score for each team combination and number of games
grouped_df = combined.groupby(['official_id', 'team_abbreviation']).agg(avg_pts=('pts', 'mean'), num_games=('pts', 'size')).reset_index()

#Add first and last name labels to each referee
expanded_df = grouped_df.merge(combined[['official_id', 'first_name', 'last_name']], on='official_id', how='left')

#Remove duplicates and rename columns
expanded_df = expanded_df.drop_duplicates()
expanded_df = expanded_df.rename(columns={'avg_pts': 'avg_pts_ref'})

#Find the average score for each team
avg = combined.groupby('team_abbreviation')['pts'].mean().reset_index()
avg = avg.rename(columns={'pts': 'avg_score'})

#Merge this average score with the table of referees
expanded_df = expanded_df.merge(avg, on='team_abbreviation', how='left')

# Rename the 'avg_score' column from 'new_table' to 'avg_team_score'
expanded_df = expanded_df.rename(columns={'avg_score': 'avg_pts_team'})

#Metric 1: Difference in average scores with referee versus average scores overall
expanded_df['score_difference'] = expanded_df['avg_pts_ref'] - expanded_df['avg_pts_team']
expanded_df['abs_score_difference'] = expanded_df['score_difference'].abs()

#Dataframe to only show matches with 30 games refereed to reduce noise
expanded_df_30 = expanded_df[expanded_df['num_games'] > 30].reset_index()
expanded_df_30 = expanded_df_30.sort_values(by='abs_score_difference', ascending=False)

#Table of the top 10 highest by metric 1 (for blog post)
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

#Table for highest scorer of metric 1 for diagram in Tableau
Ged_Games = combined[(combined['first_name']=='Gediminas') & (combined['team_abbreviation']=='WAS')][['game_date','pts']]
WAS = combined[combined['team_abbreviation']=='WAS'][['game_date','pts']]

Ged_Games = Ged_Games.drop_duplicates()
WAS = WAS.drop_duplicates()

WAS['game_date'] = pd.to_datetime(WAS['game_date'])
Ged_Games['game_date'] = pd.to_datetime(Ged_Games['game_date'])
Ged_Games.to_csv('Outputs/Ged_Games.csv')
WAS.to_csv('Outputs/WAS.csv')

#Convert game_date to year for metric 2
combined['game_date'] = pd.to_datetime(combined['game_date'])
combined['year'] = combined['game_date'].dt.year

#Find average for a team in a given year
avg2 = combined.groupby(['year', 'team_abbreviation'])['pts'].mean().reset_index()
avg2 = avg2.rename(columns={'pts': 'avg_score'})

#Metric 2: Difference between team average in a given year and the referee's average
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

#Like before, only show those with 30 games refereed for a given team
avg_diff_30 = avg_diff[avg_diff['num_games'] > 30]
avg_diff_30 = avg_diff_30.sort_values(by='abs_score_difference', ascending=False)

#Table showing top 10 by metric 2
diagram2 = avg_diff_30.head(10)[['team_abbreviation', 'referee_name', 'num_games', 'score_diff', 'abs_score_difference']]

diagram2 = diagram2.rename(columns={
    'team_abbreviation': 'Team',
    'num_games': 'Games',
    'score_diff': 'Difference',
    'abs_score_difference': 'Absolute Difference'
})

diagram2.to_csv('Outputs/diagram2.csv')

#Table showing highest scorer on metric two and the associate team scores
Ayotte_Games = combined[(combined['first_name']=='Mark') & (combined['last_name']=='Ayotte') & ((combined['team_abbreviation']=='NYK'))][['game_date','pts']]
NYK = combined[combined['team_abbreviation']=='NYK'][['game_date','pts']]

Ayotte_Games = Ayotte_Games.drop_duplicates()
NYK = NYK.drop_duplicates()

NYK['game_date'] = pd.to_datetime(NYK['game_date'])
Ayotte_Games['game_date'] = pd.to_datetime(Ayotte_Games['game_date'])
Ayotte_Games.to_csv('Outputs/Ayotte_Games.csv')
NYK.to_csv('Outputs/NYK.csv')

