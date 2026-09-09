# Churn Prediction Platform

Predicting telecom customer churn with a full-stack ML pipeline — from raw data to a deployed, interactive prediction app.

## Problem Statement

Customer churn (customers leaving a service) directly impacts revenue for subscription-based businesses. This project builds an end-to-end system that cleans real customer data, trains a churn prediction model, serves it through an API, and exposes it via a web app and a business-facing dashboard — not just a notebook.

## Status: In Progress

- [x] Step 1: Data cleaning
- [x] Step 2: EDA & feature analysis
- [x] Step 3: Model training & validation
- [x] Step 4: Prediction API (Django REST Framework)
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
| Database | MongoDB (prediction logging — coming in a later step) |
| Frontend | React |
| Deployment | AWS |
| Reporting | Power BI |

## Steps 1–3: Data Cleaning, EDA, and Model Training

All of the data work lives in a single notebook: **`churn_project.ipynb`**.

Run:
```
pip install -r requirements.txt
```
Then open `churn_project.ipynb` in VS Code (with the Jupyter extension installed) and run all cells.

**Step 1 — Key finding:** `TotalCharges` is stored as text, and 11 rows contain a blank value instead of a number. Every one of these rows has `tenure == 0` — these are brand-new customers who haven't completed a full billing cycle yet, not random missing data. These were set to `0.0` rather than dropped or imputed with a mean, since a mean would misrepresent a genuinely new customer. Categorical labels were also standardized (e.g. collapsed `"No internet service"` into `"No"`) to keep the feature space smaller and more interpretable.

**Step 2 — Key findings:**
- Month-to-month customers churn at **42.7%** vs just **2.8%** for two-year contracts — roughly a 15x difference, and likely the strongest single predictor in the dataset.
- Churn risk is highest in a customer's first 6 months (**52.9%**) and drops steadily with tenure (**9.5%** past 4 years) — a classic "new customer risk window."
- Counterintuitive finding: customers who churn pay *more* per month on average (**$74.44**) than customers who stay (**$61.27**), suggesting price sensitivity or perceived value plays a role independent of tenure and contract type.

**Step 3 — Model training:** Compared Logistic Regression (with scaled numeric features) against Random Forest, using a stratified 80/20 split to preserve class balance and prioritizing recall on the churn class and ROC-AUC over raw accuracy, given the 73.5%/26.5% class imbalance. Numeric features were scaled with `StandardScaler`, fit only on the training set to avoid leaking test-set information. Top predictive features (from Random Forest importances): `TotalCharges`, `MonthlyCharges`, and `tenure`, followed by contract type — consistent with the Step 2 findings.

Output: `telco_cleaned.csv`, plus saved model artifacts `churn_model.joblib`, `scaler.joblib`, and `model_columns.joblib` used by the API in Step 4.

## Step 4: Prediction API (Django REST Framework)

A REST API serves live predictions from the trained model.

Run:
```
python manage.py migrate
python manage.py runserver
```

Test the endpoint:
```
POST http://127.0.0.1:8000/api/predict/
Content-Type: application/json

{
    "tenure": 2,
    "MonthlyCharges": 95.5,
    "TotalCharges": 191.0,
    "SeniorCitizen": 0,
    "Contract": "Month-to-month",
    "InternetService": "Fiber optic",
    "PaymentMethod": "Electronic check",
    "Partner": "No",
    "Dependents": "No"
}
```

Example response:
```json
{"churn_prediction": "Yes", "churn_probability": 0.714}
```

The view loads the model, scaler, and expected column structure once at server startup (not per-request), rebuilds the input into the same one-hot-encoded shape the model was trained on, applies the same fitted scaler to numeric fields, and returns both the predicted class and the churn probability.

## What's Next

Step 5 will build a React frontend so predictions can be made through a form instead of raw API calls, removing the need to test with curl/PowerShell.

## Limitations (updated as project progresses)

- Dataset represents a single snapshot in time per customer; it doesn't capture how customer behavior changes month to month.
- The model was trained with a specific scikit-learn version; loading it with a different installed version can raise compatibility warnings and should be monitored.
- This section will be expanded with deployment and monitoring limitations as later steps are completed.
