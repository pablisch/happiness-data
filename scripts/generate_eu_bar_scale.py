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
eu_df = df[df["population_EU_only"].notna()]

all_eu_vals = []

for yy in ["21", "22", "23"]:
    cols = [f"{f}_{yy}" for f in FACTORS]
    means = eu_df[cols].mean().to_numpy(dtype=float)
    all_eu_vals.append(means)

all_eu_vals = np.concatenate(all_eu_vals)
all_eu_vals = all_eu_vals[np.isfinite(all_eu_vals)]

eu_min = float(all_eu_vals.min())
eu_max = float(all_eu_vals.max())

print("EU_BAR_XMIN =", 0.0)
print("EU_BAR_XMAX =", eu_max)
print("EU_BAR_EU_MIN_RAW =", eu_min)
print("EU_BAR_EU_MAX_RAW =", eu_max)
