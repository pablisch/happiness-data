# contribution_bar_chart.py

from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd

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

TITLE_BOTTOM_PADDING = 23 * FONT_SCALE
X_LABEL_PADDING = 14 * FONT_SCALE
# -----------------------------


def _compute_region_factors(df: pd.DataFrame, geo_area: str, year: int | str):
    year_str = str(year)
    if len(year_str) == 4:  # 2021 -> "21"
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

    # -------------------------
    # SELECT THE SCOPE (EU or country)
    # -------------------------
    if geo_area == "EU":
        if "population_EU_only" not in df.columns:
            raise ValueError("EU selection requires 'population_EU_only' column")

        area_df = df[df["population_EU_only"].notna()]
        if area_df.empty:
            raise ValueError("No EU rows found (population_EU_only is empty)")

        # Average across EU member states
        series = area_df[factor_cols].mean()

    else:
        # Treat geo_area as a country name
        if "country" not in df.columns:
            raise ValueError("Country selection requires 'country' column")

        area_df = df[df["country"] == geo_area]
        if area_df.empty:
            raise ValueError(f"No rows found for country '{geo_area}'")

        # If there are multiple rows, average them; otherwise this is just the row values
        series = area_df[factor_cols].mean()

    labels = [
        "GDP",
        "Social support",
        "Life expectancy",
        "Freedom",
        "Generosity",
        "Corruption (low = better)",
        "Residual (other)",
    ]

    values = series.values
    return labels, values, year_str



def plot_contribution_bar_chart(df: pd.DataFrame, geo_area: str, year: int | str) -> BytesIO:
    labels, values, year_str = _compute_region_factors(df, geo_area, year)

    fig, ax = plt.subplots(figsize=(BASE_WIDTH, BASE_HEIGHT))

    # Horizontal bar chart
    ax.barh(labels, values)

    # BELOW - replaced in favour of suptitle
    # ax.set_title(
    #     f"Average factor contributions to happiness (ladder) score "
    #     f"for {geo_area} in 20{year_str}",
    #     fontsize=TITLE_SIZE,
    #     pad=TITLE_BOTTOM_PADDING,  # ← vertical spacing from plot
    #     loc="center",
    # )

    fig.suptitle(
        f"Average factor contributions to happiness (ladder) score "
        f"for {geo_area} in 20{year_str}",
        fontsize=TITLE_SIZE,
        y=0.98,  # near top of figure
    )

    ax.set_xlabel(
        "Contribution to happiness score",
        fontsize=AXIS_LABEL_SIZE,
        labelpad=X_LABEL_PADDING,  # ← add space between ticks and label
    )

    ax.set_ylabel(
        "Contributing factors",
        fontsize=AXIS_LABEL_SIZE,
        labelpad=12,
    )

    ax.tick_params(axis="y", labelsize=Y_TICK_SIZE)
    ax.tick_params(axis="x", labelsize=X_TICK_SIZE)

    ax.invert_yaxis()

    # Grid lines aligned with x ticks
    ax.set_axisbelow(True)
    ax.grid(
        axis="x",
        which="major",
        linestyle="-",
        linewidth=1,
        alpha=1,
        color="#666666",
    )

    # Lighten the bar container (axes spines)
    for spine in ax.spines.values():
        spine.set_color("#cccccc")
        spine.set_linewidth(0.8)

    # Remove the outer figure box
    fig.patch.set_visible(False)

    # fig.tight_layout() # replaced with below when replacing the title with a suptitle
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))


    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)

    return buf
