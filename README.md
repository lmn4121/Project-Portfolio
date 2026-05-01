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
- In order to retain feature identities, we wanted to avoid PCA at the start, however, the multicollinearity identified in EDA would    pose a challange for feature selection.
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
- In summary, the featureset was reduced from 643 &rarr; 50 &rarr; 14

## Modeling Approach
- Numerous models were attempted, including linear models, tree-based models, and an artificial neural network (ANN)
- ANN was the strongest and finalized approach, but was based on the failures of linear and tree-based models.
- *Linear models:*
  - Due to the linear relationship present in the dataset, linear models proved to be proficient with both good accuracy
    and a balanced fit
  - However, linear models are simple and lack depth for stronger learning
- *Tree models:*
  - Tree models were attempted to search for nonlinear relationships
  - Every tree model, even at low complexity, was overfitting
- *ANN: The final approach*
  - ANN models are inherently linear as each layer is a sum of slopes and biases
  - Nonlinearity can be added via activation functions
  - Strategy:
    - Create a mostly linear ANN with a single activation function before the output layer
    - This adds enough comlexity to overcome the training plateaus experienced by the linear models
      without overfitting to the same extent as the tree-based models
  - Structure:
    - 1 input layer
    - 1 20% dropout layer (regularization: force the model to explore different pathways and options)
    - 3 hidden layers
    - 1 ReLU activation layer (adds nonlinearity)
    - 1 output layer

## Model Training
**Strongest Linear Model:**
- Adaptive Boosting
  - 100 estimators
  - learning rate: 0.001
  - Base model: Standard Linear Regression
 
**Strongest Tree Model:**
- Random Forest
  - Max depth: 3
  - Number of estimators: 10

**ANN Training Structure:**
- Loss Functions: MSE
- Optimizer: ADAM
  - starting learning rate of 0.0005
  - learning rate reduced to 0.0001 on the 5,000th epoch using a step scheduler
- Total Epochs: 10,000

## Results
**Evaluation Metrics:**
- R<sup>2</sup>
  - Target variance explained by the model
  - Acts as a general accuracy
- Adjusted R<sup>2</sup>:
  - Similar to R<sup>2</sup>, but accounts for dimensionality
- Root Mean Squared Error:
  - Average prediction error
  - Allows for better comparison between models
  - Scale of IMR is from 0-100
  - Average IMR for this data is ~56
 
*Additional Model: ANN Mini:*
- Shares the same structure and training setup as the full ANN model
- Instead of using the 14 clusters compressed into components,
  it uses the single best feature from every cluster (based on correlation)
- In summary, ANN mini uses 14 features that retain their original identities inseaad of
  50 features compressed into components
  - Only requires 14 inputs instead of 50


**Train Results**
| Model | R<sup>2</sup> | Adjusted R<sup>2</sup> | RMSE |
|-------|---------------|------------------------|------|
| ANN | 0.86 | 0.85 | 5.1  |
| ANN Mini | 0.84 | 0.82 | 5.5 |
| AdaBoost Linear Model| 0.83 | 0.81 | 5.7 |
| Random Forest | 0.80 | 0.78 | 6.2 |

**Test Results**
| Model | R<sup>2</sup> | Adjusted R<sup>2</sup> | RMSE |
|-------|---------------|------------------------|------|
| ANN | 0.87 | 0.85 | 5.1  |
| ANN Mini | 0.84 | 0.80 | 5.8 |
| AdaBoost Linear Model| 0.84 | 0.80 | 5.8 |
| Random Forest | 0.71 | 0.65 | 7.7 |

## Model Interpretation
**Global Explanation:**
- Using SHapely Additive exPlanations (SHAP), each features impact on the predictions can be interpreted
- The feature importance is similar across all models, so here we emphasize the ANN results
- Below is a SHAP beeswarm plot
  - Each feature is listed with a summary of its impact on the model's predictions
  - From the plot, Neo Natal Mortality, Death Rate, BCG vaccination coverage, check ups, and state name
    have the biggest impact on Infant Mortality Rate
  - There is also contribution from features related to population density and government assistance
- The general feature impacts align with research and expectation, which validates the models learned relationships
 <img src="https://github.com/lmn4121/Project-Portfolio/blob/Capstone-Project/images/ann_beeswarm.png" width=50%>

 **Local Explanation:**

## Key Insights
**What Worked?**
*Feature Selection:*
- The most impactful stage of this project
- Splitting the features into groups and applying forward selection allowed for:
  - reducing the featureset to 50
  - retaining the feature identities
  - minimizing the impact of multicollinearity
- Agglomerative clustering + PCA:
  - further reduced the features to 14 components
  - each component retains a definition based on the features used to create it (clusters)
*ANN:*
- Combined the strengths of linear and nonlinear models while minimizing their weaknesses
  - One activation function allowed the model to learn more than linear models
    without overfitting in the same way as tree-based models

**Application:**
- IMR acts as a representation of a regions general public health
- Monitoring how the given features impact IMR can drive decisions on how to best improve a regions public health
  - Because the data is district-wise, predictions can provide insight on district=specific solutions
- In the deployment app, combining prediction SHAP analysis with agentic websearching and interpretation can provide
  a district-specific explanation on what influences IMR and suggestions on how to lower it, thus improving public health.

## Conclusion
## Future Work
## How to Run
## Repository Structure
## Requirements
