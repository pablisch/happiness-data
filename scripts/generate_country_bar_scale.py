from pathlib import Path
import sys

# Ensure repo root is on sys.path (so `import helpers...` works)
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from helpers.pickle_helpers import load_pickle

FACTORS = [
    "GDP",
    "social_support",
    "life_expectancy",
    "freedom",
    "generosity",
    "corruption",
    "other",
]

df = load_pickle("wh")

# -----------------------------
# Identify EU member countries
# -----------------------------

# EU aggregate rows (used to compute EU averages)
eu_agg_df = df[df["population_EU_only"].notna()]

if eu_agg_df.empty:
    raise ValueError("No EU aggregate rows found (population_EU_only is empty)")

# The countries contributing to EU aggregates
# (assumes the same 'country' naming is used)
eu_countries = (
    eu_agg_df["country"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

# -----------------------------
# Filter to EU member country rows
# -----------------------------
if "country" not in df.columns:
    raise ValueError("Expected a 'country' column")

country_df = df[df["country"].notna()].copy()
country_df["country"] = country_df["country"].astype(str).str.strip()
country_df = country_df[country_df["country"].isin(eu_countries)]

if country_df.empty:
    raise ValueError("No EU member country rows found")

# -----------------------------
# Collect factor values
# -----------------------------
all_vals = []

for yy in ["21", "22", "23"]:
    cols = [f"{f}_{yy}" for f in FACTORS]

    missing = [c for c in cols if c not in country_df.columns]
    if missing:
        raise ValueError(f"Missing expected columns for year 20{yy}: {missing}")

    vals = country_df[cols].to_numpy(dtype=float).ravel()
    all_vals.append(vals)

all_vals = np.concatenate(all_vals)
all_vals = all_vals[np.isfinite(all_vals)]

eu_min = float(all_vals.min())
eu_max = float(all_vals.max())

print("EU_COUNTRY_MIN_RAW =", eu_min)
print("EU_COUNTRY_MAX_RAW =", eu_max)

print("SUGGESTED_FIXED_BAR_XMIN =", eu_min)
print("SUGGESTED_FIXED_BAR_XMAX =", eu_max)
