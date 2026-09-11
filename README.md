# Churn Prediction Platform

A full-stack machine learning application that predicts telecom customer churn — from raw, messy data to a live, deployed web app.

**🔗 Live Demo:** [churn-frontend-1nb4.onrender.com](https://churn-frontend-1nb4.onrender.com)
**🔗 Live API:** [churn-api-4wgc.onrender.com/api/predict/](https://churn-api-4wgc.onrender.com/api/predict/)

> Note: hosted on Render's free tier — the backend may take ~30-50 seconds to wake up on the first request after a period of inactivity.

---

## Overview

Customer churn — when a customer leaves a subscription-based service — directly impacts revenue for businesses. This project builds a complete system that:

1. Cleans a real, messy customer dataset
2. Explores it for genuine, defensible business insights
3. Trains and validates a churn prediction model
4. Serves live predictions through a REST API
5. Presents them through an interactive web app
6. Runs entirely on free, publicly deployed infrastructure

This isn't a single notebook — it's an end-to-end product, built and debugged step by step.

## Status: Complete (Core Pipeline)

- [x] Step 1: Data cleaning
- [x] Step 2: EDA & feature analysis
- [x] Step 3: Model training & validation
- [x] Step 4: Prediction API (Django REST Framework)
- [x] Step 5: Frontend (React)
- [x] Step 6: Deployment (Render)
- [ ] Step 7: Monitoring dashboard (Power BI)
- [ ] Step 8: Prediction logging (MongoDB)

## Tech Stack

| Layer | Tools |
|---|---|
| Data & Modeling | Python, Pandas, scikit-learn |
| API | Django REST Framework, Gunicorn, WhiteNoise |
| Frontend | React (Vite) |
| Deployment | Render (Web Service + Static Site) |
| Version Control | Git, GitHub |

## Architecture

```
┌─────────────────┐         HTTPS POST          ┌──────────────────────┐
│  React Frontend  │  ─────────────────────────▶ │   Django REST API     │
│  (Static Site)   │  ◀───────────────────────── │   (Web Service)       │
│  Render          │      JSON prediction         │   Render               │
└─────────────────┘                              │  ┌─────────────────┐  │
                                                    │  │ scikit-learn    │  │
                                                    │  │ model + scaler  │  │
                                                    │  └─────────────────┘  │
                                                    └──────────────────────┘
```

## Dataset

[IBM Telco Customer Churn](https://www.kaggle.com/blastchar/telco-customer-churn) — 7,043 customers, 21 features (demographics, account info, subscribed services, churn label).

---

## Steps 1–3: Data Cleaning, EDA, and Model Training

All data work lives in a single notebook: **`churn_project.ipynb`**.

**Run locally:**
```bash
pip install -r requirements.txt
```
Open `churn_project.ipynb` in VS Code (with the Jupyter extension) and run all cells.

### Step 1 — Data Cleaning

**Key finding:** `TotalCharges` is stored as text, and 11 rows contain a blank value instead of a number. Every one of these rows has `tenure == 0` — brand-new customers who haven't completed a full billing cycle yet, not random missing data. These were set to `0.0` rather than dropped or imputed with a mean, since a mean would misrepresent a genuinely new customer.

Categorical labels were also standardized (e.g. collapsed `"No internet service"` into `"No"`) to keep the feature space smaller and more interpretable.

### Step 2 — Exploratory Data Analysis

- Month-to-month customers churn at **42.7%** vs just **2.8%** for two-year contracts — roughly a 15x difference, and the strongest single predictor in the dataset.
- Churn risk is highest in a customer's first 6 months (**52.9%**) and drops steadily with tenure (**9.5%** past 4 years) — a "new customer risk window."
- **Counterintuitive finding:** customers who churn pay *more* per month on average (**$74.44**) than customers who stay (**$61.27**) — suggesting price sensitivity or perceived value plays a role independent of tenure and contract type.

### Step 3 — Model Training & Validation

Compared Logistic Regression (with scaled numeric features) against Random Forest, using a stratified 80/20 split to preserve class balance (73.5% / 26.5%) and prioritizing recall on the churn class and ROC-AUC over raw accuracy. `StandardScaler` was fit only on the training set to avoid leaking test-set information.

Top predictive features (Random Forest importances): `TotalCharges`, `MonthlyCharges`, `tenure`, then contract type — consistent with the EDA findings.

Output: `telco_cleaned.csv`, plus saved model artifacts (`churn_model.joblib`, `scaler.joblib`, `model_columns.joblib`) used by the API.

---

## Step 4: Prediction API (Django REST Framework)

Serves live predictions from the trained model.

**Run locally:**
```bash
python manage.py migrate
python manage.py runserver
```

**Endpoint:**
```
POST /api/predict/
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

**Response:**
```json
{"churn_prediction": "Yes", "churn_probability": 0.714}
```

The view loads the model, scaler, and expected column structure once at server startup, rebuilds incoming requests into the same one-hot-encoded shape the model was trained on, applies the fitted scaler to numeric fields, and returns both the predicted class and probability.

---

## Step 5: Frontend (React)

A form-based UI replaces manual API calls.

**Run locally:**
```bash
cd frontend
npm install
npm run dev
```

**Design approach:** a two-panel layout separates data entry (left) from the result (right) — a live "risk readout" panel that changes color based on the predicted probability (red for high risk, amber for medium, teal for low), rather than a flat yes/no answer. The goal is legibility for a non-technical user (e.g. a support rep deciding whether to intervene), not just a raw number. Typography pairs a serif display font (Fraunces) with a clean sans-serif (IBM Plex Sans) and a monospace probability readout (IBM Plex Mono).

---

## Step 6: Deployment (Render)

Both services are deployed on Render's free tier:

- **Backend** — Web Service running Gunicorn, static files served via WhiteNoise, `DEBUG` and `ALLOWED_HOSTS` controlled through environment variables (not hardcoded).
- **Frontend** — Static Site built with Vite, API base URL injected at build time via `VITE_API_URL`.

**Debugging notes worth keeping:**
- **Local CORS mismatch:** initial integration failed with `No 'Access-Control-Allow-Origin' header is present`. Traced via browser DevTools → Console to `CORS_ALLOWED_ORIGINS` only listing port 3000 (the older Create React App default) while Vite serves on port 5173.
- **Production CORS mismatch:** after deploying, the same class of error reappeared because the live frontend's Render URL wasn't yet in the backend's allowed origins. Fixed by adding a `FRONTEND_URL` environment variable read at runtime in `settings.py`, avoiding a hardcoded production URL in source code.

Both issues were diagnosed the same way — reading the exact browser error rather than guessing — and fixed with configuration, not code rewrites.

---

## What's Next

- **Step 7:** Power BI dashboard tracking prediction volume and model confidence over time.
- **Step 8:** Log every prediction request to MongoDB to enable the Step 7 dashboard and monitor for model drift.

## Limitations

- Dataset represents a single snapshot in time per customer; it doesn't capture how behavior changes month to month.
- The model was trained with a specific scikit-learn version; loading it with a different installed version raises compatibility warnings (visible in Render logs) and should be monitored if retrained.
- The backend is on Render's free tier, which spins down after inactivity — the first request after idle time will be slow (~30-50s) while the instance restarts. A paid tier or scheduled keep-alive ping would remove this in a production setting.
- No authentication on the API — acceptable for a portfolio demo, not for production use with real customer data.

---

## Closing Note

This project is a work in progress by design — Steps 1 through 6 (data cleaning through live deployment) are complete and functional today; Steps 7 and 8 are planned extensions rather than gaps. Each step so far was built, tested, and debugged individually, including two separate CORS issues traced through browser DevTools rather than guessed at — the kind of real-world friction a tutorial rarely shows.

## Author

**Jahnvi Shah**
[GitHub](https://github.com/jahnvishah07) · [LinkedIn](https://www.linkedin.com/in/jahnvi-shah-91808a369/) · [Live Demo](https://churn-frontend-1nb4.onrender.com)