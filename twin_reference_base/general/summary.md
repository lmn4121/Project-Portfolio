# Project Portfolio

Collection of projects by **Landon Nguyen** — Data Scientist / AI Engineering.

## About

I’m a data science student at **The University of Texas at Arlington** in the Fastrack program (**B.S. Data Science** with a Biology concentration and Mathematics minor; **M.S. Applied Statistics and Data Science**, expected **December 2027**; GPA **3.9**).

I have about **6 years** of programming experience and **2 years** applying statistical, data mining, and machine learning methods to research and data-driven problems. I’m especially interested in combining **AI engineering** with data science to build intelligent and autonomous systems.

**Core toolkit (from resume):** Python, SQL, R, SAS; NumPy/Pandas/scikit-learn; TensorFlow/Keras and PyTorch; LLMs, RAG, and agent tooling.

**Resume:** [Landon_Nguyen_Resume.pdf](./Landon_Nguyen_Resume.pdf)  
(Contact details are in the PDF.)

## How this repo is organized

Each project lives on its **own branch** with its own README focused on techniques and results. Browse a branch to see the full write-up and code.

## Projects

### [Capstone-Project](https://github.com/lmn4121/Project-Portfolio/tree/Capstone-Project) — Infant Mortality Rate Study
Undergraduate capstone (**DATA-4332**): predict infant mortality rate (IMR) for districts in India’s Empowered Action Group states using Annual Health Survey indicators.

**Techniques:** EDA (leakage, multicollinearity, missingness), state-wise imputation, robust scaling, forward selection + agglomerative clustering/PCA (643 → 50 → 14 features), linear and tree baselines, final **ANN**, SHAP explainability, Streamlit deployment with XAI + agentic interpretation.

**Results:** Best ANN about **R² 0.86** and **RMSE 5.1** (train; test R² ~0.87).

### [Kaggle-Project](https://github.com/lmn4121/Project-Portfolio/tree/Kaggle-Project) — Metastatic Cancer Diagnosis
WiDS Datathon 2024 Challenge 1: binary classification of whether a patient received a metastatic cancer diagnosis within 90 days of screening.

**Techniques:** Feature filtering, mode imputation, one-hot encoding, simple neural net, AdaBoost, and gradient boosting with GridSearchCV.

**Results:** ~**80%** validation accuracy; Kaggle private/public scores **0.789** / **0.798**. Best among compared models: boosted gradient ensemble.

### [Data4380-Computer-Vision](https://github.com/lmn4121/Project-Portfolio/tree/Data4380-Computer-Vision) — Chest X-Ray Classification
**DATA 4380** computer vision project: classify chest X-rays as **COVID-19**, **Normal**, or **Viral Pneumonia** ([Kaggle dataset](https://www.kaggle.com/datasets/pranavraikokte/covid19-image-dataset)).

**Techniques:** Baselines (ANN/CNN), CLAHE and augmentation, frozen VGG16 exploration, final fine-tuned **DenseNet201** with class weights.

**Results:** Final model **validation macro F1 0.92**, **test macro F1 0.83** (written report). Branch also includes the course report and presentation PDFs.
