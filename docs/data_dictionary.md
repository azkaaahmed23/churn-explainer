# Data dictionary

One row per customer (7,043). The first 21 columns come from the Kaggle "Telco Customer Churn" file; `clean.py` adds the
next 3; notebook 04 adds the last 6 (the file Power BI reads, `data/processed/telco_predictive_scores.csv`).

**Model use:** *input* = the model sees it. *audit* = kept so we can check how the model treats groups, but the model does not see it.
*not used* = left out on purpose. *result* = produced by the model or derived from its output.

## Original columns

| Column | Meaning | Values | Model use |
|---|---|---|---|
| `customerID` | Unique customer code | e.g. 7590-VHVEG | not used |
| `gender` | Customer gender | Female, Male | audit |
| `SeniorCitizen` | Senior citizen? | 0 = no, 1 = yes | audit |
| `Partner` | Has a partner | Yes, No | input |
| `Dependents` | Has dependents (children, etc.) | Yes, No | input |
| `tenure` | Months as a customer | 0 to 72 | input |
| `PhoneService` | Has phone service | Yes, No | input |
| `MultipleLines` | Has more than one phone line | Yes, No, No phone service | input |
| `InternetService` | Type of internet | DSL, Fiber optic, No | input |
| `OnlineSecurity` | Has the online-security add-on | Yes, No, No internet service | input |
| `OnlineBackup` | Has the online-backup add-on | Yes, No, No internet service | input |
| `DeviceProtection` | Has the device-protection add-on | Yes, No, No internet service | input |
| `TechSupport` | Has the tech-support add-on | Yes, No, No internet service | input |
| `StreamingTV` | Streams TV through the company | Yes, No, No internet service | input |
| `StreamingMovies` | Streams movies through the company | Yes, No, No internet service | input |
| `Contract` | Contract length | Month-to-month, One year, Two year | input |
| `PaperlessBilling` | Gets paperless bills | Yes, No | input |
| `PaymentMethod` | How the customer pays | Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic) | input |
| `MonthlyCharges` | Current monthly bill in dollars | 18.25 to 118.75 | input |
| `TotalCharges` | Total billed so far in dollars. Blank in the raw file for 11 brand-new customers (tenure 0); `clean.py` sets those to 0 | 0 to 8,684.80 | not used (almost equal to tenure x MonthlyCharges) |
| `Churn` | Did the customer leave? | Yes = already left, No = still a customer | the answer the model learns |

## Added by `clean.py`

| Column | Meaning | Values | Model use |
|---|---|---|---|
| `churn_flag` | `Churn` as a number | 1 = left, 0 = stayed | the answer the model learns |
| `tenure_bucket` | Tenure grouped for SQL and Power BI | 1. 0-12 months, 2. 13-24 months, 3. 25-48 months, 4. 49-72 months | not used |
| `addon_count` | How many of the six add-ons the customer has (OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies) | 0 to 6 | not used |

## Added by notebook 04 (the scores file)

| Column | Meaning | Values | Model use |
|---|---|---|---|
| `churn_probability` | Out-of-fold chance that this customer resembles past churners (never scored by a model that saw them) | 0 to 1 | result |
| `top_reasons` | Up to three plain-language reasons (from SHAP, filled into a fixed template) for customers at or above the 27% cut-off | text, or "low risk" | result |
| `risk_band` | Low = below 27%, Medium = 27% to under 50%, High = 50% or more | Low, Medium, High | result |
| `risk_band_order` | 1, 2, 3 so Power BI sorts the bands correctly | 1, 2, 3 | result |
| `is_active` | Customer has not left (`Churn = No`) | True, False | result |
| `expected_monthly_revenue_at_risk` | `churn_probability` x `MonthlyCharges` for active customers; 0 for customers who already left | dollars | result |

## Things to remember when reading these columns
- `Churn = Yes` means the customer **already left**. The data has no dates, so scores say "resembles past churners", not "will leave next quarter".
- `expected_monthly_revenue_at_risk` is an expected value (probability x money), not a forecast and not customer lifetime value.
- In the model, "No internet service" and "No phone service" are treated as plain "No" (`src/modeling.py`), but the data keeps the original labels so charts can tell "no internet" apart from "has internet but no security".
