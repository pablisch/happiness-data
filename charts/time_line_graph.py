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
    years = [2021, 2022, 2023]

    eu_df = df[df["population_EU_only"].notna()]
    eu_vals = [
        float(eu_df["ladder_score_21"].mean()),
        float(eu_df["ladder_score_22"].mean()),
        float(eu_df["ladder_score_23"].mean()),
    ]

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

    ax.plot(years, c_vals, marker="o", linewidth=2, label=geo_area)

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

    ax.set_xlabel("Year", fontsize=AXIS_LABEL_SIZE, labelpad=X_LABEL_PADDING)
    ax.set_ylabel("Happiness (ladder) score", fontsize=AXIS_LABEL_SIZE)

    ax.tick_params(axis="both", labelsize=TICK_SIZE)
    ax.set_xticks(years)

    if fixed_scale:
        ax.set_ylim(FIXED_GRAPH_MIN, FIXED_GRAPH_MAX)
    else:
        ymin = min(c_vals + eu_vals)
        ymax = max(c_vals + eu_vals)
        ymin = min(ymin, EU_TOTAL_MIN)
        ymax = max(ymax, EU_TOTAL_MAX)
        pad = (ymax - ymin) * 0.08
        ax.set_ylim(ymin - pad, ymax + pad)

    ax.grid(axis="y", linestyle="-", linewidth=1, color="#cccccc")
    ax.legend(frameon=False, fontsize=TICK_SIZE)

    for spine in ax.spines.values():
        spine.set_color("#cccccc")

    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf
