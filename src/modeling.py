"""The model recipe, used by notebooks 03 and 04 (and by the optional Streamlit app later).

Why one file? Every preprocessing step lives inside ONE scikit-learn Pipeline built here:
  relabel -> fill gaps -> scale numbers -> one-hot encode categories -> logistic regression.
So raw customer details go in, a churn probability comes out, and training and the app treat data identically.

Note for loading the saved model: joblib remembers `recode_service_levels` by name, so a script that calls
joblib.load() must be able to `import modeling` (the notebooks add the src/ folder to the path for this).
"""
from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

TARGET = "churn_flag"

NUMERIC = ["tenure", "MonthlyCharges"]
ADDON_COLS = [
    "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies",
]
CATEGORICAL = [
    "Partner", "Dependents", "PhoneService", "MultipleLines", "InternetService",
    *ADDON_COLS,
    "Contract", "PaperlessBilling", "PaymentMethod",
]
FEATURES = NUMERIC + CATEGORICAL  # the 16 model inputs; why these: notebooks/02_eda_train.ipynb, section 8

# Kept in the data for the fairness audit, deliberately NOT given to the model.
AUDIT_COLS = ["gender", "SeniorCitizen"]


def recode_service_levels(X: pd.DataFrame) -> pd.DataFrame:
    """Relabel "No internet service" / "No phone service" as plain "No".

    Those labels only repeat InternetService = "No" and PhoneService = "No" (checked in the EDA notebook).
    This step learns nothing from the data, so it cannot leak. It lives here, not in clean.py, so the
    cleaned data keeps the original labels (a Power BI chart can then tell "no internet" from "no security").
    """
    X = X.copy()
    for col in ADDON_COLS:
        X[col] = X[col].replace("No internet service", "No")
    X["MultipleLines"] = X["MultipleLines"].replace("No phone service", "No")
    return X


def build_pipeline(C: float = 1.0, class_weight: str | None = None) -> Pipeline:
    """Raw feature columns in, churn probability out."""
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(drop="if_binary", handle_unknown="ignore", sparse_output=False)),
    ])
    prep = ColumnTransformer(
        [("num", numeric, NUMERIC), ("cat", categorical, CATEGORICAL)],
        verbose_feature_names_out=False,
    )
    return Pipeline([
        ("recode", FunctionTransformer(recode_service_levels, feature_names_out="one-to-one")),
        ("prep", prep),
        ("clf", LogisticRegression(C=C, class_weight=class_weight, max_iter=2000)),
    ])


def split_xy(df: pd.DataFrame):
    """Feature frame and 0/1 target from a cleaned/split CSV."""
    return df[FEATURES].copy(), df[TARGET].to_numpy()
