# NBA Referee Neutrality Investigation

[![Blog Article](https://img.shields.io/badge/blog-article-brightgreen?link=https%3A%2F%2Fblakelaw.github.io%2Fprojects%2F1_project%2F)](https://blakelaw.github.io/projects/1_project/)

## Description

This project investigates the neutrality of referees in approximately 64,000 NBA games. This is primarily written in Python, with principal component analysis completed in R.

## Features

- **Data preprocessing**: Transformed dataset by performing group operations, including SQL preprocessing, concatenating home and away game data, merging tables, and filtering data to reduce noise
- **Quantitative Analysis**: Developed four quantitative approaches to evaluate the impact of referees on game metrics and results.
  - **Points over expected**: For a given referee-team combination, the difference in average score when the game was officiated by the referee and the overall average.
  - **Elo score**: Points over expected, but takes the average within the same year rather than the team's overall average. 
  - **Principal component analysis**: Adds 14 features to points, including: assists, steals, blocks, free throw percentage. Each of these features is reduced to two principal components, and the largest deviations in either direction have a higher score.
  - **Propensity score matching**: Ran logistic regression to generate propensity scores for every referee in a given game, based on the home team win percentage, away team win percentage, and the time the game occurred. Matched every game to another game (excluding those officiated by the same referee), and conducted a t-test on 86 experienced referees.


- **Visualization**: Created visualizations for each metric with Tableau and Datawrapper. See blog post.

- **Results**: The analysis did not find any evidence pointing towards a systemic bias on the part of the referees.

## Usage

`metrics.py` - preprocesses dataset and creates points over expected and elo metrics

`PCA.py` - preprocesses dataset for PCA in R

`NBA_PCA_R` - PCA analysis in R

`PSM.py` - propensity score matching on dataset

`Outputs` - Contains all outputs for visualization and PCA loadings

- `Ged_Games.csv`/`WAS.csv` - WAS games officiated by Gediminas Petraitis, identified as the highest scorer on Method 2, and all WAS games
- `Ayotte_Games.csv`/`NYK.csv` - NYK games officiated by Mark Ayotte, identified as the highest scorer on Method 2, and all NYK games
- `PSM_Results.csv` - Output of propensity score matching results
- `PCA_Results.csv` - Each referee with aggregated stats and 14 principal components and their loadings

## Results

### **Method 1: Points over Expected**



<p align="center">
  <img src="https://i.imgur.com/n3HdVg1.png">
  <br>
  <span style="font-size: 12px;">Top 10 referees by method 1, from <code>metrics.py</code></span>
</p

### **Method 2: Elo Score**



<p align="center">
  <img src="https://i.imgur.com/Wp5WuTQ.png">
  <br>
  <span style="font-size: 12px;">Top 10 referees by method 2, from <code>metrics.py</code></span>
</p

### **Method 3: Principal Component Analysis**



<p align="center">
  <img src="https://i.imgur.com/gE6uQh4.png">
  <br>
  <span style="font-size: 12px;">Referees by principal components from <code>NBA_PCA.R</code> (minimum 50 games officiated)</span>
</p

### **Method 4: Propensity Score Matching**



<p align="center">
  <img src="https://i.imgur.com/dMFkEsF.png">
  <br>
  <span style="font-size: 12px;">Referees with lowest p-values in t-test after propensity score matching, from <code>PSA.py</code></span>
</p