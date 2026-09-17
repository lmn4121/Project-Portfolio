                                              1




Empowered Action: An Infant Mortality Study
          Capstone 2 Final Report


       Landon Nguyen & Alex Nguyen
                DATA 4382
            Dr. Masoud Rostami
                May 4, 2026


---

                                                                                                              2


                                                Introduction
​       Infant mortality rate (IMR) is a crucial health metric that represents the general quality of a
region’s public health infrastructure. Nine states in India make up the Empowered Action Group; these
states were identified as “lagging behind” in terms of public health and are the base problem that this
study aims to understand. More specifically, the goal of this project was to create a model that can
accurately predict the IMR for a given district and, therefore, determine the greatest districtwise factors
contributing to poor public health; this could enable district-specific planning for improving public health
and quality of life. Expanding on the baseline model and initial strategy from Capstone 1, the goal of this
study was to improve model performance via stronger preprocessing and advanced modeling
architectures. Furthermore, this study also aimed to utilize Explainable AI (XAI) to determine the greatest
contributing factors to each district’s predicted IMR and implement XAI into model deployment to create
a tool capable of driving public health solutions.
                                                Background
​       The Infant Mortality Rate (IMR) is widely regarded as one of the most sensitive indicators of a
nation’s social development and the effectiveness of its healthcare delivery systems. In the context of
India, national averages often mask significant regional disparities. To address these inequities, the
Government of India identified the Empowered Action Group (EAG), a collective nine states (including
Bihar, Chhattisgarh, Jharkhand, Madhya Pradesh, Odisha, Rajasthan, Uttar Pradesh, and Uttarakhand) that
have historically lagged in demographic transition and public health outcomes.
​       These regions face unique challenges, including varying levels of literacy, access to maternal
care, and immunization coverage. While state-level policies provide a broad framework, public health
experts emphasize that district-wise analysis is essential for identifying areas that are lacking. By
understanding the specific socioeconomic and clinical drivers within these 284 districts, stakeholders can
transition from generalized health mandates to targeted, evidence-based interventions. Data from the
Annual Health Survey provides the necessary granularity to explore these variables, offering a path to
reduce infant mortality rates through localized public health strategies.
​
                                                Methodology
Data Understanding
​       The dataset used for this project was procured by the Annual Health Survey and shared via
Kaggle. Data was collected from 284 districts across 9 Empowered Action Group states in India: states
identified as “lagging behind” with regards to public health. The dataset was tabular, consisting of 284
rows where each row represented a single district; there were 644 columns, including the target variable,
that were grouped into 26 classifications indicated by a two-letter prefix (AA, BB, etc.). After acquiring


---

                                                                                                                3


the data, the first stage of this project was exploring the dataset for any outstanding properties that could
provide insight or interfere with modeling. The most notable features of the dataset included the target
variable distribution, null value patterns, multicollinearity, and potential data leakage.
​       The target variable for this project was total infant mortality rate (IMR). The total IMR variable
was distributed (see Fig. 1) to identify any potential quirks or outliers.




Figure 1. Distribution of the target variable (total IMR). The mean is marked with a red line, and the
median is marked with a yellow line.
The distribution shows a mostly normal spread, which is further validated by the mean and median being
nearly the same, 55 and 56, respectively. A lack of skewness implied that there should not be any notable
outliers in the target distribution and, therefore, would not be a major issue for modeling.
​       Next, null values were inspected for any peculiar patterns so that a proper strategy could be
developed to handle them. In total, 199 features contained null values. Interestingly, many features
contained the same number of null values, so a missingness matrix was created to identify any potential
patterns within these features (see Fig. 2).




Figure 2. Missingness matrix for features containing 44 null values.


---

                                                                                                            4


The matrix displays a uniform pattern for null values. That is, any feature with the same number of null
values was missing information for the exact same districts. Here, a missingness matrix was shown for
features missing 44 values, but this pattern also exists for features missing 45, 72, 98, etc. values.
​       Additionally, one of the most prominent problems for datasets with high dimensionality is
multicollinearity. One unique property of this dataset was that features were already grouped together into
major classes, indicated by their two-letter prefix. Under the assumption that high correlations would exist
within these groups, heatmaps were created to inspect their interrelationships (see Fig. 3).




