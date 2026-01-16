from pathlib import Path
import sys
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

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

records = []

for yy in ["21", "22", "23"]:
    for f in FACTORS:
        col = f"{f}_{yy}"
        if col not in df.columns:
            continue

        vals = df[col].to_numpy(dtype=float)
        mask = np.isfinite(vals)

        for idx in np.where(mask)[0]:
            records.append({
                "country": df.loc[idx, "country"],
                "factor": f,
                "year": f"20{yy}",
                "value": vals[idx],
                "row": idx,
            })

# Find global minimum
min_rec = min(records, key=lambda r: r["value"])

print("MOST NEGATIVE VALUE FOUND")
for k, v in min_rec.items():
    print(f"{k}: {v}")
