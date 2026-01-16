# contribution_bar_chart.py

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
    """
    Returns:
      labels: list[str]
      country_values: np.ndarray
      eu_values: np.ndarray
      year_str: str  (two-digit, e.g. "21")
    """
    # Normalise inputs
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

    # EU series (always computed so it can be optionally displayed)
    if "population_EU_only" not in df.columns:
        raise ValueError("EU overlay requires 'population_EU_only' column")

    eu_df = df[df["population_EU_only"].notna()]
    if eu_df.empty:
        raise ValueError("No EU rows found (population_EU_only is empty)")

    eu_series = eu_df[factor_cols].mean()

    # Country series
    if "country" not in df.columns:
        raise ValueError("Country selection requires 'country' column")

    # Be tolerant of whitespace differences
    country_mask = df["country"].astype(str).str.strip() == geo_area
    country_df = df[country_mask]

    if country_df.empty:
        raise ValueError(f"No rows found for country '{geo_area}'")

    country_series = country_df[factor_cols].mean()

    labels = [
        "GDP",
        "Social support",
        "Life expectancy",
        "Freedom",
        "Generosity",
        "Corruption (low = better)",
        "Residual (other)",
    ]

    return labels, country_series.values, eu_series.values, year_str


def build_contribution_bar_title(geo_area: str, year: int | str, show_eu: bool = False) -> str:
    year_str = str(year)
    if len(year_str) == 4:
        year_str = year_str[-2:]
    year = f"20{year_str}"

    title = f"Average factor contributions to happiness (ladder) score\nfor {geo_area} in {year}"
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
    labels, country_series, eu_series, year_str = _compute_region_factors(df, geo_area, year)

    # Normalise to arrays
    country_vals = np.asarray(country_series, dtype=float)
    eu_vals = np.asarray(eu_series, dtype=float)

    fig, ax = plt.subplots(figsize=(BASE_WIDTH, BASE_HEIGHT_BAR))

    # Helpers
    finite_country = country_vals[np.isfinite(country_vals)]
    country_has_negative = bool(finite_country.size and (finite_country.min() < 0))

    # ------------------------------------------------
    # X-axis range selection
    #
    # fixed_scale=True:
    #   - XMAX fixed (EU-wide)
    #   - XMIN = 0 unless current country needs negatives; then use FIXED_BAR_XMIN
    #
    # fixed_scale=False (bugfixed):
    #   - show negatives if current country has them
    #   - but do NOT allow XMIN to go below FIXED_BAR_XMIN (EU-country fixed minimum)
    # ------------------------------------------------
    if fixed_scale:
        xmax = FIXED_BAR_XMAX * (1.0 + FIXED_BAR_XPAD_RATIO)
        xmin = FIXED_BAR_XMIN if country_has_negative else 0.0
        ax.set_xlim(xmin, xmax)

        if xmin < 0:
            ax.axvline(0, linewidth=1, color="#666666", alpha=0.8)

    else:
        xmax = EU_BAR_XMAX * (1.0 + EU_BAR_XPAD_RATIO)

        if country_has_negative:
            vmin = float(finite_country.min())

            # Padding can push below the intended "floor" (FIXED_BAR_XMIN), so clamp it.
            pad = (xmax - vmin) * EU_BAR_XPAD_RATIO
            xmin_raw = vmin - pad
            xmin = max(FIXED_BAR_XMIN, xmin_raw)
        else:
            xmin = 0.0

        ax.set_xlim(xmin, xmax)

        if xmin < 0:
            ax.axvline(0, linewidth=1, color="#666666", alpha=0.8)
    # ------------------------------------------------

    if not show_eu:
        # Single series
        ax.barh(labels, country_vals)
    else:
        # Grouped bars: Country (top) + EU (below)
        y = np.arange(len(labels))

        group_height = 0.8
        bar_h = group_height / 2.2
        gap = bar_h * 0.25

        y_country = y - (bar_h / 2 + gap / 2)
        y_eu = y + (bar_h / 2 + gap / 2)

        ax.barh(y_country, country_vals, height=bar_h, label=geo_area, color=COUNTRY_COLOR)
        ax.barh(y_eu, eu_vals, height=bar_h, label="EU average", color=EU_COLOR)

        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.legend(loc="lower right", frameon=False)

    ax.set_xlabel(
        "Contribution to happiness score",
        fontsize=AXIS_LABEL_SIZE,
        labelpad=X_LABEL_PADDING,
    )

    ax.set_ylabel(
        "Contributing factors",
        fontsize=AXIS_LABEL_SIZE,
        labelpad=12,
    )

    ax.tick_params(axis="x", labelsize=TICK_SIZE)
    ax.tick_params(axis="y", labelsize=TICK_SIZE)

    ax.invert_yaxis()

    ax.set_axisbelow(True)
    ax.grid(
        axis="x",
        which="major",
        linestyle="-",
        linewidth=1,
        alpha=1,
        color="#666666",
    )

    for spine in ax.spines.values():
        spine.set_color("#cccccc")
        spine.set_linewidth(0.8)

    fig.patch.set_visible(False)
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf
