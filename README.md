# Online Shoppers Purchase Intent

Statistical learning project predicting whether an e-commerce browsing session ends in a purchase.

## Summary

This project uses the UCI Online Shoppers Purchasing Intention dataset to model purchase intent from user-session behavior. The dataset contains page interaction metrics, Google Analytics features, session context, and technical profile variables for online shopping visits.

The analysis combines exploratory data analysis, unsupervised clustering, dimensionality reduction, and supervised classification to answer a practical question: which session behaviors are most predictive of conversion?

## Dataset

- Source: UCI Online Shoppers Purchasing Intention dataset
- Observations: 12,330 browsing sessions
- Predictors: 17 input variables
- Target: `Revenue` indicating whether a session ended in purchase
- Class balance: 15.5% purchase sessions, 84.5% non-purchase sessions

## Methods

- Exploratory data analysis of numeric and categorical session features
- PCA for dimensionality reduction and multicollinearity diagnostics
- K-means and hierarchical clustering for visitor-behavior segmentation
- Logistic regression, Lasso, Ridge, and Elastic Net baselines
- LDA and KNN classifiers
- Random Forest and Gradient Boosted Trees
- ROC/AUC, accuracy, sensitivity, specificity, and F1 evaluation

## Key Findings

- `PageValues` was the dominant predictor across tree-based feature-importance measures.
- Gradient Boosted Trees achieved the strongest overall AUC among evaluated models.
- Tree ensembles outperformed simpler classifiers by capturing nonlinear interactions in mixed numeric/categorical features.
- Class imbalance remained the central deployment challenge; threshold tuning or resampling would be needed for real-time flagging.

## Tech Stack

- R / R Markdown
- caret
- glmnet
- randomForest
- gbm
- pROC
- MASS / class / e1071

## Repository Layout

```text
STAT432_Final_Project.Rmd   Full reproducible analysis
STAT432_Final_Project.pdf   Rendered project report
online_shoppers_intention.csv Dataset used for modeling
other/                      Dataset notes, EDA utilities, original paper
```

## Reproduce

Open `STAT432_Final_Project.Rmd` in RStudio and render the document after installing the required R packages.

```r
install.packages(c("tidyverse", "caret", "glmnet", "pROC", "randomForest", "gbm", "MASS", "class", "e1071", "cluster"))
```
