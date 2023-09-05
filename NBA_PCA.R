install.packages("knitr")
library(knitr)

# Load the data
data_for_pca <- read.csv('/Users/blakelaw/Library/CloudStorage/OneDrive-Personal/PycharmProjects/NBA/PCA.csv', header = TRUE)

# Exclude the unnecessary columns for PCA including the "Unnamed: 0" and "x" columns
data_pca_only <- data_for_pca[, !(names(data_for_pca) %in% c('Unnamed: 0', 'first_name', 'last_name', 'official_id', 'num_games', 'X'))]

# Perform PCA
pca_result <- prcomp(data_pca_only, scale. = TRUE, center = TRUE)

# Extract the scores for each principal component
scores <- pca_result$x

# Append the PC scores to the original dataframe
data_with_scores <- cbind(data_for_pca, scores)


# If you wish to save the dataframe with normalized scores:
write.csv(data_with_scores, '/Users/blakelaw/Library/CloudStorage/OneDrive-Personal/PycharmProjects/NBA/PCA_results.csv', row.names = FALSE)

# Print the loadings to understand the weightings for each principal component
print(pca_result$rotation)

print(data_with_scores)

rounded_rotation <- round(pca_result$rotation, 3)
table_output <- kable(rounded_rotation, format = "html", caption = "PCA Loadings")
writeLines(table_output, "/Users/blakelaw/Downloads/my_table.html")




