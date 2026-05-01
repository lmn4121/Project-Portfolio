# Empowered Action: Infant Mortality Rate Study
## The Problem
According to the Annual Health Survey in India, 9 states were identified as "lagging behind" in terms of public health. Infant Mortality Rate (IMR) is a key represetation of the public health for a given region. Thus, the problem was to identify the greatest influences over IMR. \
**Why this matters:** Identifying the contributing factors to IMR can help develop district-specific plan for improving public health and reducing infant deaths.

## Project Overview
**Goal:** 
- Identify key contributors to IMR
- Develop a model that can use indentified features to predict IMR

**Approach:**
- Explore relationships between the features and the target variable
- Preprocess the data
  - Handle missing values
  - Encode categorical features
  - Scale the data
- Develop a preprocessing pipeline to reduce dimensionality while retaining feature identities
- Develop a predictive model
- Deploy the model
  - Incorporate Explainable AI and Agentic AI for interpretation and transparency

**Key Results:**
- Produced a model with 86% R<sup>2</sup> and 5.1 RMSE
- Identified key features with clear a clear influence on IMR
  - Reduced necessary features from 640 to 50 for a full mode or 14 for a smaller model
- Developed a deployment app that can make and interpret predictions to develop a solution for reducing IMR.

## Data
**Source:** This data was sourced from [Kaggle](https://www.kaggle.com/datasets/rajanand/key-indicators-of-annual-health-survey) 

**Type and Shape:**
- This data is tabular
- There are 284 rows where each row represents a district in India
- There are 643 features excluding the target variable
  - Each feature belongs to one of 26 classifications, indicated by a two letter prefix (AA, BB, etc.)

**Key Features:**


## Key Exploratory Data Analysis (EDA)
**Target Variable Distribution:** /
- The target variable (total IMR) was normally distributed with a mean and median ~55
  - This implied that there shouldn't be a major outlier problem within the target variable
<img src="https://github.com/lmn4121/Project-Portfolio/blob/Capstone-Project/images/target_distribution.png" width=50%>

**Multicolinearity:**
- High multicollinearity exists between features with the same prefix label
   - This displayed a necessity for reducing dimensionality
- The heatmap below displays the correlation between variables with the AA prefix
  - Numerous white and light red spots indicate high correlation
<img src="https://github.com/lmn4121/Project-Portfolio/blob/Capstone-Project/images/AA_heatmap.png" width=70%>

**Null Values:**
- Many features were missing information for the same districts
- The missingness matrix below shows uniform missingness across numerous features
  - This makes it hard to impute values based on the relationships between features
  - Furthermore, there are not enough rows to justify dropping them
<img src="https://github.com/lmn4121/Project-Portfolio/blob/Capstone-Project/images/msno_44.png">

**Data Leakage:**
- From the multicollinearity problem above, it makes sense that their would be features that share the same prefix 
  as the target variable and are, therefore, highly correlated with the target variable
- The table below shows the top 10 features based on correlation with total IMR
  - Numerous other IMR and infant death features can be identified, which have near perfect correlation with the target variable
  - This presented a data leakage problem
<img src="https://github.com/lmn4121/Project-Portfolio/blob/Capstone-Project/images/target_correlations.png" width=50%>

## Data Preprocessing
**Null Values:**
- From EDA, it was identified that missing values had a peculiar pattern
- There are not enough rows to justify dropping null values row-wise
- Because features are missing information for the same rows, imputation cannot be based on feature relationships
- The only usuable relationship that could be identified was state-wise
- Strategy:
  - Remove features with more than 70 missing values
  - Impute the remaining features with state-wise medians
 
**Data Leakage:**
- Features with more than 0.7 correlation with the target variable were dropped
  - This removed all mortality variables that posed a data leakage problem

**Encoding:**
- There were Only two categorical variables in the dataset:
  - District names: removed because they were essentially row indices
  - State names: Target encoded
    - Wanted to retain the state variable due to its value
    - Wanted to prevent increasing the dimensionality of the dataset with one-hot encoding
    - States did not have an inherent order, so target encoding was the best option

**Scaling:**
- Features were on vastly different scales
- Standard scaling is sensitive to skewness and outliers
  - Too many features to individually inspect for correcting skewness
- Robust scaling is used instead
  - This is a scaling method that is robust to outliers

**Outliers:**
- The target variable was normally distributed, and did not have a notable outlier problem
- Few specific districts appeared that significantly deviated from relationships present between the features
  and the target variable
  - These districtrs were identifiable due to being outliers in the residual distributions during modeling
  - These handfull of districts were removed
 
**Feature Selection:**
- Due to the high dimensionality and extreme imbalance between rows and columns, feature selection
  was the most crucial aspect of the project
- Feature selection was split into a two part strategy:

*Part 1:*
In order to retain feature identities, we wanted to avoid PCA at the start, however, the multicollinearity identified in EDA would pose a challange for feature selection.
- To avoid the multicollinearity issue, the featureset was split into 20 subgroups
  - Because most multicollinearity existed between features with the same prefix (AA, BB, etc.), each group
    was made to minimize the number of features with the same prefix.
- After splitting the features into groups, forward selection was run on each group individually, and the
  top features from each group were aggregated back into a full featureset
- The forward selection process reduced the featureset to 50 features

*Part 2:*
- Numerous strategies were attempted, but the most successful strategy was a combination of agglomerative clustering and PCA.
- After the forward selection method, the remaining 50 featues retained their multicollinearity
- Agglomerative clustering was used to cluster related features together based on the correlation matrix
  - Result: 14 clusters of related features
- PCA models were then used on each individual cluster to compress them down into single components
  - Each cluster became one principal component
  - Because the features in each cluster were known, each component could be assigned an identity based on
    the features that contributed to it

*End Result:*
- 14 components that made up the featureset
- In other words, the featureset was reduced from 643 &rarr 50 &rarr 14

## Modeling Approach
## Model Training
## Results
## Model Interpretation
## Key Insights
## Conclusion
## Future Work
## How to Run
## Repository Structure
## Requirements