Figure 3. Heatmap of features belonging to the AA subgroup.
The heatmap shows numerous hot-spots where high correlation exists between the variables. As such, the
subgroup relationships are used later in handling the multicollinearity problem.
​       Finally, one interesting property of the dataset was that the target variable, total IMR, belonged to
a subgroup that contained other IMR values split by gender and urbanization as well as other mortality
measurements. Therefore, a correlation table was created to inspect the relationships between these
features and the target variable (see Fig. 4)


---

                                                                                                               5




Figure 4. A table of correlations between the target variable and other variables in its subgroups (YY).
Figure 4 shows that some of the features in the same subgroup as the target variable had nearly perfect
correlation with it. As such, these features posed a major data leakage problem.
Data Preprocessing
​       Before proper models could be created, the major quality issues in the dataset needed to be
addressed. The first step taken to prepare the dataset for modeling was handling the data leakage problem.
Data leakage could interfere with any step throughout the project and lead to misleading results.
Therefore, features with more than 70% correlation with the target variable were removed. This included
all of the other IMR features and numerous other mortality measurements.
         After clearing the data leakage problem, null values were handled. The null values posed an
interesting challenge because the limited number of rows and excessive number of features meant that
dropping rows would not be a viable option. Furthermore, the uniform missingness pattern would make it
difficult to impute values based on the features’ relationships.. One notable relationship existed between
the null values and the states. That is, the proportion of null values was different at the state level, and the
distributions of each feature differed between the states. Therefore, missing values for features missing at
most 44 values were imputed with the state median. Features with more than 44 missing values were
removed from the dataset.
        Following null value imputation and removal, the dataset was split into 70/30 train and test sets.
A validation set was not used as there was too little data. A 70/30 split allocated ~200 observations for
training which, with proper feature selection, should be enough to train a working model.
        Next, the state names needed to be encoded and the features needed to be scaled to prevent large
scale features from dominating the predictions. State name was target encoded to avoid adding additional
dimensions to the dataset via one–hot encoding. Then, robust scaling was applied to the dataset. The
dataset contained a mixture of skewed and normally distributed variables, making standard scaling
non-optimal. Furthermore, the high dimensionality of the dataset makes handling skewness for individual


---

                                                                                                              6


variables inefficient. Robust scaling, as the name implies, is robust to outliers; this makes it ideal for
scaling a high dimensional dataset that contains a mixture of skewed and normally distributed variables.
​       Finally, multicollinearity was handled via a two part feature selection. In the first part, the
featureset was split into 20 subsets to separate features with the same prefix (classification); doing this
minimized the impact of multicollinearity on the feature selection process. Forward selection was then
applied to each subgroup individually, and the top features from each group were aggregated; this left 50
remaining features from the original 643. In the second part, agglomerative clustering was applied to the
remaining 50 features, based on the correlation matrix, which resulted in 14 clusters of related features
(see Fig. 5).




Figure 5. The 50 features separated into 14 clusters as a result of the agglomerative clustering.
As seen in Figure 5, each cluster contains similar features and, therefore, can be assigned a fitting identity.
Using PCA, each cluster was then compressed into one component, that is, each cluster became one
feature in the final featureset.
Initial Modeling
​       Originally, the selected models included linear regression and Random Forest. Linear regression
is a standard linear model that uses linear relationships to determine its predictions. Linear regression was
chosen to test the strength of the dataset’s linear relationships and act as a baseline model due to its
simplicity. Random forest is an ensemble of decision trees that recursively partitions the dataset based on
feature values to make a prediction. In opposition to linear regression, Random Forest was chosen to test
the viability of nonlinear relationships and complex model architectures.


---

                                                                                                           7


Figure 6. Comparison of the linear regression baseline and Random Forest.
The evaluation metrics used for this project include R2, adjusted R2, and root mean squared error (RMSE).
R2 represents the proportion of variance in the target variable explained by the predicted values, thus
acting as a form of accuracy. Adjusted R2 is similar but accounts for the dimensionality of the dataset.
RMSE represents the average error of the model and is a standard metric for comparing model
performances. Figure 6 displays two key insights. First, linear regression has a balanced fit (even train and
test performance) but lacks the depth for stronger predictions. Second, Random Forest, a nonlinear model,
makes stronger train predictions, but its complexity leads to overfitting.
Fine-Tuning
​       All tree-based models led to overfitting, so fine-tuning emphasized linear models. Numerous
methods were attempted to boost the performance of the linear regression model, including L1 (Lasso)
and L2 (Ridge) regularization. One notable performance boost came from adaptive boosting (AdaBoost)
using a linear regression model as the based model, which slightly improved the test metrics. The most
notable performance boost came from changing model architectures to a custom artificial neural network
(ANN; see Fig. 7).




