# Data4390 Computer Vision: Chest X-Ray Classification

## Contents
- [The Problem](#the-problem)
- [Project Overview](#project-overview)
- [Data](#data)
- [Exploration](#exploration)
- [Final Modeling Approach](#final-modeling-approach)
- [Results](#results)
- [Key Insights](#key-insights)
- [How to Run](#how-to-run)
- [Repository Structure](#repository-structure)

## The Problem
Classify chest X-ray images into one of three categories: **Covid**, **Normal**, or **Viral Pneumonia**.

This was a course project for **DATA 4390** and my first project focused on computer vision.

## Project Overview
**Goal:**
- Build an image classifier that distinguishes Covid, Normal, and Viral Pneumonia chest X-rays
- Practice core computer vision techniques: CNNs, augmentation, class imbalance handling, and transfer learning

**Approach:**
- Explore the dataset and class balance
- Prototype simple models (fully connected network and small CNNs)
- Try transfer learning with VGG16 and DenseNet201
- Finalize a DenseNet201 fine-tuning setup based on instructor guidance and examples

**Key Results (final DenseNet201 model):**
- Held-out test set (**66** images): overall accuracy **0.88**
- Per-class test F1: Covid **0.96**, Normal **0.80**, Viral Pneumonia **0.86**
- Macro-average precision / recall / F1 on that report: **0.87**

## Data
**Dataset (as used in the notebook):**
- Local / Google Drive folder named `Covid19-dataset`
- Three class folders corresponding to **Covid**, **Normal**, and **Viral Pneumonia**
- Images loaded and resized for training (student exploration used **256×256**; the final DenseNet pipeline used **224×224**)

**Splits used for the final DenseNet pipeline** (`ImageDataGenerator`, `validation_split=0.2` on the train folder):
- Train: **201** images
- Validation: **50** images
- Test: **66** images (from the separate `test` folder)

**Class imbalance (student training folder counts):**
- Covid: **111**
- Normal: **70**
- Viral Pneumonia: **70**

Balanced **class weights** were used when fitting the final model.

> Note: The notebook references a Drive path only. A public dataset citation is not recorded in the notebook, so this README does not invent one.

## Exploration
Early work treated this as an introduction to computer vision. Experiments included:

- Simple **ANN** (flatten → dense layers)
- Small **CNNs** from scratch
- **CLAHE**-style contrast enhancement and geometric / photometric augmentation
- Transfer learning with **VGG16** and **DenseNet201** (frozen bases, then limited unfreezing)

These runs informed preprocessing and architecture choices. They are not the published end results.

## Final Modeling Approach
The final model follows an instructor-advised DenseNet setup that I reproduced and trained:

**Architecture:**
- Backbone: **DenseNet201** pretrained on **ImageNet** (`include_top=False`)
- Head: **GlobalAveragePooling2D** → **Dropout(0.3)** → **Dense(3, softmax)**

**Training setup:**
- Input size: **224×224**, batch size **16**
- Augmentation (train): rescale `1/255`, rotation (±15°), shear / zoom / shift (0.1), horizontal flip
- Loss: `categorical_crossentropy`
- Fine-tuning: unfreeze the last **40** DenseNet layers
- Optimizer: **Adam** with learning rate **1e-5**
- Epochs: **25**
- **Class weights** applied for imbalance

## Results
### Test set (named-class classification report)
| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| Covid | 1.00 | 0.92 | 0.96 | 26 |
| Normal | 0.80 | 0.80 | 0.80 | 20 |
| Viral Pneumonia | 0.82 | 0.90 | 0.86 | 20 |
| **Overall accuracy** | | | **0.88** | **66** |

Macro-average precision / recall / F1 on this report: **0.87**.

### Training / validation (final fit)
- Final epoch validation accuracy: **0.84** (train accuracy ≈ **0.85**)

### Validation F1 stability check
Repeated prediction on the validation generator (30 runs; augmentation can vary) produced validation F1 with mean / median **0.85**, std **0.03**.

## Key Insights
- Transfer learning with a modern CNN backbone was far more practical than training deep networks from scratch on a small medical image set
- Class imbalance mattered; balanced class weights were part of the final training setup
- Augmentation and a careful train/validation split on the training folder helped stabilize learning before evaluating on the held-out test folder
- Covid was the strongest class in the final test report; Normal was the hardest of the three

## How to Run
1. Place the `Covid19-dataset` folder so that it contains `train/` and `test/` class subfolders (matching the notebook’s expected layout)
2. Open `Data4390_Computer_Vision.ipynb` in Jupyter or Google Colab (GPU recommended)
3. Update any Drive / local paths to point at your dataset copy
4. Run cells in order; the final DenseNet section is labeled around the instructor-guided fine-tuning workflow near the end of the notebook

Dependencies used in the notebook include TensorFlow / Keras, OpenCV, scikit-learn, NumPy, Matplotlib, and Seaborn.

## Repository Structure
- `README.md` — this summary (goal, techniques, results)
- `Data4390_Computer_Vision.ipynb` — full exploration notebook plus the final DenseNet201 fine-tuning and evaluation
