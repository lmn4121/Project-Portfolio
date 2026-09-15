# DATA 4380 Computer Vision: Chest X-Ray Classification

## Contents
- [The Problem](#the-problem)
- [Project Overview](#project-overview)
- [Data](#data)
- [Exploration](#exploration)
- [Final Modeling Approach](#final-modeling-approach)
- [Results](#results)
- [Key Insights](#key-insights)
- [Reports](#reports)
- [How to Run](#how-to-run)
- [Repository Structure](#repository-structure)

## The Problem
Classify chest X-ray images into one of three categories: **COVID-19**, **Normal** (healthy lungs), or **Viral Pneumonia**.

This was a **DATA 4380: Data Problems** course project (University of Texas at Arlington) and my first project focused on computer vision.

**Research framing (from the written report):** Can deep learning on chest X-rays differentiate healthy individuals from those with COVID-19 or viral pneumonia—and serve as a precedent for AI-assisted screening alongside standard nucleic acid testing?

## Project Overview
**Goal:**
- Build an image classifier that distinguishes COVID-19, normal, and viral pneumonia chest X-rays
- Practice core computer vision techniques: CNNs, augmentation, class-imbalance handling, and transfer learning

**Approach:**
- Explore the dataset, class balance, and how hard Normal vs Pneumonia are to tell apart visually
- Prototype simple baselines (ANN and a small CNN)
- Method 1: CLAHE + oversampling-style augmentation with a deeper CNN and frozen VGG16
- Method 2 (final): geometric augmentation + class weights with fine-tuned **DenseNet201**

**Key Results (final DenseNet201 model, from the written report):**
- Validation macro F1: **0.92**
- Test macro F1: **0.83**
- Validation F1 stability (30 repeated predicts): mean/median **0.85**, std **0.03**, range **0.12**

## Data
**Source:** [COVID-19 Image Dataset (Kaggle)](https://www.kaggle.com/datasets/pranavraikokte/covid19-image-dataset) — Pranav Raikote

**Classes:**
- COVID-19 (majority)
- Normal
- Viral Pneumonia

**Size / splits used in exploration:**
- Total: **317** images (small dataset)
- Typical exploration split: Train **251** (~80%) / Validation **33** (~10%) / Test **33** (~10%)
- Train class counts: COVID-19 **111** (~44%), Normal **70** (~28%), Pneumonia **70** (~28%)

**Splits used for the final DenseNet pipeline:**
- Train: **201** (~63%)
- Validation: **50** (~16%)
- Test: **66** (~21%)

Images were rescaled to \[0, 1\]. Final DenseNet inputs were **224×224**.

## Exploration
Early work treated this as an introduction to computer vision:

- **ANN baseline** and a **one-block CNN** — both struggled (near-random / severe overfitting on this small set)
- **CLAHE** contrast enhancement combined with minority-class oversampling-style augmentation
- Deeper **CNN from scratch** and frozen **VGG16** transfer learning (Method 1) — improved training behavior but still weak on minority classes / validation

These runs informed preprocessing and architecture choices. They are exploration, not the published end results.

## Final Modeling Approach
**Method 2 — DenseNet201 fine-tuning** (instructor-guided setup I reproduced):

**Architecture:**
- Backbone: **DenseNet201** pretrained on **ImageNet** (`include_top=False`)
- Head: **GlobalAveragePooling2D** → **Dropout(0.3)** → **Dense(3, softmax)**

**Strategy:**
- Unfreeze later DenseNet convolutional layers (written report: last **43** layers) so the backbone can adapt from ImageNet toward X-ray appearance
- Use **class weights** instead of oversampling for imbalance
- Apply geometric augmentation at load time: horizontal flip, shear/zoom/shift (0.1), rotation (±15°)

**Training:**
- Optimizer: **Adam**, learning rate **1e-5**
- Epochs: **25**, batch size **16**
- Loss: categorical cross-entropy

## Results
### Final DenseNet201 (written report)
| Split | Macro F1 | Notes |
|-------|----------|-------|
| Validation | **0.92** | Strongest held-out-in-training metric |
| Test | **0.83** | Gap vs validation indicates variance on a small set |

Confusion matrices in the report show the main failure mode is **Normal vs Viral Pneumonia**; COVID-19 is the strongest class.

### Validation F1 stability
30 repeated validation predictions (augmentation can vary): mean/median F1 **0.85**, std **0.03**, range **0.12**.

### Method 1 (exploration, for context)
- Deeper CNN after CLAHE/oversampling: train macro F1 ~**0.49**, but validation remained poor (including failure on the Normal class in the report)
- Frozen VGG16: train/val macro F1 ~**0.50** / **0.47**

## Key Insights
- Fine-tuning a heavy transfer model beat building CNNs from scratch on this small medical set
- ImageNet initialization helps, but is not X-ray-specific—variance and Normal↔Pneumonia confusion remain the main limits
- Macro F1 (and recall) matter more than raw accuracy under slight class imbalance and a contagious-disease framing
- The model is better framed as a **screening aid** (potential positive / not) than as a standalone diagnostic, matching the report’s conclusion

## Reports
Course writeups included on this branch:
- `Nguyen_Landon_DATA4380_Report.pdf` — full written report (methods, results, conclusion)
- `Data4380_Covid19_Presentation.pdf` — slide-style project presentation

## How to Run
1. Download the [Kaggle COVID-19 Image Dataset](https://www.kaggle.com/datasets/pranavraikokte/covid19-image-dataset) so it has `train/` and `test/` class folders
2. Open `Data4380_Computer_Vision.ipynb` in Jupyter or Google Colab (GPU recommended)
3. Point Drive / local paths at your dataset copy
4. Run cells in order; the final DenseNet fine-tuning section is near the end of the notebook

Dependencies used in the notebook include TensorFlow / Keras, OpenCV, scikit-learn, NumPy, Matplotlib, and Seaborn.

## Repository Structure
- `README.md` — this summary (goal, techniques, results)
- `Data4380_Computer_Vision.ipynb` — exploration notebook plus final DenseNet201 fine-tuning and evaluation
- `Nguyen_Landon_DATA4380_Report.pdf` — written project report
- `Data4380_Covid19_Presentation.pdf` — presentation slides
