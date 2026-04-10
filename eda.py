"""
Exploratory Data Analysis — Online Shoppers Purchasing Intention
================================================================
Generates a ydata-profiling HTML report and prints key summary statistics
to stdout.

Usage:
    python eda.py

Output:
    eda_report.html   — full interactive profiling report
"""

import pathlib
import pandas as pd
from ydata_profiling import ProfileReport

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_PATH = pathlib.Path(__file__).parent / "online_shoppers_intention.csv"
REPORT_PATH = pathlib.Path(__file__).parent / "eda_report.html"

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("Loading data...")
df = pd.read_csv(DATA_PATH)

# Fix dtypes for profiling clarity
bool_cols = ["Weekend", "Revenue"]
for col in bool_cols:
    df[col] = df[col].astype(bool)

cat_cols = ["Month", "VisitorType"]
for col in cat_cols:
    df[col] = df[col].astype("category")

print(f"  Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

# ---------------------------------------------------------------------------
# Quick console summary
# ---------------------------------------------------------------------------
print("\n--- Column types ---")
print(df.dtypes.to_string())

print("\n--- Missing values ---")
missing = df.isnull().sum()
print(missing[missing > 0].to_string() if missing.any() else "  No missing values.")

print("\n--- Target distribution (Revenue) ---")
vc = df["Revenue"].value_counts()
for val, count in vc.items():
    print(f"  {str(val):>5}: {count:>6,}  ({count / len(df) * 100:.1f}%)")

print("\n--- Visitor type distribution ---")
print(df["VisitorType"].value_counts().to_string())

print("\n--- Session month distribution ---")
month_order = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "June",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
month_counts = (
    df["Month"]
    .value_counts()
    .reindex([m for m in month_order if m in df["Month"].cat.categories])
)
print(month_counts.to_string())

print("\n--- Numeric feature summary ---")
numeric_cols = df.select_dtypes(include="number").columns.tolist()
print(df[numeric_cols].describe().round(3).to_string())

print("\n--- Revenue rate by visitor type ---")
print(
    df.groupby("VisitorType", observed=True)["Revenue"]
    .mean()
    .mul(100)
    .round(1)
    .rename("purchase_rate_%")
    .to_string()
)

print("\n--- Revenue rate by month ---")
month_revenue = (
    df.groupby("Month", observed=True)["Revenue"]
    .mean()
    .mul(100)
    .round(1)
    .rename("purchase_rate_%")
)
print(month_revenue.to_string())

print("\n--- Revenue rate: weekday vs weekend ---")
print(
    df.groupby("Weekend")["Revenue"]
    .mean()
    .mul(100)
    .round(1)
    .rename("purchase_rate_%")
    .to_string()
)

print("\n--- Correlation with Revenue (numeric features) ---")
# Encode Revenue as 0/1 for correlation
df_corr = df.copy()
df_corr["Revenue_int"] = df_corr["Revenue"].astype(int)
corr = (
    df_corr[numeric_cols + ["Revenue_int"]]
    .corr()["Revenue_int"]
    .drop("Revenue_int")
    .sort_values(key=abs, ascending=False)
)
print(corr.round(3).to_string())

# ---------------------------------------------------------------------------
# ydata-profiling report
# ---------------------------------------------------------------------------
print("\nGenerating ydata-profiling report (this may take a minute)...")

profile = ProfileReport(
    df,
    title="Online Shoppers Purchasing Intention — EDA Report",
    dataset={
        "description": (
            "Session-level data from an e-commerce website. "
            "Target variable 'Revenue' indicates whether the session ended in a purchase. "
            "Source: Sakar et al. (2019), doi:10.1007/s00521-018-3523-0"
        ),
        "url": "https://doi.org/10.1007/s00521-018-3523-0",
    },
    # Correlations: include Cramér's V for categoricals
    correlations={
        "pearson": {"calculate": True},
        "spearman": {"calculate": True},
        "cramers": {"calculate": True},
    },
    # Interaction plots for top numeric pairs
    interactions={
        "continuous": True,
        "targets": ["Revenue"],
    },
    missing_diagrams={
        "bar": True,
        "matrix": False,
        "heatmap": False,
    },
    explorative=True,
    progress_bar=True,
)

profile.to_file(REPORT_PATH)
print(f"\nReport saved to: {REPORT_PATH}")
print("Open eda_report.html in a browser to explore the full interactive report.")
