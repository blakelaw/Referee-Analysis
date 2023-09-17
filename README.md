# NBA Referee Neutrality Investigation

[![Blog Article](https://img.shields.io/badge/blog-article-brightgreen?link=https%3A%2F%2Fblakelaw.github.io%2Fprojects%2F1_project%2F)](https://blakelaw.github.io/projects/1_project/)

## Description

This project investigates the neutrality of referees in approximately 64,000 NBA games. This is primarily written in Python, with the PCA completed in R.

## Features
  
- **Quantitative Analysis**: Developed four quantitative approaches to evaluate the impact of referees on game metrics and results. 
- Points over expected: For a given referee-team combination, the difference in average score when the game was officiated by the referee and the overall average
- Elo score: Points over expected, but takes the average within the same year
- Principal component analysis: Adds 14 features to points, including: assists, steals, blocks, free throw percentage. Each of these features is reduced to two principal components, and the largest deviations in either direction have a higher score
- Propensity score matching: Ran logistic regression to generate propensity scores for every referee in a given game, based on the home team win percentage, away team win percentage, and the time the game occurred. Matched every game to another game (excluding those officiated by the same referee), and conducted a t-test on 86 experienced referees

- **Visualization**: Created visualizations for each metric with Tableau and Datawrapper. See blog post.

- **Results**: The analysis did not find any evidence pointing towards a systemic bias on the part of the referees.

## Usage

`metrics.py`
- contains points over expected and elo metrics

`PCA.py`
- preprocesses dataset for PCA in R

`NBA_PCA_R`
- PCA analysis in R

`PSM.py`
- propensity score matching on dataset

`Outputs`
- Contains all outputs for visualization and PCA loadings


