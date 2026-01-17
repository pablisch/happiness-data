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
    if eu_df.empty:
        raise ValueError("No EU rows found (population_EU_only is empty)")

    eu_series = eu_df[factor_cols].mean()

    if "country" not in df.columns:
        raise ValueError("Country selection requires 'country' column")

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
        "Corruption",
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


def _scaled_font(base: float, width_px: int | None, height_px: int | None) -> float:
    """
    Scales a base font down for small dashboard tiles.
    Uses the *smaller* of width/height constraints.
    """
    if not width_px or not height_px:
        return float(base)

    # Reference "nice" tile size
    ref_w, ref_h = 560, 240
    scale = min(width_px / ref_w, height_px / ref_h)

    # Clamp so it never becomes silly
    scale = max(0.55, min(1.0, scale))
    return float(base) * scale


def plot_contribution_bar_chart(
    df: pd.DataFrame,
    geo_area: str,
    year: int | str,
    show_eu: bool = False,
    fixed_scale: bool = False,
    # NEW: size from frontend
    width_px: int | None = None,
    height_px: int | None = None,
) -> BytesIO:
    labels, country_series, eu_series, year_str = _compute_region_factors(df, geo_area, year)

    country_vals = np.asarray(country_series, dtype=float)
    eu_vals = np.asarray(eu_series, dtype=float)

    # -------- Figure sizing --------
    # If the frontend provides pixel sizes, create a figure to match.
    # Otherwise fall back to your BASE_WIDTH/BASE_HEIGHT_BAR.
    dpi = 140  # dashboard-friendly sharpness without huge files
    if width_px and height_px:
        fig_w = max(3.2, width_px / dpi)
        fig_h = max(1.8, height_px / dpi)
        figsize = (fig_w, fig_h)
    else:
        figsize = (BASE_WIDTH, BASE_HEIGHT_BAR)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # -------- Font sizing (scale down for small tiles) --------
    axis_label_size = _scaled_font(AXIS_LABEL_SIZE, width_px, height_px)
    tick_size = _scaled_font(TICK_SIZE, width_px, height_px)
    # Less padding for dashboard tiles
    xlabel_pad = max(3, int(_scaled_font(X_LABEL_PADDING, width_px, height_px)))

    # Helpers
    finite_country = country_vals[np.isfinite(country_vals)]
    country_has_negative = bool(finite_country.size and (finite_country.min() < 0))

    # X-axis range selection (your existing logic)
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
            pad = (xmax - vmin) * EU_BAR_XPAD_RATIO
            xmin_raw = vmin - pad
            xmin = max(FIXED_BAR_XMIN, xmin_raw)
        else:
            xmin = 0.0
        ax.set_xlim(xmin, xmax)
        if xmin < 0:
            ax.axvline(0, linewidth=1, color="#666666", alpha=0.8)

    # Bars
    if not show_eu:
        ax.barh(labels, country_vals, color=COUNTRY_COLOR)
    else:
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

        # Legend in a predictable spot; smaller font
        ax.legend(loc="lower right", frameon=False, fontsize=tick_size)

    ax.set_xlabel(
        "Contribution to happiness score",
        fontsize=axis_label_size,
        labelpad=xlabel_pad,
    )
    ax.set_ylabel(
        "Contributing factors",
        fontsize=axis_label_size,
        labelpad=8,
    )

    ax.tick_params(axis="x", labelsize=tick_size)
    ax.tick_params(axis="y", labelsize=tick_size)

    ax.invert_yaxis()
    ax.set_axisbelow(True)
    ax.grid(axis="x", which="major", linestyle="-", linewidth=1, alpha=1, color="#666666")

    for spine in ax.spines.values():
        spine.set_color("#cccccc")
        spine.set_linewidth(0.8)

    fig.patch.set_visible(False)

    # Tight but stable; keep small padding so labels fit
    fig.tight_layout(pad=0.6)

    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf
