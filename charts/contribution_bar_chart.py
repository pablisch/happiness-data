from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from charts.chart_style import (
    AXIS_LABEL_SIZE,
    TICK_SIZE,
    X_LABEL_PADDING,
    BASE_WIDTH,
    BASE_HEIGHT_BAR,
    EU_BAR_XMIN, EU_BAR_XMAX, EU_BAR_XPAD_RATIO,
    FIXED_BAR_XMIN, FIXED_BAR_XMAX, FIXED_BAR_XPAD_RATIO,
    COUNTRY_COLOR, EU_COLOR,
)


def _compute_region_factors(df: pd.DataFrame, geo_area: str, year: int | str):
    geo_area = str(geo_area).strip()

    year_str = str(year)
    if len(year_str) == 4:
        year_str = year_str[-2:]
    suffix = f"_{year_str}"

    factor_basenames = [
        "GDP",
        "social_support",
        "life_expectancy",
        "freedom",
        "generosity",
        "corruption",
        "other",
    ]
    factor_cols = [f"{name}{suffix}" for name in factor_basenames]

    missing = [c for c in factor_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns for year 20{year_str}: {missing}")

    if "population_EU_only" not in df.columns:
        raise ValueError("EU overlay requires 'population_EU_only' column")

    eu_df = df[df["population_EU_only"].notna()]
    eu_series = eu_df[factor_cols].mean()

    country_df = df[df["country"].astype(str).str.strip() == geo_area]
    if country_df.empty:
        raise ValueError(f"No rows found for country '{geo_area}'")

    country_series = country_df[factor_cols].mean()

    labels = [
        "GDP",
        "Social support",
        "Life expectancy",
        "Freedom",
        "Generosity",
        "Corruption",
        "Residual (other)",
    ]

    return labels, country_series.values, eu_series.values


def build_contribution_bar_title(geo_area: str, year: int | str, show_eu: bool = False) -> str:
    year_str = str(year)
    if len(year_str) == 4:
        year_str = year_str[-2:]
    year = f"20{year_str}"

    title = f"Happiness contributory factor scores for\n{geo_area} in {year}"
    if show_eu:
        title += " (alongside EU average)"
    return title


def plot_contribution_bar_chart(
    df: pd.DataFrame,
    geo_area: str,
    year: int | str,
    show_eu: bool = False,
    fixed_scale: bool = False,
) -> BytesIO:

    labels, country_vals, eu_vals = _compute_region_factors(df, geo_area, year)

    country_vals = np.asarray(country_vals, dtype=float)
    eu_vals = np.asarray(eu_vals, dtype=float)

    fig, ax = plt.subplots(figsize=(BASE_WIDTH, BASE_HEIGHT_BAR))

    finite_country = country_vals[np.isfinite(country_vals)]
    country_has_negative = bool(finite_country.size and finite_country.min() < 0)

    if fixed_scale:
        xmax = FIXED_BAR_XMAX * (1 + FIXED_BAR_XPAD_RATIO)
        xmin = FIXED_BAR_XMIN if country_has_negative else 0
    else:
        xmax = EU_BAR_XMAX * (1 + EU_BAR_XPAD_RATIO)
        xmin = FIXED_BAR_XMIN if country_has_negative else 0

    ax.set_xlim(xmin, xmax)

    if xmin < 0:
        ax.axvline(0, linewidth=1, color="#666666", alpha=0.8)

    if show_eu:
        y = np.arange(len(labels))
        bar_h = 0.35

        ax.barh(y - bar_h / 2, country_vals, height=bar_h, color=COUNTRY_COLOR, label=geo_area)
        ax.barh(y + bar_h / 2, eu_vals, height=bar_h, color=EU_COLOR, label="EU average")

        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.legend(frameon=False, fontsize=TICK_SIZE)
    else:
        ax.barh(labels, country_vals, color=COUNTRY_COLOR)

    ax.set_xlabel(
        "Contribution to happiness score",
        fontsize=AXIS_LABEL_SIZE,
        labelpad=X_LABEL_PADDING,
    )
    ax.set_ylabel("Contributing factors", fontsize=AXIS_LABEL_SIZE)

    ax.tick_params(axis="x", labelsize=TICK_SIZE)
    ax.tick_params(axis="y", labelsize=TICK_SIZE)

    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="-", linewidth=1, color="#cccccc")

    for spine in ax.spines.values():
        spine.set_color("#cccccc")

    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf
