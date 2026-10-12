"""Phase 1: deterministic cleaning of the Telco churn data.

Reads  data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
Writes data/processed/telco_clean.csv

Design notes
- This script does NOT split, scale, or impute with statistics. Anything learned from data
  (medians, scalers, encoders) belongs inside the sklearn Pipeline after the train/test split.
  The only "imputation" here is a known business rule: TotalCharges is blank for tenure-0
  customers (they haven't been billed yet), so it is 0, not a median.
- `gender` is KEPT in the cleaned file so the subgroup audit in Phase 4 can use it. It is dropped
  from the model's feature matrix later, not here.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
OUT = ROOT / "data" / "processed" / "telco_clean.csv"

ADDON_COLS = [
    "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies",
]
INTERNET_DEPENDENT = ADDON_COLS


def tenure_bucket(months: int) -> str:
    """Ordered labels so they sort correctly in SQL and Power BI."""
    if months <= 12:
        return "1. 0-12 months"
    if months <= 24:
        return "2. 13-24 months"
    if months <= 48:
        return "3. 25-48 months"
    return "4. 49-72 months"


def main() -> None:
    if not RAW.exists():
        raise SystemExit(
            f"Raw file not found: {RAW}\n"
            "Download 'Telco Customer Churn' from Kaggle and save it at that path."
        )

    df = pd.read_csv(RAW, dtype=str)  # read everything as text first, convert deliberately
    print(f"Loaded {len(df):,} rows x {df.shape[1]} columns")

    # 1. Strip stray whitespace in every text column
    df = df.apply(lambda s: s.str.strip())

    # 2. Integrity checks before touching anything
    assert df["customerID"].is_unique, "customerID is not unique"
    assert not df.duplicated().any(), "fully duplicated rows found"

    # 3. Numeric conversions
    df["tenure"] = pd.to_numeric(df["tenure"], errors="raise").astype(int)
    df["SeniorCitizen"] = pd.to_numeric(df["SeniorCitizen"], errors="raise").astype(int)
    df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="raise")

    # 4. TotalCharges: blanks are tenure-0 customers -> 0 (verified, not assumed)
    total = pd.to_numeric(df["TotalCharges"], errors="coerce")
    blank = total.isna()
    print(f"Blank TotalCharges: {blank.sum()} (tenure values: {sorted(int(t) for t in df.loc[blank, 'tenure'].unique())})")
    assert (df.loc[blank, "tenure"] == 0).all(), "blank TotalCharges outside tenure-0 customers"
    df["TotalCharges"] = total.fillna(0.0)

    # 5. Logical dependency checks (add-ons require internet; multiple lines require phone)
    no_net = df["InternetService"] == "No"
    for col in INTERNET_DEPENDENT:
        bad = (no_net & (df[col] != "No internet service")).sum()
        assert bad == 0, f"{col}: {bad} rows have add-on without internet service"
    bad_lines = ((df["PhoneService"] == "No") & (df["MultipleLines"] != "No phone service")).sum()
    assert bad_lines == 0, f"{bad_lines} rows have MultipleLines without phone service"
    print("Dependency checks passed (no add-ons without internet, no extra lines without phone)")

    # 6. Target: keep readable text AND a 0/1 flag
    assert set(df["Churn"].unique()) == {"Yes", "No"}, "unexpected Churn values"
    df["churn_flag"] = (df["Churn"] == "Yes").astype(int)

    # 7. Analysis helper columns (descriptive only; the model learns from the raw columns)
    df["tenure_bucket"] = df["tenure"].map(tenure_bucket)
    df["addon_count"] = (df[ADDON_COLS] == "Yes").sum(axis=1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    print(f"Churn rate: {df['churn_flag'].mean():.1%}")
    print(f"Wrote {len(df):,} rows -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
