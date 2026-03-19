# ❄️ F3 Innovate Frost Risk Forecasting Challenge  
## Team **Tyler and Aziz**

Welcome to the repository for our submission to the **F3 Innovate Frost Risk Forecasting Challenge**.  
Our goal is to build a **probabilistic frost-risk forecasting pipeline** for California specialty crop regions using CIMIS weather station data.

We forecast **frost occurrence and temperature** at multiple lead times and evaluate how well the model generalizes to **new locations and new frost seasons**.

---

## 📁 Repository Structure

```bash
├── F3Project.ipydb               # Project Notebook
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── F3 Frost Report.pdf            # Final PDF report (answers Q1–Q4)
```

## 🧰 Environment Setup
```
conda create -n frost python=3.10
conda activate frost
pip install -r requirements.txt
```

## 🌡️ Problem Overview
For each CIMIS station and each hour, we aim to forecast:
**Whether frost will occur**
**Probability that temperature < 0°C**
**Seasonal frost patterns** (useful for long-term planning)
**Hourly frost variability** at specific stations
The goal is to create **actionable, interpretable** frost forecasts useful for growers statewide.

## 🚀 Pipeline Overview
1. **Prepoccesing**
Cleaned the CIMIS dataset, handled missing values, engineered new features, applied cyclical encoding, and standardized all predictors.
3. **Feature Selection**
Selected the most relevant weather and derived variables for frost prediction while checking for multicollinearity.
4. **Train–Test Split**
Used LOSO (Use on station out) four test/train split
5. **Model Training**
Trained the classification model using the processed weather features to predict frost events.
6. **Hyperparameter Tuning**
Optimized model parameters using cross-validation to improve performance and reduce overfitting.
7. **Model Evaluation**
Evaluated performance using ROC-AUC, PR-AUC, BRIER, and RMSE

## 🔧 Preprocessing Steps
1. Loaded the full CIMIS daily weather dataset.
2. Added month, year, and day columns for time tracking.
3. Created frost labels aligned with daily weather observations.
4. Checked for missing values across all variables.
5. Examined correlations between weather variables.
8. Engineered new features for early frost detection:
   - Dewpoint depression (air temperature – dewpoint)
   - Short-term cooling rate (temperature change over time)
   - Calm-wind indicator (wind speed < 1 m/s)
   - Vapor pressure deficit (VPD)
   - Applied sine and cosine encoding to:
         Month (to preserve seasonality)
         Wind direction (to preserve circular direction)
9. Standardized all continuous predictor variables.
10. One-Hot encoded categorical variables
11. Handled missing values
## 🧠 Modeling Strategy
- Random Forest
- Tuned XGB Boost Classifer

## 🚀 Running the Project

### 1. Install Dependencies
Make sure you have Python and `pip` installed. From the root directory run:

```bash
pip install -r requirements.txt
```

### 2. Launch Jupyter Notebook
To run the modeling pipeline and reproduce results:

#### a.) Open the Jupyter environment:

```bash
jupyter notebook
```

In your browser, open the notebook file:
```bash
F3Project.ipynb
```
Then simply run all cells sequentially to process data, train models, and reproduce results.

## 🔗 References
1. UC Davis Biometeorology Group.
Principles of Frost Protection.
(Discusses dewpoint, radiational cooling, calm winds, VPD, agricultural frost protection.)
https://biomet.ucdavis.edu/doc/Principles_of_Frost_Protection%E2%80%93UCDavis_Biometeorology_Group.pdf

2. Vapor Pressure Deficit Reference (Formula & physical meaning).
https://wikifire.wsl.ch/tiki-index.php?page=Vapor+pressure+deficit

3. Dewpoint Depression Mechanism (Video explanation).
https://youtu.be/6buQuGG53gs?si=GKY9xD4dmnzo_kOB&t=11
