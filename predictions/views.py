import os
import joblib
import pandas as pd
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Load model artifacts once, at server startup, not on every request.
MODEL_PATH = os.path.join(settings.BASE_DIR, "churn_model.joblib")
SCALER_PATH = os.path.join(settings.BASE_DIR, "scaler.joblib")
COLUMNS_PATH = os.path.join(settings.BASE_DIR, "model_columns.joblib")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
model_columns = joblib.load(COLUMNS_PATH)

NUMERIC_FEATURES = ["tenure", "MonthlyCharges", "TotalCharges"]


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
    Returns churn prediction and probability.
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

    return Response({
        "churn_prediction": "Yes" if prediction == 1 else "No",
        "churn_probability": round(probability, 3)
    })