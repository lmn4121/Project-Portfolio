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
**Target Variable Distribution** /
- The target variable (total IMR) was normally distributed with a mean and median ~55
  - This implied that there shouldn't be a major outlier problem within the target variable
<img src="https://github.com/lmn4121/Project-Portfolio/blob/Capstone-Project/images/target_distribution.png" width=70%>

**Multicolinearity:**
- High multicollinearity exists between features with the same prefix label
   - This displayed a necessity for reducing dimensionality
- The heatmap below displays the correlation between variables with the AA prefix
  - Numerous white and light red spots indicate high correlation
<img src="https://github.com/lmn4121/Project-Portfolio/blob/Capstone-Project/images/AA_heatmap.png" width=70%>

**Null Values**
- Many features were missing information for the same districts
- The missingness matrix below shows uniform missingness across numerous features
  - This makes it hard to impute values based on the relationships between features
  - Furthermore, there are not enough rows to justify dropping them
<img src="https://github.com/lmn4121/Project-Portfolio/blob/Capstone-Project/images/msno_44.png">

**Data Leakage**
- From the multicollinearity problem above, it makes sense that their would be features that share the same prefix /
  as the target variable and are, therefore, highly correlated with the target variable
- The table below shows the top 10 features based on correlation with total IMR
  - Numerous other IMR and infant death features can be identified, which have near perfect correlation with the target variable
  - This presented a data leakage problem
<img src="https://github.com/lmn4121/Project-Portfolio/blob/Capstone-Project/images/target_correlations.png" width=50%>

## Data Preprocessing
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
