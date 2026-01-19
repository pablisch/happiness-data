# export_analysis_pack.py
#
# One-off script to extract a MINIMAL analysis dataset
# from the same pickle your dashboard already uses.
#
# Output:
#   factor_spread.csv  ← this is what you upload to ChatGPT

import numpy as np
import pandas as pd

from helpers.pickle_helpers import load_pickle
from helpers.data_filter import filter_to_eu_only


def wide_to_tidy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert your wide EU dataset:
      ladder_score_21, GDP_21, ...
      ladder_score_22, GDP_22, ...
    into tidy rows:
      country | year | ladder_score | GDP | ...
    """
    year_map = {
        "21": 2021,
        "22": 2022,
        "23": 2023,
    }

    pieces = []

    for suffix, year in year_map.items():
        year_cols = [c for c in df.columns if c.endswith(f"_{suffix}")]
        if not year_cols:
            continue

        sub = df[["country"] + year_cols].copy()
        sub.columns = ["country"] + [c.replace(f"_{suffix}", "") for c in year_cols]
        sub["year"] = year
        pieces.append(sub)

    tidy = pd.concat(pieces, ignore_index=True)

    for c in tidy.columns:
        if c not in ("country", "year"):
            tidy[c] = pd.to_numeric(tidy[c], errors="coerce")

    return tidy.sort_values(["year", "country"]).reset_index(drop=True)


def main():
    # Load EXACT same data as dashboard
    df = load_pickle("wh")
    df = filter_to_eu_only(df)

    df = df.replace([np.inf, -np.inf], np.nan)

    tidy = wide_to_tidy(df)

    # Long form for stats
    metrics = [c for c in tidy.columns if c not in ("country", "year")]
    long = tidy.melt(
        id_vars=["country", "year"],
        value_vars=metrics,
        var_name="metric",
        value_name="value",
    ).dropna(subset=["value"])

    g = long.groupby(["year", "metric"])["value"]

    spread = g.agg(
        n="count",
        min="min",
        max="max",
        mean="mean",
        std="std",
        median="median",
    ).reset_index()

    q = g.quantile([0.25, 0.75]).unstack(level=-1).reset_index()
    q = q.rename(columns={0.25: "q25", 0.75: "q75"})

    spread = spread.merge(q, on=["year", "metric"], how="left")
    spread["range"] = spread["max"] - spread["min"]
    spread["iqr"] = spread["q75"] - spread["q25"]

    spread = spread.sort_values(["year", "metric"]).reset_index(drop=True)

    spread.to_csv("factor_spread.csv", index=False)

    print("✔ Wrote factor_spread.csv")
    print("Rows:", len(spread))
    print("Metrics:", spread['metric'].unique().tolist())


if __name__ == "__main__":
    main()
