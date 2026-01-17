# charts/map_data.py
from __future__ import annotations

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from charts.eu_iso2 import EU_NAME_TO_ISO2

YEARS: List[int] = [2021, 2022, 2023]

# These match your existing factor columns used elsewhere
FACTORS: List[str] = [
    "GDP",
    "social_support",
    "life_expectancy",
    "freedom",
    "generosity",
    "corruption",
    "other",
]

LADDER_COLS: Dict[int, str] = {
    2021: "ladder_score_21",
    2022: "ladder_score_22",
    2023: "ladder_score_23",
}

FACTOR_COLS: Dict[int, Dict[str, str]] = {
    2021: {f: f"{f}_21" for f in FACTORS},
    2022: {f: f"{f}_22" for f in FACTORS},
    2023: {f: f"{f}_23" for f in FACTORS},
}


def _require_cols(df: pd.DataFrame, cols: List[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")


def _get_eu_country_names(df: pd.DataFrame) -> List[str]:
    """
    Uses the same EU membership logic as your charts:
    EU rows are those with population_EU_only notna,
    and the list of EU countries is derived from those rows.
    """
    if "population_EU_only" not in df.columns:
        raise ValueError("EU selection requires 'population_EU_only' column")
    if "country" not in df.columns:
        raise ValueError("Expected a 'country' column")

    eu_agg_df = df[df["population_EU_only"].notna()]
    if eu_agg_df.empty:
        raise ValueError("No EU rows found (population_EU_only is empty)")

    eu_countries = (
        eu_agg_df["country"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )
    eu_countries = [c for c in eu_countries if c]  # drop blanks
    return sorted(eu_countries)


def _safe_float(x: Any) -> float | None:
    try:
        v = float(x)
        return v if np.isfinite(v) else None
    except Exception:
        return None


def _compute_eu_averages(df: pd.DataFrame) -> Dict[str, Any]:
    eu_df = df[df["population_EU_only"].notna()]
    eu: Dict[str, Any] = {"scores": {}, "factors": {}}

    # Ladder EU averages
    for y in YEARS:
        col = LADDER_COLS[y]
        eu["scores"][str(y)] = _safe_float(eu_df[col].mean())

    # Factor EU averages
    for y in YEARS:
        eu["factors"][str(y)] = {}
        for f, col in FACTOR_COLS[y].items():
            eu["factors"][str(y)][f] = _safe_float(eu_df[col].mean())

    return eu


def _compute_country_means(df: pd.DataFrame, eu_countries: List[str]) -> pd.DataFrame:
    """
    Returns a df where each row is one country and columns include
    ladder_score_21/22/23 and factor cols.
    """
    country_df = df[df["country"].notna()].copy()
    country_df["country"] = country_df["country"].astype(str).str.strip()
    country_df = country_df[country_df["country"].isin(eu_countries)]

    if country_df.empty:
        raise ValueError("No EU member country rows found (after filtering)")

    needed_cols = ["country"] + list(LADDER_COLS.values())
    for y in YEARS:
        needed_cols.extend(list(FACTOR_COLS[y].values()))
    _require_cols(country_df, needed_cols)

    # mean per country (same semantics as your other charts)
    return country_df.groupby("country", as_index=False)[needed_cols[1:]].mean()


def _compute_bounds(payload_countries: List[Dict[str, Any]], eu: Dict[str, Any]) -> Dict[str, Any]:
    """
    Precompute useful global bounds so the frontend can keep fixed scales stable.
    - score_delta_min/max across EU countries and years
    - factor_delta_min/max per factor across EU countries and years
    - score_min/max (absolute) across EU countries and years
    - factor_min/max per factor (absolute) across EU countries and years
    """
    score_vals: List[float] = []
    score_deltas: List[float] = []
    factor_vals: Dict[str, List[float]] = {f: [] for f in FACTORS}
    factor_deltas: Dict[str, List[float]] = {f: [] for f in FACTORS}

    for c in payload_countries:
        scores = c.get("scores", {})
        factors = c.get("factors", {})

        for y in YEARS:
            ys = str(y)

            c_score = scores.get(ys)
            eu_score = eu["scores"].get(ys)
            if isinstance(c_score, (int, float)) and isinstance(eu_score, (int, float)):
                if np.isfinite(c_score) and np.isfinite(eu_score):
                    score_vals.append(float(c_score))
                    score_deltas.append(float(c_score) - float(eu_score))

            fy = factors.get(ys, {})
            eu_fy = eu["factors"].get(ys, {})
            for f in FACTORS:
                c_f = fy.get(f)
                eu_f = eu_fy.get(f)
                if isinstance(c_f, (int, float)) and np.isfinite(c_f):
                    factor_vals[f].append(float(c_f))
                if (
                    isinstance(c_f, (int, float))
                    and isinstance(eu_f, (int, float))
                    and np.isfinite(c_f)
                    and np.isfinite(eu_f)
                ):
                    factor_deltas[f].append(float(c_f) - float(eu_f))

    def _minmax(xs: List[float]) -> Tuple[float | None, float | None]:
        xs = [x for x in xs if np.isfinite(x)]
        if not xs:
            return None, None
        return float(min(xs)), float(max(xs))

    score_min, score_max = _minmax(score_vals)
    delta_min, delta_max = _minmax(score_deltas)

    factor_minmax = {f: {"min": _minmax(factor_vals[f])[0], "max": _minmax(factor_vals[f])[1]} for f in FACTORS}
    factor_delta_minmax = {f: {"min": _minmax(factor_deltas[f])[0], "max": _minmax(factor_deltas[f])[1]} for f in FACTORS}

    return {
        "score": {"min": score_min, "max": score_max},
        "score_delta_vs_eu": {"min": delta_min, "max": delta_max},
        "factors": factor_minmax,
        "factor_delta_vs_eu": factor_delta_minmax,
    }


def build_map_payload(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Single payload for all map modes.
    EU-only countries, all years, all factors, plus EU averages and useful bounds.
    """
    # validate
    _require_cols(df, ["country", "population_EU_only"] + list(LADDER_COLS.values()))
    for y in YEARS:
        _require_cols(df, list(FACTOR_COLS[y].values()))

    eu_countries = _get_eu_country_names(df)
    eu = _compute_eu_averages(df)

    means_df = _compute_country_means(df, eu_countries)

    countries: List[Dict[str, Any]] = []
    for _, row in means_df.iterrows():
        name = str(row["country"]).strip()
        iso2 = EU_NAME_TO_ISO2.get(name)

        # If we can't map it, we still include it, but iso2 will be None
        country_obj: Dict[str, Any] = {
            "name": name,
            "iso2": iso2,
            "scores": {},
            "factors": {},
        }

        for y in YEARS:
            ys = str(y)
            country_obj["scores"][ys] = _safe_float(row[LADDER_COLS[y]])

            country_obj["factors"][ys] = {}
            for f, col in FACTOR_COLS[y].items():
                country_obj["factors"][ys][f] = _safe_float(row[col])

        countries.append(country_obj)

    bounds = _compute_bounds(countries, eu)
    unmapped = sorted([c["name"] for c in countries if not c.get("iso2")])

    return {
        "years": YEARS,
        "factors": FACTORS,
        "countries": countries,  # name + per-year scores/factors
        "eu": eu,                # per-year EU averages for scores and factors
        "bounds": bounds,        # global bounds for fixed scale maps
        "unmapped": unmapped,
    }
