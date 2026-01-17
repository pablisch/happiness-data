# # charts/score_card.py
#
# from typing import Any
# import numpy as np
# import pandas as pd
#
# from charts.time_line_graph import _compute_series
#
# from charts.chart_style import (
#     EU_DELTA_MIN,
#     EU_DELTA_MAX,
# )
#
#
# def build_score_card_title(geo_area: str, year: int | str, show_eu: bool = False) -> str:
#     year_str = str(year)
#     if len(year_str) == 4:
#         year_str = year_str[-2:]
#     year_full = f"20{year_str}"
#     return f"Happiness (ladder) score for {geo_area} in {year_full}" + (" vs EU average" if show_eu else "")
#
#
# def get_score_card_values(df: pd.DataFrame, geo_area: str, year: int | str) -> dict[str, Any]:
#     years, c_vals, eu_vals = _compute_series(df, geo_area)
#
#     year_int = int(year)
#     if year_int not in years:
#         raise ValueError(f"Year {year_int} not available in series: {years}")
#
#     # Convert to simple year->value maps (None-safe)
#     c_by_year: dict[int, float | None] = {}
#     eu_by_year: dict[int, float | None] = {}
#
#     for y, cv, ev in zip(years, c_vals, eu_vals):
#         yi = int(y)
#         c_by_year[yi] = float(cv) if np.isfinite(cv) else None
#         eu_by_year[yi] = float(ev) if np.isfinite(ev) else None
#
#     # Current year values
#     c = c_by_year.get(year_int)
#     eu = eu_by_year.get(year_int)
#
#     delta_vs_eu = None
#     if c is not None and eu is not None:
#         delta_vs_eu = c - eu
#
#     # NEW: 3-year deltas vs selected year
#     base = c  # selected year's country score
#     deltas_vs_selected_year: dict[int, float | None] = {}
#     for yy in [2021, 2022, 2023]:
#         v = c_by_year.get(yy)
#         if base is None or v is None:
#             deltas_vs_selected_year[yy] = None
#         else:
#             deltas_vs_selected_year[yy] = v - base
#
#     # Keep your existing keys exactly, add new ones
#     return {
#         # existing fields
#         "year": year_int,
#         "country_score": c,
#         "eu_score": eu,
#         "delta_vs_eu": delta_vs_eu,
#         "delta_min": EU_DELTA_MIN,
#         "delta_max": EU_DELTA_MAX,
#
#         # NEW fields for the 3-year row
#         "years": [2021, 2022, 2023],
#         "selected_year": year_int,
#         "deltas_vs_selected_year": deltas_vs_selected_year,
#
#         # NEW: colour scale bounds for these year-deltas (starting rule)
#         "year_delta_min": -0.5,
#         "year_delta_max": 0.5,
#     }

# charts/score_card.py

from typing import Any
import numpy as np
import pandas as pd

from charts.time_line_graph import _compute_series
from charts.chart_style import EU_DELTA_MIN, EU_DELTA_MAX


FACTORS = [
    "GDP",
    "social_support",
    "life_expectancy",
    "freedom",
    "generosity",
    "corruption",
    "other",
]

FACTOR_LABELS = {
    "GDP": "GDP",
    "social_support": "Social support",
    "life_expectancy": "Life expectancy",
    "freedom": "Freedom",
    "generosity": "Generosity",
    "corruption": "Corruption (low = better)",
    "other": "Residual (other)",
}

# If you want "lower is better" for a factor, set -1.
# NOTE: These are *contributions to ladder score* in your dataset; most likely "higher is better"
# even for corruption, but keep this here in case you later confirm you want inversion.
FACTOR_DIRECTION = {
    "GDP": 1,
    "social_support": 1,
    "life_expectancy": 1,
    "freedom": 1,
    "generosity": 1,
    "corruption": 1,
    "other": 1,
}


def build_score_card_title(geo_area: str, year: int | str, show_eu: bool = False) -> str:
    year_str = str(year)
    if len(year_str) == 4:
        year_str = year_str[-2:]
    year_full = f"20{year_str}"
    return f"Happiness (ladder) score for {geo_area} in {year_full}" + (" vs EU average" if show_eu else "")


