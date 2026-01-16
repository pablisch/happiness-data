# contribution_bar_chart.py

from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

BASE_WIDTH = 12
BASE_HEIGHT = 8

# -----------------------------
# Typography control
# -----------------------------
FONT_SCALE = 1.5  # change this to scale all chart text

TITLE_SIZE = 16 * FONT_SCALE
AXIS_LABEL_SIZE = 13 * FONT_SCALE
Y_TICK_SIZE = 13 * FONT_SCALE
X_TICK_SIZE = 13 * FONT_SCALE

X_LABEL_PADDING = 14 * FONT_SCALE
# -----------------------------


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
) -> BytesIO:
    out = _compute_region_factors(df, geo_area, year)

    # Support both versions:
    # - new: (labels, country_series, eu_series, year_str)
    # - old: (labels, values, year_str)  [no eu_series]
    if len(out) == 4:
        labels, country_series, eu_series, year_str = out
        country_vals = np.asarray(country_series, dtype=float)
        eu_vals = np.asarray(eu_series, dtype=float)
    elif len(out) == 3:
        labels, country_vals, year_str = out
        country_vals = np.asarray(country_vals, dtype=float)
        eu_vals = None
    else:
        raise ValueError(f"_compute_region_factors returned unexpected length: {len(out)}")

    fig, ax = plt.subplots(figsize=(BASE_WIDTH, BASE_HEIGHT))

    # ------------------------------------------------
    # Stable X-axis range (so toggling EU doesn't rescale)
    # Always compute limits using BOTH country + EU values
    # (if EU values exist)
    # ------------------------------------------------
    if eu_vals is not None:
        limit_vals = np.concatenate([country_vals, eu_vals])
    else:
        limit_vals = country_vals

    finite_vals = limit_vals[np.isfinite(limit_vals)]

    if finite_vals.size == 0:
        ax.set_xlim(0.0, 1.0)
    else:
        xmax = float(finite_vals.max())
        xmin = float(finite_vals.min())

        # For contributions these should be >= 0, but keep safe:
        xmin = min(0.0, xmin)

        pad = (xmax - xmin) * 0.06 if xmax > xmin else 0.1
        ax.set_xlim(xmin, xmax + pad)
    # ------------------------------------------------

    if not show_eu or eu_vals is None:
        # --- Single set ---
        ax.barh(labels, country_vals)
    else:
        # --- Grouped bars: Country + EU ---
        y = np.arange(len(labels))

        group_height = 0.8
        bar_h = group_height / 2.2
        gap = bar_h * 0.25

        y_country = y - (bar_h / 2 + gap / 2)
        y_eu = y + (bar_h / 2 + gap / 2)

        ax.barh(y_country, country_vals, height=bar_h, label=geo_area)
        ax.barh(y_eu, eu_vals, height=bar_h, label="EU average", color="#888888")

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

    ax.tick_params(axis="y", labelsize=Y_TICK_SIZE)
    ax.tick_params(axis="x", labelsize=X_TICK_SIZE)

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
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf




# def plot_contribution_bar_chart(
#     df: pd.DataFrame,
#     geo_area: str,
#     year: int | str,
#     show_eu: bool = False,
# ) -> BytesIO:
#     labels, country_values, eu_values, year_str = _compute_region_factors(df, geo_area, year)
#
#     fig, ax = plt.subplots(figsize=(BASE_WIDTH, BASE_HEIGHT))
#
#     if not show_eu:
#         # --- Current behaviour ---
#         ax.barh(labels, country_values)
#
#     else:
#         # --- Grouped bars: Country (top) + EU (beneath) ---
#         y = np.arange(len(labels))
#
#         group_height = 0.8          # total vertical space per factor row
#         bar_h = group_height / 2.2  # thinner bars to fit two
#         gap = bar_h * 0.25          # small gap between them
#
#         # Country above, EU beneath
#         y_country = y - (bar_h / 2 + gap / 2)
#         y_eu = y + (bar_h / 2 + gap / 2)
#
#         ax.barh(y_country, country_values, height=bar_h, label=geo_area)
#         ax.barh(y_eu, eu_values, height=bar_h, label="EU average", color="#888888")
#
#         # Center tick labels between the paired bars
#         ax.set_yticks(y)
#         ax.set_yticklabels(labels)
#
#         ax.legend(loc="lower right", frameon=False)
#
#     ax.set_xlabel(
#         "Contribution to happiness score",
#         fontsize=AXIS_LABEL_SIZE,
#         labelpad=X_LABEL_PADDING,
#     )
#
#     ax.set_ylabel(
#         "Contributing factors",
#         fontsize=AXIS_LABEL_SIZE,
#         labelpad=12,
#     )
#
#     ax.tick_params(axis="y", labelsize=Y_TICK_SIZE)
#     ax.tick_params(axis="x", labelsize=X_TICK_SIZE)
#
#     ax.invert_yaxis()
#
#     # Grid lines aligned with x ticks
#     ax.set_axisbelow(True)
#     ax.grid(
#         axis="x",
#         which="major",
#         linestyle="-",
#         linewidth=1,
#         alpha=1,
#         color="#666666",
#     )
#
#     # Lighten the bar container (axes spines)
#     for spine in ax.spines.values():
#         spine.set_color("#cccccc")
#         spine.set_linewidth(0.8)
#
#     # Remove the outer figure box
#     fig.patch.set_visible(False)
#
#     fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))
#
#     buf = BytesIO()
#     fig.savefig(buf, format="png", transparent=True)
#     plt.close(fig)
#     buf.seek(0)
#     return buf
