# Online Shoppers Purchasing Intention

## Dataset Overview

The **Online Shoppers Purchasing Intention** dataset contains browsing session records collected from an e-commerce website. Each row represents a single user session, and the goal is to predict whether that session ended in a purchase (`Revenue = TRUE`) or not (`Revenue = FALSE`).

- **Source:** Sakar, C.O. et al. (2019). *Real-time prediction of online shoppers' purchasing intention using multilayer perceptron and LSTM recurrent neural networks.* Neural Computing and Applications, Vol. 31, pp. 6893–6908. [doi:10.1007/s00521-018-3523-0](https://doi.org/10.1007/s00521-018-3523-0)
- **Instances:** 12,330 sessions
- **Features:** 17 input features + 1 binary target (`Revenue`)
- **Class distribution:** 10,422 negative sessions (84.5%) and 1,908 positive sessions (15.5%)
- **Collection design:** Each session belongs to a **distinct user** over a 1-year period, deliberately constructed to avoid bias toward any specific campaign, special day, user profile, or time period.

---

## Features

### Page Interaction Features (Numeric)
| Feature | Type | Description |
|---|---|---|
| `Administrative` | int | Number of administrative pages visited in the session |
| `Administrative_Duration` | float | Total time (sec) spent on administrative pages |
| `Informational` | int | Number of informational pages visited in the session |
| `Informational_Duration` | float | Total time (sec) spent on informational pages |
| `ProductRelated` | int | Number of product-related pages visited in the session |
| `ProductRelated_Duration` | float | Total time (sec) spent on product-related pages |

> Page type classification is derived from the URL information of each page and updated in real time as the visitor navigates.

