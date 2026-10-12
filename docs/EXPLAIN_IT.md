# EXPLAIN_IT: a study guide for this project

Use this to practise explaining the project in your own words. Each step has **what I did**, **why**, and **what to say**.

## The project in 60 seconds

"I took a telecom customer dataset and built a model that estimates each customer's chance of leaving. I split the data first
and never touched the test set until the end. I checked that the probabilities are honest, because I multiply them by monthly
charges to estimate revenue at risk. Every customer gets a plain-language reason, for example 'month-to-month contract, new
customer'. I also audited how the model treats groups like gender and seniors, because leaving a column out does not make a
model fair. Power BI shows the results to managers."

## Step by step

| Step | What I did | Why | What to say |
|---|---|---|---|
| 1. Clean (`clean.py`) | Fixed 11 blank `TotalCharges` (all brand-new customers, so set to 0), converted types, checked that no one has add-ons without internet | Bad data in, bad model out. The blank values had a real explanation, so I used it instead of a median | "The blanks were customers with 0 months of tenure, so they had not been billed; 0 is the right value." |
| 2. SQL profiling | Churn rate by contract, tenure, internet type, add-ons, payment method, revenue | Find where churn concentrates before modelling | "Month-to-month and first-year customers churn most." |
| 3. Split (`split.py`) | 70% train / 30% test, same churn share in both, fixed seed | The test set must stay unseen, or the results flatter the model | "I decided nothing about the model using test data." |
| 4. EDA (notebook 02) | Looked at the training data only; found redundant columns and checked for proxies | Decide what the model should use | "`TotalCharges` is almost tenure x monthly charges, so I dropped it." |
| 5. Model (notebook 03) | Logistic regression inside one pipeline; chose `C` by cross-validation | One pipeline means the app later treats raw input exactly like the training data | "Everything that learns from data lives inside the pipeline." |
| 6. Calibration | Compared predicted vs actual churn rates; showed class weights break it | Probabilities feed a money number | "When it says 30%, about 30% churn." |
| 7. Cut-off | Offer when probability is at least 27%, from a cost rule | A cut-off should have a reason | "It balances the cost of a discount against the value of keeping a customer; the inputs are assumptions." |
| 8. Test | Graded the saved model against simple baselines | A model only counts if it beats a simple rule | "ROC-AUC 0.84; at the same number flagged it catches 92% of churners vs 88% for the contract rule." |
| 9. SHAP reasons (notebook 04) | Per-customer pushes, combined back to the 16 original features, turned into short sentences | A bare percentage is hard to act on | "The reasons are template text built from SHAP values, not AI-written." |
| 10. Score everyone | Out-of-fold probabilities, risk bands, revenue at risk | No customer is scored by a model that saw them | "Scores are not inflated by training on the same customers." |
| 11. Fairness table | Flag rate, recall and false-positive rate by gender, seniors, partner, dependents | Dropping a column does not guarantee equal treatment | "Gender is balanced; seniors get flagged nearly twice as often by mistake." |

## One customer's journey (practise saying this in about 90 seconds)

A real row from the scores file: customer **2800-VEQXM**. 3 months with the company, month-to-month contract,
fiber optic internet, no tech support, pays by mailed check, $74.75 a month, and has **not** left yet.

1. **Clean (`clean.py`):** the row passes the checks (numbers are numbers, no add-ons without internet). Helper columns such as `tenure_bucket` are added.
2. **Model (`modeling.py`):** tenure and monthly charges are scaled, the categories become 0/1 columns, and the logistic regression adds up its weights
   into a probability. Month-to-month, fibre and a short tenure all push it up.
3. **Honest score (notebook 04):** the probability, **61.9%**, comes from a model that never saw this customer (out-of-fold).
4. **Risk band:** 50% or more means **High**.
5. **Reasons (SHAP + template):** *"new customer (3 months); month-to-month contract; fiber optic internet"*.
6. **Revenue at risk:** 0.6188 x $74.75 = **$46.26** of expected monthly revenue at risk. It is an expected value, not a forecast.
7. **Power BI (next):** this row appears in the customer table with its band and reasons, so someone knows who to look at first and why.

**The 90-second version:** "Take one customer: three months in, month-to-month, fibre, no tech support. The cleaned row goes into one pipeline that
turns it into numbers and gives a churn probability of 62%. That score is out-of-fold, so the model never saw this customer. High risk means
50% or more. SHAP shows what pushed the score up, and a fixed template turns it into a sentence a manager can read. Multiply the probability by their bill and
you get $46 of monthly revenue at risk. Power BI then shows that row, ranked with everyone else."

## What makes this different from a typical churn project
1. **Split first**, so there is no leakage.
2. **Honest probabilities**: checked, and shown to break with class weights.
3. **A cut-off with a reason** instead of picking 0.5 or chasing recall.
4. **Out-of-fold scoring** for the dashboard.
5. **A group audit**, and an honest note on what it does not prove.

## Questions you might be asked
- **Why logistic regression?** It is easy to explain, its weights can be read directly, and its probabilities are usually already well calibrated.
- **What is overfitting, and how did you guard against it?** Memorising the training data. I used a held-out test set and cross-validation on the training data.
- **Why is accuracy not enough?** About 73% of customers do not churn, so "always predict no churn" scores 73.5% and catches nobody.
- **What is the difference between recall and precision?** Recall: of real churners, how many I flagged. Precision: of those I flagged, how many really churned.
- **What does ROC-AUC mean?** The chance that a randomly chosen churner gets a higher score than a randomly chosen loyal customer (0.84 here).
- **What would you do with more time?** Compare against a random forest, run an A/B test on retention offers, and train with a fairness constraint (Project 3).
- **What are the limits?** No time dimension, assumed offer economics, and the reasons show what the model uses, not what causes churn.
- **Is revenue at risk a forecast?** No. It is an exposure score for customers who resemble past churners.

## Words to know
- **One-hot encoding:** turning a category (like contract type) into 0/1 columns.
- **Cross-validation:** splitting the training data into parts and rotating which part is held back, to check a setting fairly.
- **Out-of-fold:** a prediction made by a model that did not see that customer.
- **Log-loss / Brier score:** error scores for probabilities (lower is better). Log-loss punishes confident wrong answers.
- **Calibration:** whether predicted probabilities match real frequencies.
- **False-positive rate:** of customers who stayed, the share I flagged anyway.

## The scores file (what Power BI reads): `data/processed/telco_predictive_scores.csv`
One row per customer (7,043). Besides the cleaned original columns it has:

| Column | Meaning |
|---|---|
| `churn_flag` | 1 if the customer already left, else 0 |
| `churn_probability` | Out-of-fold probability (0 to 1) of resembling past churners |
| `risk_band` / `risk_band_order` | Low (below 27%), Medium (27% to under 50%), High (50% or more) / 1, 2, 3 for sorting |
| `is_active` | True if the customer has not left (`Churn = No`) |
| `expected_monthly_revenue_at_risk` | `churn_probability x MonthlyCharges` for active customers; 0 for customers who already left |
| `top_reasons` | Up to three plain-language reasons for customers at or above 27%; "low risk" otherwise |
| `tenure_bucket`, `addon_count` | Helper columns for SQL and Power BI (not model inputs) |

## Honest limits to mention
No time dimension; the offer economics are assumed; one test set with 561 churners, so small gaps are noise; reasons show what the model uses, not causes.
