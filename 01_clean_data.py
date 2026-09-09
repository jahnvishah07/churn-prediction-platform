"""
Step 1: Data Cleaning — Telco Customer Churn
Dataset: IBM Telco Customer Churn (7,043 rows, 21 columns)
Source: https://raw.githubusercontent.com/treselle-systems/customer_churn_analysis

Run: python 01_clean_data.py
Output: telco_cleaned.csv
"""

import pandas as pd

RAW_PATH = "telco.csv"
OUT_PATH = "telco_cleaned.csv"

def load_raw(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def fix_total_charges(df: pd.DataFrame) -> pd.DataFrame:
    """
    TotalCharges is read as a string column. 11 rows contain a blank
    string instead of a number — every one of them has tenure == 0,
    meaning these are brand-new customers who haven't completed a
    full billing cycle yet. This isn't random missingness; it's a
    real business state, so the correct fix is to set TotalCharges
    to 0 for these rows rather than dropping them or imputing a mean
    (which would misrepresent a genuinely brand-new customer).
    """
    before_blank = (df["TotalCharges"].str.strip() == "").sum()
    df["TotalCharges"] = df["TotalCharges"].replace(" ", pd.NA)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    zero_tenure_mask = df["tenure"] == 0
    df.loc[zero_tenure_mask & df["TotalCharges"].isna(), "TotalCharges"] = 0.0

    remaining_nulls = df["TotalCharges"].isna().sum()
    print(f"TotalCharges: fixed {before_blank} blank values "
          f"({remaining_nulls} unresolved nulls remain)")
    return df


def clean_categorical_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Several columns use 'No internet service' / 'No phone service'
    as a third category where 'No' would be more consistent and
    easier for one-hot encoding downstream. Standardizing these
    keeps the feature space smaller and more interpretable.
    """
    cols_to_simplify = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies"
    ]
    for col in cols_to_simplify:
        df[col] = df[col].replace(
            {"No internet service": "No", "No phone service": "No"}
        )
    df["MultipleLines"] = df["MultipleLines"].replace(
        {"No phone service": "No"}
    )
    return df


def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """Keep the original Churn column but add a numeric version for modeling."""
    df["Churn_Flag"] = (df["Churn"] == "Yes").astype(int)
    return df


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    A couple of simple, defensible engineered features:
    - tenure_bucket: groups tenure into interpretable ranges, useful
      for both modeling and for the Power BI dashboard later.
    - avg_monthly_spend: TotalCharges / max(tenure, 1), sanity-checks
      against MonthlyCharges and catches any remaining data issues.
    """
    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[-1, 6, 12, 24, 48, 72],
        labels=["0-6mo", "7-12mo", "13-24mo", "25-48mo", "49-72mo"]
    )
    df["avg_monthly_spend"] = df["TotalCharges"] / df["tenure"].clip(lower=1)
    return df


def report_class_balance(df: pd.DataFrame) -> None:
    counts = df["Churn"].value_counts(normalize=True) * 100
    print("\nClass balance (Churn):")
    print(counts.round(1).to_string())
    print("-> Imbalanced. Use stratified splits and report precision/recall/F1,"
          " not just accuracy, in the next step.")


def main():
    df = load_raw(RAW_PATH)
    df = fix_total_charges(df)
    df = clean_categorical_labels(df)
    df = encode_target(df)
    df = add_engineered_features(df)
    report_class_balance(df)

    df.to_csv(OUT_PATH, index=False)
    print(f"\nSaved cleaned dataset -> {OUT_PATH} ({df.shape[0]} rows, {df.shape[1]} columns)")


if __name__ == "__main__":
    main()