Figure 7. Custom artificial neural network architecture.
ANNs are inherently linear as the predictions come from a sum of slopes and biases, and nonlinearity is
integrated via activation functions. The custom ANN was designed to have mostly linear layers with a
single ReLU activation function at the end of the network; this added just enough complexity to surpass
the linear models without overfitting like the tree-based models. Overfitting was accounted for in the
ANN structure using a dropout layer, which forced the network to explore different pathways. This model
trained for 10,000 epochs using mean squared error loss (MSE) and Adam optimization at an initial
learning rate of 0.0005. A step scheduler was used to slow the learning rate to 0.0001 in the second half of


---

                                                                                                            8


training; this slowed the model's learning to prevent it from overfitting. Both optimized models, AdaBoost
and ANN, performed better than the baseline and Random Forest models (see Fig. 8).




Figure 8. Optimized AdaBoost and ANN metrics.
Figure 8 shows the metrics achieved by an adaptive boosted linear regression model and the custom ANN
architecture. Both models achieved an adjusted R2 at or above 0.80. The ANN model performed the best,
being the first model to surpass an adjusted R2 value of 0.85. Furthermore, The ANN was the first model
to have balanced train and test metrics.
Explainable AI (XAI) Analysis
​       Model predictions were interpreted using SHapely Additive exPlanation (SHAP) values, starting
with a global analysis (see Fig. 9), that is, the general impact each feature had on the model’s predictions.




Figure 9. SHAP beeswarm plot for the ANN model.
The SHAP plot shows that the most impactful features were neonatal mortality, death rate, BCG
vaccination coverage, and health check ups; these all align with modern research and expectations. The
SHAP plot also shows how the model perceives the relationship between each feature and the target
variable. Increases in death rate and neonatal mortality clearly increase the predicted IMR. Furthermore, a
greater coverage lacking BCG vaccinations (BCG_No_Vaccination) is also a strong driver of increased
IMR, and vice versa. Thus, the learned relationships for the top three features falls within expectation,
which validates the models predictions. Some features, however, may require further inspection. For
example, the mixed results for general vaccination coverage and the inverse relationship seen for check
ups.


---

                                                                                                              9


Model Deployment
​       The best performing ANN model was deployed via Streamlit. The deployment architecture
consisted of a home page and two model selections: the full ANN model and a smaller ANN-mini model.
The full ANN model is the best performing model from the pipeline. A user can input data (the 50 top
features from the feature selection process and the district name) by either uploading a CSV file or
manually inputting data by following the provided template. Users only need to ensure the data has no
missing values; a preprocessor is built in to handle encoding, scaling, and PCA compression. The
ANN-mini model works similarly, but only requires 14 feature inputs (and the district name) at the cost of
some performance. The mini model also has a single-input option, which provides a separate input bar for
each feature; this is ideal for faster predictions and rough estimates.
​       After inputting data into the model, both models follow a similar workflow. The data is
preprocessed to fit the selected model → the model makes predictions for the inputs (regardless of the
number of inputs) → the deployment app returns a table of the provided district names and the predicted
IMR values. The user is then given a series of optional functions. The first function returns a SHAP
waterfall plot to display how each feature contributed to the final prediction for a selected district. The
second function uses an agentic AI to interpret the SHAP plot and describe how each feature relates to the
predicted IMR to the user (see Fig. 10).




Figure 10. Example of the SHAP waterfall plot and agentic explanation produced by the deployment app.
The last function uses a 3 agent system to combine the SHAP values with a web search to write a targeted
report on how the features are impacting IMR for the specified region and recommend solutions for
reducing IMR and improving public health (see Fig. 11).


---

                                                                         10




Figure 11. Example of the agent report produced by the deployment app.


---

                                                                                                               11


