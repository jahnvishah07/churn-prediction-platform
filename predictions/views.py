import os
import joblib
import pandas as pd
from datetime import datetime, timezone
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load model artifacts once, at server startup, not on every request.
MODEL_PATH = os.path.join(settings.BASE_DIR, "churn_model.joblib")
SCALER_PATH = os.path.join(settings.BASE_DIR, "scaler.joblib")
COLUMNS_PATH = os.path.join(settings.BASE_DIR, "model_columns.joblib")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
model_columns = joblib.load(COLUMNS_PATH)

NUMERIC_FEATURES = ["tenure", "MonthlyCharges", "TotalCharges"]

# --- MongoDB setup (also done once at startup, same pattern as the model) ---
# MONGO_URI is read from an environment variable, never hardcoded, so the
# real credentials never end up in source control or a screenshot.
# If it's missing (e.g. running locally without it set), logging is
# silently skipped rather than crashing the whole API — predictions
# should still work even if logging is down.
MONGO_URI = os.environ.get("MONGO_URI")
mongo_client = None
predictions_collection = None

if MONGO_URI:
    try:
        mongo_client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
        db = mongo_client["churn_platform"]
        predictions_collection = db["predictions"]
    except Exception as e:
        print(f"MongoDB connection failed at startup: {e}")
else:
    print("MONGO_URI not set — prediction logging is disabled.")


def log_prediction(input_data: dict, prediction: str, probability: float) -> None:
    """
    Logs one prediction request + result to MongoDB with a timestamp.
    Wrapped in try/except so a logging failure (network blip, auth
    issue, etc.) never breaks the actual prediction response the
    user is waiting on.
    """
    if predictions_collection is None:
        return
    try:
        predictions_collection.insert_one({
            "input": input_data,
            "churn_prediction": prediction,
            "churn_probability": probability,
            "timestamp": datetime.now(timezone.utc),
        })
    except Exception as e:
        print(f"Failed to log prediction to MongoDB: {e}")


@api_view(["POST"])
def predict_churn(request):
    """
    Expects JSON body with raw customer fields, e.g.:
    {
        "tenure": 5, "MonthlyCharges": 70.5, "TotalCharges": 350.0,
        "SeniorCitizen": 0, "Contract": "Month-to-month",
        "InternetService": "Fiber optic", "PaymentMethod": "Electronic check",
        "Partner": "Yes", "Dependents": "No"
    }
    Returns churn prediction and probability. Every request is also
    logged to MongoDB (if configured) for later monitoring/dashboarding.
    """
    data = request.data

    required_fields = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen",
                        "Contract", "InternetService", "PaymentMethod", "Partner", "Dependents"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return Response({"error": f"Missing fields: {missing}"}, status=400)

    input_df = pd.DataFrame([data])
    input_df = pd.get_dummies(
        input_df, columns=["Contract", "InternetService", "PaymentMethod", "Partner", "Dependents"]
    )

    for col in model_columns:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[model_columns]

    input_df[NUMERIC_FEATURES] = scaler.transform(input_df[NUMERIC_FEATURES])

    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0][1])

    churn_prediction = "Yes" if prediction == 1 else "No"
    churn_probability = round(probability, 3)

    log_prediction(data, churn_prediction, churn_probability)

    return Response({
        "churn_prediction": churn_prediction,
        "churn_probability": churn_probability
    })