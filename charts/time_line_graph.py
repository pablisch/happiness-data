# time_line_graph.py

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
    # Expect these columns exist in your combined dataframe
    required = ["ladder_score_21", "ladder_score_22", "ladder_score_23"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    years = [2021, 2022, 2023]

    # EU average (based on population_EU_only marker like you used before)
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

    # Country series
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


def plot_time_line_graph(
    df: pd.DataFrame,
    geo_area: str,
    show_eu: bool = False,
    fixed_scale: bool = False,
) -> BytesIO:
    years, c_vals, eu_vals = _compute_series(df, geo_area)

    fig, ax = plt.subplots(figsize=(BASE_WIDTH, BASE_HEIGHT_GRAPH))

    # --- Plot country line (always) ---
    ax.plot(
        years,
        c_vals,
        marker="o",
        linewidth=2,
        label=geo_area,
    )

    # --- Optional EU line (only if show_eu) ---
    if show_eu:
        ax.plot(
            years,
            eu_vals,
            marker="o",
            linestyle="--",
            linewidth=2,
            color=EU_COLOR,          # matches EU bars
            label="EU average",
        )

    ax.set_xlabel("Year", fontsize=AXIS_LABEL_SIZE, labelpad=X_LABEL_PADDING)
    ax.set_ylabel("Happiness (ladder) score", fontsize=AXIS_LABEL_SIZE)

    ax.tick_params(axis="both", labelsize=TICK_SIZE)
    ax.set_xticks(years)

    ax.grid(axis="y", linestyle="-", linewidth=1, alpha=1, color="#666666")

    # ------------------------------------------------
    # Y-axis behaviour toggle (stable ranges)
    # ------------------------------------------------
    limit_vals = list(c_vals) + list(eu_vals)

    if fixed_scale:
        ax.set_ylim(FIXED_GRAPH_MIN, FIXED_GRAPH_MAX)
    else:
        ymin = min(limit_vals) if limit_vals else EU_TOTAL_MIN
        ymax = max(limit_vals) if limit_vals else EU_TOTAL_MAX

        ymin = min(ymin, EU_TOTAL_MIN)
        ymax = max(ymax, EU_TOTAL_MAX)

        pad = (ymax - ymin) * 0.06
        ax.set_ylim(ymin - pad, ymax + pad)

    # ------------------------------------------------
    # Legend / key
    #
    # IMPORTANT:
    # - Positioned under the plot (right of y-ticks)
    # - Removed from layout calculations so chart size
    #   does NOT change when show_eu toggles
    # ------------------------------------------------
    leg = ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.08, -0.02),
        frameon=False,
        fontsize=TICK_SIZE,
    )
    # Critical: prevent tight_layout from resizing axes
    leg.set_in_layout(False)


    for spine in ax.spines.values():
        spine.set_color("#cccccc")
        spine.set_linewidth(0.8)

    fig.patch.set_visible(False)

    # Reserve a fixed bottom margin ALWAYS so layout is stable
    fig.tight_layout(rect=[0, 0.14, 1, 1])

    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    buf.seek(0)

    return buf