Figure 11 demonstrates the deployment agent’s ability to interpret feature contributions to a given IMR
prediction and use them as a basis for recommending public health improvements.
                                         Challenges and Solutions
​       The first major challenge encountered was the dimensionality of the dataset. With 643 features
and only 284 rows, any models were guaranteed to overfit. Furthermore, with this being a health analytics
dataset, applying PCA and losing the features’ definitions would pose ethical concerns. However, feature
selection, such as forward or backward selection, would suffer due to the multicollinearity in such a large
featureset. To circumvent these issues, a two stage feature selection process was implemented to reduce
the dimensionality while working around the multicollinearity. In the first stage, by splitting the features
into subgroups before forward selection, each subgroup could undergo selection without suffering from
multicollinearity. In the second stage, clustering the remaining 50 features into related groups and
applying PCA to each cluster further reduced the featureset to 14 components that could still be defined
based on the features composing each cluster. Ultimately, this feature selection process enabled models to
learn without severely overfitting.
​       The second major challenge was the limited number of observations. Linear models performed
well, but were limited in depth. Additionally, more complex ensembles struggled with severe overfitting.
ANN posed as an unexpected intermediate, especially since neural networks typically need a lot of data to
perform well. However, ANNs are inherently linear, and a tested ANN architecture with only linear layers
performed the same as a linear regression model. Adding a single ReLU activation function at the end of
the structure, right before the output, gave the model enough nonlinear potential to surpass the linear
regression models, but not so much complexity that the model would always overfit. Furthermore,
including an early dropout layer right after the input integrated regularization to further prevent
overfitting. Lastly, using a scheduler to slow the learning rate in the second half of the training loop and
stopping the training loop early also helped prevent the model from overfitting. Ultimately, the custom
ANN architecture and training structure resulted in a good-fit model that performed better than previous
attempts while remaining balanced.
                                         Key Results and Insights
​       Numerous models were produced, but the most important comparison to be made is between the
baseline model, a tree-based model ensemble (Random Forest), an optimized linear model (AdaBoost),
and the custom ANN model (see Fig. 12)


---

                                                                                                              12


Figure 12. Train and Test comparison tables of the most important models.
From the table, it can be concluded that nonlinear models perform significantly worse than linear models,
which implies that most fluctuations in IMR can be explained through linear relationships. However, the
best performance comes from the ANN model; this implies some level of complexity within the data’s
relationships.
        The global SHAP analysis from before validated the model’s predictions by justifying its most
important learned relationships. However, Looking at the SHAP explanations of individual predictions
reveals some potential inconsistencies (see Fig. 13).




Figure 13. SHAP waterfall plots of an underprediction and an overprediction.
From the overprediction (residual of -14.18) it is clear that the death rate for this district severely inflates
the predicted IMR; this implies the presence of instrumental variables that are inflating the general death
rate but not IMR directly, which interfered with the model’s prediction. The presence of instrumental
variables is an extremely important limiting factor for the model because district–specific variables that
interfere with the relationship between IMR and the predictors can lead to inaccurate results. The SHAP
plot of the underprediction (residual of 10.61) reveals that the district’s state is pushing the model’s
prediction too low. The impact of state on the model’s prediction implies that the district is an outlier
within its state and an issue may exist at the state-wise level. The potential of a state-level issue is
problematic because it may not be properly captured in this districtwise dataset and study.
                                        Conclusion and Future Work
​       In conclusion, the purpose of this project was to produce a model that could predict districtwise
IMR and identify pressing issues in a region’s public health. The greatest contributions to the models
success were the two stage feature selection process that reduced the featureset from 643 original
variables to 14 definable components and the custom ANN architecture that enabled a strong combination
of linear and nonlinear learning. Furthermore, a successful deployment app was created to combine the


---

                                                                                                           13


predictive model with XAI and agentic AI to both produce an IMR prediction and use the prediction’s
contributing factors to identify district-specific public health problems and recommend potential
solutions.
​       The greatest limitation to this project was the number of observations. Having only 284 severely
restricted the learning potential of the models. Furthermore, because the number of rows was far exceeded
by the number of features, the vast majority of features could not be used to prevent overfitting.
Therefore, future work should emphasize collecting more data. Expanding the collection of data to span
more states would not only increase the size of the dataset and quality of the models, but it would also
expand the applicable range of the model’s deployment.


---

