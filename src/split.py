"""Step 3: split the customers into a training set (70%) and a test set (30%), ONCE, before any modelling.

Reads  data/processed/telco_clean.csv
Writes data/processed/train.csv and data/processed/test.csv

The rules for the rest of the project
- Anything the model LEARNS from data (averages for scaling, category lists, coefficients, the threshold)
  is learned from train.csv only.
- test.csv is used once, at the very end of notebooks/03_model.ipynb, to grade the finished model.
  It is never used to explore the data or to choose settings.
"""
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
CLEAN_CSV = ROOT / "data" / "processed" / "telco_clean.csv"
TRAIN_CSV = ROOT / "data" / "processed" / "train.csv"
TEST_CSV = ROOT / "data" / "processed" / "test.csv"

RANDOM_STATE = 42   # fixed seed, so everyone gets the same split
TEST_SIZE = 0.30


def main() -> None:
    if not CLEAN_CSV.exists():
        raise SystemExit("Run `python src/clean.py` first.")

    df = pd.read_csv(CLEAN_CSV)

    # stratify = keep the same churn share (about 26.5%) in both parts
    train, test = train_test_split(
        df, test_size=TEST_SIZE, stratify=df["churn_flag"], random_state=RANDOM_STATE
    )
    train = train.sort_values("customerID").reset_index(drop=True)
    test = test.sort_values("customerID").reset_index(drop=True)

    # Safety checks: stop loudly if anything is off
    assert len(train) + len(test) == len(df), "rows were lost or duplicated"
    assert set(train["customerID"]).isdisjoint(test["customerID"]), "a customer is in both sets"

    train.to_csv(TRAIN_CSV, index=False)
    test.to_csv(TEST_CSV, index=False)

    for name, part in (("train", train), ("test", test)):
        print(f"{name:<5} {len(part):>5,} rows | churned {int(part['churn_flag'].sum()):>5,} ({part['churn_flag'].mean():.2%})")
    print("Wrote train.csv and test.csv to data/processed/")


if __name__ == "__main__":
    main()