### Google Analytics Metrics (Numeric)
| Feature | Type | Description |
|---|---|---|
| `BounceRates` | float | Average bounce rate across pages visited — the percentage of visitors who enter the site from a page and leave without triggering any further requests |
| `ExitRates` | float | Average exit rate across pages visited — for each page, the percentage of all pageviews that were the last in the session |
| `PageValues` | float | Average Google Analytics "Page Value" of pages visited before completing a transaction; a natural proxy for purchase intent (ranked #1 by all feature selection methods in the original study) |
| `SpecialDay` | float | Closeness of the session to a special commercial day (e.g., Valentine's Day, Mother's Day); takes a non-zero value in the days approaching the holiday and reaches a maximum of 1 on the day itself |

### Session Context Features (Categorical / Ordinal)
| Feature | Type | Description |
|---|---|---|
| `Month` | categorical | Month of the session (Feb–Dec; January is absent from the data) |
| `OperatingSystems` | int (nominal) | Operating system used (integer-encoded) |
| `Browser` | int (nominal) | Browser used (integer-encoded) |
| `Region` | int (nominal) | Geographic region of the user (integer-encoded) |
| `TrafficType` | int (nominal) | Traffic source / referral channel (integer-encoded; 20 distinct types) |
| `VisitorType` | categorical | `Returning_Visitor`, `New_Visitor`, or `Other` |
| `Weekend` | bool | Whether the session occurred on a weekend |

### Target
| Feature | Type | Description |
|---|---|---|
| `Revenue` | bool | Whether the session resulted in a purchase (TRUE) or not (FALSE) |

---

## Research Questions

This project uses the dataset to investigate the following questions:

1. **Which browsing behaviors are the strongest predictors of purchase intent?**
2. **Can we build a reliable classifier to flag high-intent sessions in real time?**
3. **Does visitor type (new vs. returning) meaningfully affect purchasing behavior?**
4. **Are there natural groupings of user sessions that reveal distinct shopping personas?**
5. **How does seasonality (month, special day, weekend) influence purchase probability?**

---

## Analytical Approach & ML Methods

The analysis is structured as a progression from exploratory work through unsupervised discovery to supervised prediction, with careful attention to model selection and evaluation throughout.

### 1. Exploratory Data Analysis
Before modelling, we characterise the data: distributions of page interaction times, the 84.5% / 15.5% class split in `Revenue`, correlation structure among numeric features, and frequency profiles across categorical variables (month, visitor type, traffic source). The significant right-skew in duration features and the near-zero distribution of `PageValues` for most sessions (reflecting that only a minority of pages contribute to transactions) are noted for later preprocessing. The strong pairwise correlation between `BounceRates` and `ExitRates` — noted in the original paper as a source of redundancy — is examined as motivation for both PCA and Lasso.

---

### 2. Unsupervised Learning — Understanding the Data

#### Principal Component Analysis (PCA)
The ten numeric features span correlated subspaces (e.g., `BounceRates`/`ExitRates` are strongly correlated; page count and duration pairs move together). PCA reduces this to a small number of interpretable components, visualises session spread in 2D, and diagnoses multicollinearity before regression. The proportion of variance explained by each component informs feature engineering.

#### K-means & Hierarchical Clustering
Ignoring the `Revenue` label, clustering discovers natural visitor personas — for example, a "window shopper" cluster (high page counts, zero purchases), a "high-intent" cluster (elevated `PageValues`, low bounce), and a "one-and-done" cluster (high bounce rates). Results are validated with silhouette scores and compared across cluster counts. Hierarchical clustering (Ward linkage) provides a dendrogram to reason about the number of natural groups.

---

### 3. Supervised Learning — Predicting Purchase Intent

#### Baseline: Logistic Regression & Classification
Logistic regression provides an interpretable probabilistic baseline. Given the class imbalance (~15.5% positive), we apply class weighting and evaluate with AUC-ROC and F1 rather than raw accuracy. Coefficients directly quantify the log-odds contribution of each feature, providing a transparent answer to Research Question 1.

#### Discriminant Analysis (LDA / QDA)
Linear Discriminant Analysis assumes Gaussian class-conditional distributions and equal covariance, while QDA relaxes the latter. Both are applied as low-parameter alternatives to logistic regression; LDA also serves as a dimensionality-reduction step, projecting sessions onto the axis of maximum class separability.

#### Shrinkage Methods: Ridge Regression & Lasso
With 17+ features (after encoding categoricals, the design matrix expands), regularisation is essential. **Lasso** performs automatic feature selection — shrinking irrelevant features to exactly zero — directly answering which variables matter most. **Ridge** retains all features but shrinks correlated predictors together, offering stability. Both are tuned via cross-validated lambda grids.

#### K-Nearest Neighbors (KNN)
KNN is applied as a non-parametric reference point. Notably, the original paper explicitly excluded KNN from their real-time system on the grounds that it is a **lazy-learning algorithm** — it defers all computation to inference time, making it impractical for real-time session scoring. This provides a natural motivator for discussing the **curse of dimensionality**: with many features (including one-hot-encoded categoricals), Euclidean distance becomes less meaningful and KNN performance degrades. PCA-reduced feature spaces partially mitigate this, illustrating the interplay between dimensionality reduction and distance-based methods.

#### Decision Trees & Ensemble Methods
A single decision tree (analogous to the C4.5 algorithm used in the original study) gives a fully interpretable model with natural handling of categorical features. The original paper found that while C4.5 achieved high raw accuracy, it suffered from class imbalance — defaulting to predicting the majority (non-purchase) class and yielding a low F1 score. This motivates **Random Forests** (bagging with random feature subsets) and **Gradient Boosted Trees**, which the original paper found to be stronger. Variable importance scores from Random Forest provide a non-linear counterpart to Lasso's feature selection. The original paper found `PageValues`, `ExitRates`, and `BounceRates` consistently at the top of feature rankings — we expect our tree-based importance scores to replicate this finding.

> **Class imbalance handling:** Following the original paper's approach, we apply **oversampling** of the minority (purchase) class on the training partition only — never on the held-out test set — to avoid data leakage.

#### Support Vector Machines (SVM) & Kernel Trick
SVMs with both **linear** and **RBF kernels** are fitted. The original paper observed that while linear SVM achieved higher raw accuracy than RBF SVM on the imbalanced dataset, the RBF kernel produced more balanced true-positive/true-negative rates — a concrete illustration of why accuracy alone is a misleading metric under class imbalance. After oversampling, RBF SVM significantly outperformed the linear variant. The margin-based objective is robust to outliers; the regularisation parameter `C` controls the bias-variance trade-off directly.

---

### 4. Model Selection & Evaluation

#### Bias-Variance Trade-off
The progression from logistic regression → regularised regression → decision tree → random forest → gradient boosting illustrates the bias-variance trade-off concretely. Overfitting in deep trees versus underfitting in a shallow logistic model is visualised through learning curves.

#### Resampling Methods: Cross-Validation & Bootstrap
All models are evaluated with **stratified k-fold cross-validation** (k=5 or 10) to account for class imbalance and prevent data leakage. The **bootstrap** is used to produce confidence intervals for key metrics (AUC, F1) and to estimate the variance of feature importance scores from tree ensembles. The original paper repeated a 70/30 train/test split 100 times and used a t-test to compare classifier performance — we use cross-validation as a more data-efficient equivalent.

> **Benchmark from original paper (with oversampling):** Decision Tree: ~85% accuracy, F1 ≈ 0.84; SVM (RBF): ~86% accuracy, F1 ≈ 0.85; MLP: ~87% accuracy, F1 ≈ 0.86. Our traditional ML methods should be evaluated against this baseline.

#### Linear Regression & Model Selection (supplementary)
Although `Revenue` is binary, **linear probability models** are fitted as a pedagogical reference. More practically, `PageValues` and session duration can be modelled as continuous targets to understand what drives engagement depth, using forward/backward stepwise selection and information-criterion (AIC/BIC) comparisons.

---

## Summary of Methods vs. Research Questions

| Research Question | Primary Methods |
|---|---|
| Which features predict purchase? | Lasso, Random Forest importance, Logistic Regression coefficients |
| Build a reliable purchase classifier | Logistic Regression, SVM, Gradient Boosting + CV evaluation |
| New vs. returning visitor effects | LDA, Logistic Regression (interaction terms), Clustering |
| Natural session groupings / personas | K-means, Hierarchical Clustering, PCA |
| Seasonality effects | Logistic Regression with month/weekend features, Decision Trees |

---

## Repository Structure

```
.
├── README.md                  # This file
├── online_shoppers_intention.csv
├── eda.py                     # EDA script using ydata-profiling
├── eda_report.html            # Generated profiling report
└── s00521-018-3523-0.pdf      # Original paper describing the dataset
```

---

## Requirements

```
pandas
ydata-profiling
```

Install with:
```bash
pip install pandas ydata-profiling
```