def _eu_country_list(df: pd.DataFrame) -> list[str]:
    if "population_EU_only" not in df.columns:
        raise ValueError("EU logic requires 'population_EU_only' column")

    eu_agg_df = df[df["population_EU_only"].notna()].copy()
    if eu_agg_df.empty:
        raise ValueError("No EU rows found (population_EU_only is empty)")

    if "country" not in eu_agg_df.columns:
        raise ValueError("EU logic requires 'country' column")

    eu_countries = (
        eu_agg_df["country"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )
    return [c for c in eu_countries if c]


def _year_suffix(year: int | str) -> str:
    ys = str(year)
    if len(ys) == 4:
        ys = ys[-2:]
    return ys


def _rank_desc(values_by_country: dict[str, float | None]) -> tuple[dict[str, int | None], int]:
    """
    Rank 1 = best (largest), rank N = worst (smallest).
    Countries with None are unranked (rank=None).
    Returns: (rank_by_country, total_ranked)
    """
    items = [(c, v) for c, v in values_by_country.items() if v is not None and np.isfinite(v)]
    if not items:
        return {c: None for c in values_by_country.keys()}, 0

    # Sort high->low
    items.sort(key=lambda x: float(x[1]), reverse=True)
    total = len(items)

    rank_by_country: dict[str, int | None] = {c: None for c in values_by_country.keys()}
    for i, (c, _v) in enumerate(items, start=1):
        rank_by_country[c] = i

    return rank_by_country, total


def get_score_card_values(df: pd.DataFrame, geo_area: str, year: int | str) -> dict[str, Any]:
    # --- current-year ladder + EU series (reuses your proven logic) ---
    years, c_vals, eu_vals = _compute_series(df, geo_area)

    year_int = int(year)
    if year_int not in years:
        raise ValueError(f"Year {year_int} not available in series: {years}")

    idx = years.index(year_int)

    c = float(c_vals[idx]) if np.isfinite(c_vals[idx]) else None
    eu = float(eu_vals[idx]) if np.isfinite(eu_vals[idx]) else None

    delta_vs_eu = None
    if c is not None and eu is not None:
        delta_vs_eu = c - eu

    # --- EU ranks: overall ladder score ---
    eu_countries = _eu_country_list(df)

    overall_by_country: dict[str, float | None] = {}
    for cn in eu_countries:
        try:
            ys, cv, _ev = _compute_series(df, cn)
            if year_int in ys:
                j = ys.index(year_int)
                vv = float(cv[j]) if np.isfinite(cv[j]) else None
            else:
                vv = None
        except Exception:
            vv = None
        overall_by_country[cn] = vv

    overall_rank_map, overall_total = _rank_desc(overall_by_country)

    # --- EU ranks: per-factor contributions (selected year only) ---
    ysuf = _year_suffix(year_int)
    factor_cols = [f"{f}_{ysuf}" for f in FACTORS]

    missing = [cname for cname in factor_cols if cname not in df.columns]
    if missing:
        raise ValueError(f"Missing expected factor columns for year 20{ysuf}: {missing}")

    # Compute country factor values (same approach as your bar chart: mean over rows for that country)
    if "country" not in df.columns:
        raise ValueError("Expected a 'country' column")

    country_df = df[df["country"].notna()].copy()
    country_df["country"] = country_df["country"].astype(str).str.strip()
    country_df = country_df[country_df["country"].isin(eu_countries)]

    # Factor values for selected geo_area
    sel_mask = country_df["country"] == str(geo_area).strip()
    sel_rows = country_df[sel_mask]
    if sel_rows.empty:
        raise ValueError(f"No rows found for country '{geo_area}'")

    sel_factor_vals = sel_rows[factor_cols].mean().to_dict()
    # normalize to factor keys
    factor_values: dict[str, float | None] = {}
    for f in FACTORS:
        v = sel_factor_vals.get(f"{f}_{ysuf}")
        factor_values[f] = float(v) if v is not None and np.isfinite(v) else None

    # Build ranks per factor
    factor_ranks: dict[str, dict[str, int | None]] = {}
    for f in FACTORS:
        col = f"{f}_{ysuf}"

        # compute mean per country
        means = country_df.groupby("country")[col].mean()

        vals_map: dict[str, float | None] = {}
        for cn in eu_countries:
            vv = means.get(cn, np.nan)
            vv = float(vv) if vv is not None and np.isfinite(vv) else None

            # Apply direction (invert if needed)
            if vv is not None and FACTOR_DIRECTION.get(f, 1) == -1:
                vv = -vv

            vals_map[cn] = vv

        rank_map, total = _rank_desc(vals_map)
        factor_ranks[f] = {
            "rank": rank_map.get(str(geo_area).strip()),
            "total": total,
        }

    # --- 3-year deltas (as you already planned) ---
    # Map year->score for this country
    c_by_year: dict[int, float | None] = {}
    for y, vv in zip(years, c_vals):
        yi = int(y)
        c_by_year[yi] = float(vv) if np.isfinite(vv) else None

    base = c_by_year.get(year_int)
    deltas_vs_selected_year: dict[int, float | None] = {}
    for yy in [2021, 2022, 2023]:
        v = c_by_year.get(yy)
        if base is None or v is None:
            deltas_vs_selected_year[yy] = None
        else:
            deltas_vs_selected_year[yy] = v - base

    return {
        # existing fields
        "year": year_int,
        "country_score": c,
        "eu_score": eu,
        "delta_vs_eu": delta_vs_eu,
        "delta_min": EU_DELTA_MIN,
        "delta_max": EU_DELTA_MAX,

        # 3-year delta row (kept)
        "years": [2021, 2022, 2023],
        "selected_year": year_int,
        "deltas_vs_selected_year": deltas_vs_selected_year,
        "year_delta_min": -1.0,
        "year_delta_max": 1.0,

        # NEW: overall EU rank
        "overall_rank": overall_rank_map.get(str(geo_area).strip()),
        "overall_total": overall_total,

        # NEW: per-factor ranks + values
        "factor_labels": FACTOR_LABELS,
        "factor_values": factor_values,
        "factor_ranks": factor_ranks,
    }
