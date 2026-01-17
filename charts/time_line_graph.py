from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd

from charts.chart_style import (
    AXIS_LABEL_SIZE,
    TICK_SIZE,
    X_LABEL_PADDING,
    BASE_WIDTH,
    BASE_HEIGHT_GRAPH,
    FIXED_GRAPH_MIN,
    FIXED_GRAPH_MAX,
    EU_TOTAL_MIN,
    EU_TOTAL_MAX,
    EU_COLOR,
)

def build_timeline_title(geo_area: str, show_eu: bool = False, fixed_scale: bool = False) -> str:
    title = f"Happiness (ladder) score over time (2021–2023)\n{geo_area}"
    if show_eu:
        title += " (vs EU average)"
    return title


def _compute_series(df: pd.DataFrame, geo_area: str):
    required = ["ladder_score_21", "ladder_score_22", "ladder_score_23"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    years = [2021, 2022, 2023]

    if "population_EU_only" not in df.columns:
        raise ValueError("EU selection requires 'population_EU_only' column")

    eu_df = df[df["population_EU_only"].notna()]
    if eu_df.empty:
        raise ValueError("No EU rows found (population_EU_only is empty)")

    eu_vals = [
        float(eu_df["ladder_score_21"].mean()),
        float(eu_df["ladder_score_22"].mean()),
        float(eu_df["ladder_score_23"].mean()),
    ]

    if "country" not in df.columns:
        raise ValueError("Country selection requires 'country' column")

    cdf = df[df["country"] == geo_area]
    if cdf.empty:
        raise ValueError(f"No rows found for country '{geo_area}'")

    c_vals = [
        float(cdf["ladder_score_21"].mean()),
        float(cdf["ladder_score_22"].mean()),
        float(cdf["ladder_score_23"].mean()),
    ]

    return years, c_vals, eu_vals


def _scaled_font(base: float, width_px: int | None, height_px: int | None) -> float:
    if not width_px or not height_px:
        return float(base)

    ref_w, ref_h = 560, 240
    scale = min(width_px / ref_w, height_px / ref_h)
    scale = max(0.55, min(1.0, scale))
    return float(base) * scale


def plot_time_line_graph(
    df: pd.DataFrame,
    geo_area: str,
    show_eu: bool = False,
    fixed_scale: bool = False,
    # NEW: size from frontend
    width_px: int | None = None,
    height_px: int | None = None,
) -> BytesIO:
    years, c_vals, eu_vals = _compute_series(df, geo_area)

    dpi = 140
    if width_px and height_px:
        fig_w = max(3.2, width_px / dpi)
        fig_h = max(1.8, height_px / dpi)
        figsize = (fig_w, fig_h)
    else:
        figsize = (BASE_WIDTH, BASE_HEIGHT_GRAPH)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    axis_label_size = _scaled_font(AXIS_LABEL_SIZE, width_px, height_px)
    tick_size = _scaled_font(TICK_SIZE, width_px, height_px)
    xlabel_pad = max(3, int(_scaled_font(X_LABEL_PADDING, width_px, height_px)))

    # Plot country line
    ax.plot(
        years,
        c_vals,
        marker="o",
        linewidth=2,
        label=geo_area,
    )

    # Optional EU line
    if show_eu:
        ax.plot(
            years,
            eu_vals,
            marker="o",
            linestyle="--",
            linewidth=2,
            color=EU_COLOR,
            label="EU average",
        )

    ax.set_xlabel("Year", fontsize=axis_label_size, labelpad=xlabel_pad)
    ax.set_ylabel("Happiness (ladder) score", fontsize=axis_label_size)

    ax.tick_params(axis="both", labelsize=tick_size)
    ax.set_xticks(years)

    ax.grid(axis="y", linestyle="-", linewidth=1, alpha=1, color="#666666")

    # Y-axis behaviour toggle (your existing logic)
    limit_vals = list(c_vals) + (list(eu_vals) if show_eu else [])

    if fixed_scale:
        ax.set_ylim(FIXED_GRAPH_MIN, FIXED_GRAPH_MAX)
    else:
        ymin = min(limit_vals) if limit_vals else EU_TOTAL_MIN
        ymax = max(limit_vals) if limit_vals else EU_TOTAL_MAX

        ymin = min(ymin, EU_TOTAL_MIN)
        ymax = max(ymax, EU_TOTAL_MAX)

        pad = (ymax - ymin) * 0.06
        ax.set_ylim(ymin - pad, ymax + pad)

    # Legend under plot, but keep it from resizing axes
    leg = ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.06, -0.02),
        frameon=False,
        fontsize=tick_size,
    )
    leg.set_in_layout(False)

    for spine in ax.spines.values():
        spine.set_color("#cccccc")
        spine.set_linewidth(0.8)

    fig.patch.set_visible(False)

    # Reserve bottom margin always so legend doesn't break layout
    fig.tight_layout(rect=[0, 0.14, 1, 1], pad=0.6)

    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf
