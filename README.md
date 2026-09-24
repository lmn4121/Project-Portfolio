# Project Portfolio

Collection of projects by **Landon Nguyen** — Data Scientist / AI Engineering.

## About

I’m a data science student at **The University of Texas at Arlington** in the Fastrack dual-track program (**B.S. Data Science** with a Biology concentration and Mathematics minor; **M.S. Applied Statistics and Data Science**, expected **December 2027**; GPA **3.9**).

I have about **6 years** of programming experience and **3 years** applying statistics and machine learning to data-driven problems. I build and deploy ML and LLM applications, from explainable neural networks to RAG systems and AI agents.

**Coursework (current / upcoming):** Statistical Analysis with SAS; Linear Algebra and Statistics with R; Advanced Regression Analysis; Machine Learning Applications; Data Mining with Information Visualization.

**Self-study & planned focus:** LLM engineering (RAG, QLoRA, Hugging Face); agentic AI (Agents SDK, CrewAI, LangGraph, MCP, Guardrails); AI in production (AWS Bedrock, Terraform, CI/CD, LangFuse); Azure Databricks, PySpark, Delta Lake.

**Certifications:** IBM Machine Learning with Python; IBM Machine Learning Methodology; PyTorch for Deep Learning.

**Core toolkit (from resume):** Python, SQL, R, SAS; NumPy/Pandas/SciPy/scikit-learn; TensorFlow/Keras and PyTorch; SHAP, OpenAI APIs / Agents SDK, RAG; ChromaDB, Streamlit, Gradio, Render; Git/GitHub.

**Resume:** [Landon_Nguyen_Resume.pdf](./Landon_Nguyen_Resume.pdf)  
(Contact details are in the PDF.)

## How this repo is organized

Each project lives on its **own branch** with its own README focused on techniques and results. Browse a branch to see the full write-up and code.

## Projects

### [Capstone-Project](https://github.com/lmn4121/Project-Portfolio/tree/Capstone-Project) — Infant Mortality Rate Study
Undergraduate capstone (**DATA-4381 & DATA-4382**): predict infant mortality rate (IMR) for districts in India’s Empowered Action Group states using Annual Health Survey indicators.

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

### [Digital-Twin](https://github.com/lmn4121/Project-Portfolio/tree/Digital-Twin) — Resume Chatbot
Conversational digital twin that answers questions about background, skills, and experience using the resume plus a project knowledge base.

**Techniques:** LLM-assisted semantic chunking into Chroma (`ingest.py`); OpenAI Agents SDK twin with RAG, email capture, and unknown-question tools (`twin.py`); Gradio streaming chat UI (`app.py`); deployed on **Render** and embedded in the portfolio as a chat widget (API key kept server-side).

**Results:** End-to-end twin chatbot with retrieval-grounded answers and tools to record leads / unanswered questions instead of inventing replies. Branch includes `requirements.txt` and a prebuilt `twin_db/` vector store.
