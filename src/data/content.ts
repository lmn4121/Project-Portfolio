export const site = {
  name: "Landon Nguyen",
  title: "Data Scientist | AI Engineering",
  email: "lmnguyen420@gmail.com",
  phone: "(972) 632-6912",
  location: "Little Elm, TX",
  github: "https://github.com/lmn4121/Project-Portfolio",
  resumePath: "/Landon_Nguyen_Resume.pdf",
  summary:
    "Data science student with 6 years of programming experience and 2 years applying statistical, data mining, and machine learning methods to research and data-driven problems. Combining AI engineering with data science to build intelligent and autonomous systems.",
};

export const education = {
  school: "The University of Texas at Arlington",
  location: "Arlington, TX",
  expected: "December 2027",
  program:
    "Fastrack M.S. Applied Statistics and Data Science | B.S. Data Science | Biology Concentration | Minor in Mathematics",
  gpa: "3.9",
  currentCoursework: [
    "Statistical Analysis with SAS",
    "Linear Algebra and Statistics with R",
  ],
  upcomingCoursework: [
    "Advanced Regression Analysis",
    "Machine Learning Applications",
    "Data Mining with Information Visualization",
  ],
  certifications: [
    "IBM Machine Learning with Python",
    "IBM Machine Learning Methodology",
    "PyTorch for Deep Learning",
  ],
};

export const skills = [
  {
    label: "Languages",
    items: ["Python", "SQL", "R", "SAS"],
  },
  {
    label: "Data Science",
    items: [
      "NumPy",
      "Pandas",
      "SciPy",
      "scikit-learn",
      "imbalanced-learn",
      "Statsmodels",
      "Matplotlib",
      "Seaborn",
      "Tableau",
    ],
  },
  {
    label: "Machine Learning",
    items: [
      "Regression",
      "Classification",
      "Ensemble Methods",
      "Dimensionality Reduction",
      "Feature Selection",
      "Imbalance Handling",
    ],
  },
  {
    label: "Deep Learning & AI",
    items: [
      "TensorFlow/Keras",
      "PyTorch",
      "OpenAI APIs",
      "LLMs",
      "Agents SDK",
      "RAG",
    ],
  },
  {
    label: "Mathematics & Statistics",
    items: [
      "Hypothesis Testing",
      "Multivariate Statistics",
      "Nonparametric Tests",
      "Linear Algebra",
      "Calculus",
    ],
  },
  {
    label: "Tools",
    items: ["GitHub", "Jupyter", "SQLite"],
  },
];

export type Project = {
  id: string;
  title: string;
  subtitle: string;
  branch: string;
  branchUrl: string;
  techniques: string;
  result: string;
  bullets: string[];
};

export const projects: Project[] = [
  {
    id: "capstone",
    title: "Infant Mortality Rate Study",
    subtitle: "DATA-4332 Undergraduate Capstone",
    branch: "Capstone-Project",
    branchUrl:
      "https://github.com/lmn4121/Project-Portfolio/tree/Capstone-Project",
    techniques:
      "EDA (leakage, multicollinearity, missingness), state-wise imputation, robust scaling, forward selection + agglomerative clustering/PCA (643 → 50 → 14 features), linear and tree baselines, final ANN, SHAP explainability, Streamlit deployment with XAI + agentic interpretation.",
    result:
      "Best ANN about R² 0.86 and RMSE 5.1 (train; test R² ~0.87).",
    bullets: [
      "Curated, explored, and preprocessed data to analyze and predict infant mortality rates in Empowered Action Group states in India.",
      "Developed a preprocessing pipeline to address scarce data and high dimensionality; trained an artificial neural network achieving an R² of 0.86.",
      "Built a Streamlit deployment app that combines explainable AI (XAI) and agentic AI to generate solutions for reducing infant mortality.",
    ],
  },
  {
    id: "cv",
    title: "Chest X-Ray Classification",
    subtitle: "DATA-4380 Computer Vision",
    branch: "Data4380-Computer-Vision",
    branchUrl:
      "https://github.com/lmn4121/Project-Portfolio/tree/Data4380-Computer-Vision",
    techniques:
      "Baselines (ANN/CNN), CLAHE and augmentation, frozen VGG16 exploration, final fine-tuned DenseNet201 with class weights.",
    result:
      "Final model validation macro F1 0.92, test macro F1 0.83 (written report).",
    bullets: [
      "Processed and augmented lung X-rays to diagnose COVID-19 or viral pneumonia.",
      "Fine-tuned a transfer-learning model to achieve a macro F1 score of 0.82 on a small image dataset.",
    ],
  },
  {
    id: "kaggle",
    title: "Metastatic Cancer Diagnosis",
    subtitle: "WiDS Datathon 2024 Challenge 1 (Kaggle)",
    branch: "Kaggle-Project",
    branchUrl:
      "https://github.com/lmn4121/Project-Portfolio/tree/Kaggle-Project",
    techniques:
      "Feature filtering, mode imputation, one-hot encoding, simple neural net, AdaBoost, and gradient boosting with GridSearchCV.",
    result:
      "~80% validation accuracy; Kaggle private/public scores 0.789 / 0.798. Best among compared models: boosted gradient ensemble.",
    bullets: [
      "Binary classification of whether a patient received a metastatic cancer diagnosis within 90 days of screening.",
      "Compared a simple neural network, AdaBoost, and boosted gradient ensembles on patient location, age, and diagnosis features.",
    ],
  },
  {
    id: "twin",
    title: "Resume Chatbot Digital Twin",
    subtitle: "LLM & Agentic AI — Independent Project",
    branch: "Digital-Twin",
    branchUrl:
      "https://github.com/lmn4121/Project-Portfolio/tree/Digital-Twin",
    techniques:
      "LLM-assisted semantic chunking into Chroma; OpenAI Agents SDK twin with RAG, email capture, and unknown-question tools; FastAPI + SSE API for the portfolio chat widget (Gradio kept for local demos).",
    result:
      "Try it on this site via Ask Landon’s twin — retrieval-grounded answers with tools to record leads / unanswered questions instead of inventing replies.",
    bullets: [
      "Built agentic applications using OpenAI Agents SDK, including a digital twin and an automated email workflow.",
      "Implemented Retrieval-Augmented Generation (RAG) to provide business-specific context to LLMs.",
      "Exposed the twin as an always-on API and embedded a native portfolio chat widget (no OpenAI keys in the browser).",
    ],
  },
];

export const independentAi = [
  "Built a multimodal chatbot integrating LLMs, image generation, and text-to-speech to simulate interactive stories.",
  "Used LLMs to translate Python code into C++ for performance-oriented processing.",
  "Implemented Retrieval-Augmented Generation (RAG) to provide business-specific context to LLMs.",
  "Built agentic applications using OpenAI Agents SDK, including a digital twin and an automated email workflow.",
];
