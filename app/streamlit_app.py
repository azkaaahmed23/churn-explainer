"""A thin demo: type in one customer's details, see the model's churn risk and what drives it.

Run from the project folder:  streamlit run app/streamlit_app.py
It only LOADS the saved pipeline (models/churn_pipeline.joblib). It does no training.
"""
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))   # the saved model needs `import modeling`
import modeling  # noqa: E402


@st.cache_resource
def load_everything():
    pipeline = joblib.load(ROOT / "models" / "churn_pipeline.joblib")
    config = json.loads((ROOT / "models" / "model_config.json").read_text())
    train = pd.read_csv(ROOT / "data" / "processed" / "train.csv")
    X_train, _ = modeling.split_xy(train)
    return pipeline, config, X_train


def parent_feature(encoded_name):
    """'Contract_One year' -> 'Contract' (same idea as notebook 04)."""
    for f in modeling.FEATURES:
        if encoded_name == f or encoded_name.startswith(f + "_"):
            return f


pipeline, config, X_train = load_everything()
cutoff = config["threshold"]

st.title("Churn risk for one customer")
st.caption("Demo of the Project 2 model. Risk means 'resembles past customers who left', not a prediction of next month.")

# ---- 1. The form: one box per model input ---------------------------------
def pick(label, column, **kw):
    return st.sidebar.selectbox(label, sorted(X_train[column].unique()), **kw)

st.sidebar.header("Customer details")
row = {}
row["tenure"] = st.sidebar.slider("Months as a customer", 0, 72, 12)
row["MonthlyCharges"] = st.sidebar.number_input("Monthly bill ($)", 18.0, 120.0, 70.0, step=1.0)
row["Contract"] = pick("Contract", "Contract")
row["PaymentMethod"] = pick("Payment method", "PaymentMethod")
row["PaperlessBilling"] = pick("Paperless billing", "PaperlessBilling")
row["Partner"] = pick("Has a partner", "Partner")
row["Dependents"] = pick("Has dependents", "Dependents")
row["PhoneService"] = pick("Phone service", "PhoneService")
row["InternetService"] = pick("Internet service", "InternetService", index=0)

# Add-ons only make sense with internet, and extra lines only with a phone (same rule as the data).
if row["PhoneService"] == "No":
    row["MultipleLines"] = "No phone service"
else:
    row["MultipleLines"] = st.sidebar.selectbox("Multiple lines", ["No", "Yes"])
for col in modeling.ADDON_COLS:
    if row["InternetService"] == "No":
        row[col] = "No internet service"
    else:
        row[col] = st.sidebar.selectbox(col, ["No", "Yes"])

customer = pd.DataFrame([row])[modeling.FEATURES]

# ---- 2. The model's answer -------------------------------------------------
probability = float(pipeline.predict_proba(customer)[0, 1])
band = "High" if probability >= 0.50 else ("Medium" if probability >= cutoff else "Low")
at_risk = probability * row["MonthlyCharges"]

c1, c2, c3 = st.columns(3)
c1.metric("Churn probability", f"{probability:.1%}")
c2.metric("Risk band", band)
c3.metric("Expected revenue at risk / month", f"${at_risk:,.2f}")
st.write(f"Bands: Low below {cutoff:.0%}, Medium {cutoff:.0%} to 50%, High 50% or more. "
         "Revenue at risk = probability x monthly bill (assumes the customer is still active).")

# ---- 3. Why? Each feature's push = weight x (value - training average) ------
prep, clf = pipeline[:-1], pipeline[-1]
names = prep.get_feature_names_out()
now = prep.transform(customer)[0]
average = prep.transform(X_train).mean(axis=0)
pushes = pd.Series(clf.coef_[0] * (now - average), index=names)
pushes = pushes.groupby([parent_feature(n) for n in names]).sum().sort_values()

st.subheader("What moves this customer's risk")
st.caption("Right of zero = pushes risk UP compared with an average training customer; left = pushes it down. "
           "Units are log-odds (the model's internal scale), so compare bar lengths, not exact percentages. "
           "This shows what the model uses, not what causes churn.")
st.bar_chart(pushes)
