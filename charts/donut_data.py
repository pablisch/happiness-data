from typing import Any, Dict, List
import numpy as np
import pandas as pd


def compute_factor_donut(
    df: pd.DataFrame,
    factor: str,
    year: int | str,
    eu_only: bool = True,
    top_n: int = 8,
    group_other: bool = True,
    clamp_negative_to_zero: bool = True,
) -> Dict[str, Any]:
    """
    Returns JSON-friendly dict:
      {
        "factor": "<factor>",
        "year": 2023,
        "total": 123.45,
        "rows": [
          {"country": "Germany", "value": 12.34, "proportion": 0.10},
          ...
          {"country": "Other EU", "value": 34.56, "proportion": 0.28}   # only if group_other=True
        ]
      }

    Notes:
    - Values are computed as mean per country for the requested factor-year column.
    - Donut proportions require non-negative mass; if clamp_negative_to_zero=True,
      negative values are clipped to 0 and then removed if still <=0.
    - When group_other=False, one slice per EU country is returned (no "Other EU").

    Special case:
    - factor == "combined_score" uses ladder_score_YY (e.g. ladder_score_23)
    """
    # --- column naming ---
    year_str = str(year)
    if len(year_str) == 4:
        year_str = year_str[-2:]

    # ✅ Special-case: combined score is the overall ladder score column
    if factor == "combined_score":
        value_col = f"ladder_score_{year_str}"
    else:
        value_col = f"{factor}_{year_str}"

    if value_col not in df.columns:
        raise ValueError(f"Missing column '{value_col}'")

    if "country" not in df.columns:
        raise ValueError("Expected a 'country' column")

    # --- Identify EU member countries (based on your existing approach) ---
    if "population_EU_only" in df.columns:
        eu_agg_df = df[df["population_EU_only"].notna()].copy()
        if eu_agg_df.empty:
            raise ValueError("No EU aggregate rows found (population_EU_only is empty)")

        eu_countries = (
            eu_agg_df["country"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )
    else:
        eu_countries = (
            df["country"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

    eu_countries = [c for c in eu_countries if c]

    # --- Country rows only, normalised ---
    country_rows = df[df["country"].notna()].copy()
    country_rows["country"] = country_rows["country"].astype(str).str.strip()
    country_rows = country_rows[country_rows["country"] != ""]

    if eu_only:
        country_rows = country_rows[country_rows["country"].isin(eu_countries)]

    if country_rows.empty:
        return {"factor": factor, "year": int(year), "total": 0.0, "rows": []}

    # --- Compute mean per country for the requested column ---
    country_means = country_rows.groupby("country")[value_col].mean()

    # Ensure numeric & finite
    country_means = pd.to_numeric(country_means, errors="coerce")
    country_means = country_means[np.isfinite(country_means.values)]

    if country_means.empty:
        return {"factor": factor, "year": int(year), "total": 0.0, "rows": []}

    # Donut "mass" handling
    if clamp_negative_to_zero:
        country_means = country_means.clip(lower=0.0)

    # Remove non-positive values (donut proportions need positive totals)
    country_means = country_means[country_means > 0.0]

    if country_means.empty:
        return {"factor": factor, "year": int(year), "total": 0.0, "rows": []}

    # Sort largest first
    country_means = country_means.sort_values(ascending=False)

    total_value = float(country_means.sum())
    if not np.isfinite(total_value) or total_value <= 0.0:
        return {"factor": factor, "year": int(year), "total": 0.0, "rows": []}

    rows: List[Dict[str, Any]] = []

    if group_other:
        top_series = country_means.head(top_n)
        remainder_series = country_means.iloc[top_n:]

        for country_name, value in top_series.items():
            value_float = float(value)
            rows.append(
                {
                    "country": str(country_name),
                    "value": value_float,
                    "proportion": value_float / total_value,
                }
            )

        if not remainder_series.empty:
            remainder_sum = float(remainder_series.sum())
            rows.append(
                {
                    "country": "Other EU",
                    "value": remainder_sum,
                    "proportion": remainder_sum / total_value,
                }
            )
    else:
        for country_name, value in country_means.items():
            value_float = float(value)
            rows.append(
                {
                    "country": str(country_name),
                    "value": value_float,
                    "proportion": value_float / total_value,
                }
            )

    return {"factor": factor, "year": int(year), "total": total_value, "rows": rows}
