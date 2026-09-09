# Churn Prediction Platform

Predicting telecom customer churn with a full-stack ML pipeline — from raw data to a deployed, interactive prediction app.

## Problem Statement

Customer churn (customers leaving a service) directly impacts revenue for subscription-based businesses. This project builds an end-to-end system that cleans real customer data, trains a churn prediction model, serves it through an API, and exposes it via a web app and a business-facing dashboard — not just a notebook.

## Status: In Progress

- [x] Step 1: Data cleaning
- [ ] Step 2: EDA & feature analysis
- [ ] Step 3: Model training & validation
- [ ] Step 4: Prediction API (Django REST Framework)
- [ ] Step 5: Frontend (React)
- [ ] Step 6: Deployment (AWS)
- [ ] Step 7: Monitoring dashboard (Power BI)
- [ ] Step 8: Final documentation & write-up

## Dataset

[IBM Telco Customer Churn](https://www.kaggle.com/blastchar/telco-customer-churn) — 7,043 customers, 21 features (demographics, account info, subscribed services, churn label).

## Tech Stack

| Layer | Tools |
|---|---|
| Data & Modeling | Python, Pandas, scikit-learn |
| API | Django REST Framework |
| Database | MongoDB (prediction logging) |
| Frontend | React |
| Deployment | AWS |
| Reporting | Power BI |

## Step 1: Data Cleaning

Run:
```
pip install -r requirements.txt
python 01_clean_data.py
```

**Key finding:** `TotalCharges` is stored as text, and 11 rows contain a blank value instead of a number. Every one of these rows has `tenure == 0` — these are brand-new customers who haven't completed a full billing cycle yet, not random missing data. These were set to `0.0` rather than dropped or imputed with a mean, since a mean would misrepresent a genuinely new customer.

Also standardized categorical labels (e.g. collapsed `"No internet service"` into `"No"` across related columns) to keep the feature space smaller and more interpretable for modeling.

**Class balance:** 73.5% did not churn, 26.5% churned. This imbalance will shape the validation strategy in Step 3 — stratified splits and precision/recall/F1 will matter more than raw accuracy.

Output: `telco_cleaned.csv` (7,043 rows, 24 columns — includes two engineered features: `tenure_bucket` and `avg_monthly_spend`).

## What's Next

Step 2 will explore churn rate by contract type, tenure, and monthly charges, and finalize feature engineering ahead of model training.

## Limitations (updated as project progresses)

- Dataset represents a single snapshot in time per customer; it doesn't capture how customer behavior changes month to month.
- This section will be expanded with modeling and deployment limitations as later steps are completed.
