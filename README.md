# Customer Segmentation to Intervention Pipeline

A full data science workflow built on the UCI Online Retail II dataset,
covering RFM feature engineering, unsupervised clustering, supervised
classification, Monte Carlo intervention simulation, and a deployed REST API.

**Live Demo:** https://customer-segmentation-intervention.streamlit.app
**API Docs:** https://customer-segmentation-intervention.onrender.com/docs

**Headline Result:** Segmentation-driven intervention across 4,338 customers
produces £897,609 incremental revenue against a £37,215 campaign budget,
delivering an overall ROI of 2,312%.

## Business Problem

Businesses cannot treat all customers the same. Marketing budgets
are finite and customer value varies enormously. This project answers
three questions every CRM and marketing team faces:

- Who are our best customers and how do we retain them?
- Who is drifting away and can we bring them back cost effectively?
- Which customer segments respond best to which treatments?

## Dataset

UCI Online Retail II dataset. 541,910 transactions from a UK-based
gift-ware e-commerce retailer covering December 2010 to December 2011.
Available at: https://archive.ics.uci.edu/dataset/502/online+retail+ii

Raw data is not included in this repo. Download the xlsx file and
place it in data/raw/online+retail+ii/ before running notebooks.

## Methodology

### 1. Data Cleaning and EDA
541,910 raw transactions cleaned to 397,885 valid records.
Removed anonymous sessions (no Customer ID), cancelled invoices,
and anomalous quantities and prices. Documented in notebook 01.

### 2. RFM Feature Engineering
Recency, Frequency, and Monetary features computed per customer
against a snapshot date of 2011-12-10. Extended features include
cancellation rate and product diversity. Log transformation applied
to address right skew, followed by StandardScaler normalisation.
Documented in notebook 02.

### 3. Clustering
KMeans and DBSCAN evaluated. KMeans k=4 selected on business
interpretability grounds with silhouette score of 0.34.
DBSCAN produced two dominant clusters and three micro clusters
of 7-11 customers, silhouette score 0.17. Four segments identified:
Champions, Promising, At-Risk, Lost. Documented in notebook 03.

### 4. Classification
XGBoost and PyTorch feedforward network benchmarked as inference
classifiers for new customer segment prediction. XGBoost selected
with weighted F1 of 0.965 versus PyTorch 0.887. PyTorch implementation
retained to demonstrate neural network training pipeline including
custom Dataset class, early stopping, and learning rate scheduling.
Documented in notebook 04.

### 5. Intervention Simulation
Baseline and advanced simulations built. Advanced simulation adds
customer level heterogeneity via within-segment Recency ranking,
Monte Carlo uncertainty quantification across 10,000 iterations,
and budget constraint optimisation using linear programming.
Documented in notebooks 05 and 06.

### 6. Deployment
XGBoost model served via FastAPI REST API deployed on Render.
Streamlit frontend deployed on Streamlit Cloud.
Render kept alive via cron-job.org pings every 10 minutes.

## Key Results

### Segmentation
| Segment | Customers | Avg Recency (days) | Avg Frequency | Avg Monetary (£) |
|---|---|---|---|---|
| Champions | 713 | 11 | 13.7 | 8,086 |
| Promising | 810 | 17 | 2.1 | 548 |
| At-Risk | 1,193 | 70 | 4.1 | 1,801 |
| Lost | 1,622 | 181 | 1.3 | 342 |

### Classifier Comparison
| Model | Weighted F1 | Accuracy | Champions Recall |
|---|---|---|---|
| XGBoost | 0.965 | 97% | 0.94 |
| PyTorch | 0.887 | 89% | 0.78 |

### Intervention Simulation
| Segment | Treatment | Customers | ROI % |
|---|---|---|---|
| Champions | Loyalty Program Upsell | 713 | 5,291% |
| Promising | Cross-sell Campaign | 810 | 448% |
| At-Risk | Reactivation Voucher | 1,193 | 2,061% |
| Lost | Win-back Discount | 1,622 | 242% |

### Monte Carlo Risk Analysis (10,000 simulations)
| Segment | Mean ROI % | 5th Percentile | Prob Positive ROI | Risk Adjusted ROI |
|---|---|---|---|---|
| Champions | 5,301% | 2,606% | 99.9% | 3.26 |
| At-Risk | 2,057% | 1,169% | 100.0% | 3.78 |
| Promising | 446% | 115% | 98.7% | 2.21 |
| Lost | 246% | -87% | 88.1% | 1.25 |

### Budget Optimisation (£25,000 constraint)
Optimal allocation targets Champions (100%), At-Risk (100%),
and Promising (37%). Lost segment excluded. Maximum incremental
revenue under constraint: £847,378.

## Repo Structure

```
customer-segmentation-intervention/
    data/
        processed/          # RFM features, cluster labels, model artifacts
    notebooks/
        01_eda.ipynb                    # Data audit and cleaning
        02_feature_engineering.ipynb    # RFM computation and scaling
        03_clustering.ipynb             # KMeans and DBSCAN comparison
        04_classifier.ipynb             # XGBoost and PyTorch benchmarking
        05_intervention.ipynb           # Baseline intervention simulation
        06_advanced_simulation.ipynb    # Monte Carlo and budget optimisation
    src/
        config.py           # Centralised parameters and intervention definitions
        features.py         # RFM computation functions
        model.py            # PyTorch Dataset and model classes
        simulation.py       # Intervention engine
    api/
        main.py             # FastAPI inference endpoint
    outputs/
        figures/            # All saved charts
        segment_profiles.csv
        intervention_results.csv
    streamlit_app.py        # Streamlit frontend
    Procfile                # Render deployment config
    requirements.txt
```

## How to Run

### Setup
```bash
git clone https://github.com/BhavyaMehra/customer-segmentation-intervention.git
cd customer-segmentation-intervention
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### Data
Download UCI Online Retail II dataset from:
https://archive.ics.uci.edu/dataset/502/online+retail+ii

Place the xlsx file in: data/raw/online+retail+ii/online_retail_II.xlsx

### Run Notebooks
Run notebooks in order 01 through 06 from the notebooks/ folder.

### Run API Locally
```bash
uvicorn api.main:app --reload
```
API docs available at http://localhost:8000/docs

### Run Streamlit Locally
```bash
streamlit run streamlit_app.py
```

## Dependencies
See requirements.txt. Key libraries: pandas, numpy, scikit-learn,
xgboost, torch, fastapi, uvicorn, streamlit, scipy.

## Limitations and Future Work
- Lift rates are assumption based and require A/B test validation
- Campaign costs reflect direct delivery costs only
- Beta distribution would be more theoretically correct for
  Monte Carlo lift rate sampling than normal distribution
- Robust optimisation using downside percentile estimates
  is a natural extension of the budget optimisation

