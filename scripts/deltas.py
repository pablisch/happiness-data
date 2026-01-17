from pathlib import Path
import sys

# Ensure repo root is on sys.path (so `import helpers...` works)
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from helpers.pickle_helpers import load_pickle

# Reuse the proven ladder-score extraction logic
from charts.time_line_graph import _compute_series


df = load_pickle("wh")

# -----------------------------
# Identify EU member countries
# -----------------------------
eu_agg_df = df[df["population_EU_only"].notna()]
if eu_agg_df.empty:
    raise ValueError("No EU aggregate rows found (population_EU_only is empty)")

eu_countries = (
    eu_agg_df["country"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

# -----------------------------
# Compute deltas: country - EU
# across all EU countries and all years in _compute_series
# -----------------------------
all_deltas = []

for c in eu_countries:
    years, c_vals, eu_vals = _compute_series(df, c)

    # Make sure types behave (lists/arrays)
    c_arr = np.asarray(c_vals, dtype=float)
    eu_arr = np.asarray(eu_vals, dtype=float)

    deltas = c_arr - eu_arr
    deltas = deltas[np.isfinite(deltas)]
    all_deltas.append(deltas)

all_deltas = np.concatenate(all_deltas) if all_deltas else np.array([], dtype=float)
all_deltas = all_deltas[np.isfinite(all_deltas)]

if all_deltas.size == 0:
    raise ValueError("No finite delta values found")

delta_min = float(all_deltas.min())
delta_max = float(all_deltas.max())

print("EU_DELTA_MIN_RAW =", delta_min)
print("EU_DELTA_MAX_RAW =", delta_max)

# Optional: suggested rounded bounds (outward) for nicer stability
print("SUGGESTED_EU_DELTA_MIN =", round(delta_min - 1e-9, 2))
print("SUGGESTED_EU_DELTA_MAX =", round(delta_max + 1e-9, 2))
