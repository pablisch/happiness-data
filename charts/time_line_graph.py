# time_line_graph.py

from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd

BASE_WIDTH = 12
BASE_HEIGHT = 6

# -----------------------------
# Typography control
# -----------------------------
FONT_SCALE = 1.5

TITLE_SIZE = 16 * FONT_SCALE
AXIS_LABEL_SIZE = 13 * FONT_SCALE
TICK_SIZE = 12 * FONT_SCALE

X_LABEL_PADDING = 12 * FONT_SCALE
# -----------------------------

# -----------------------------
# Scale values
# -----------------------------
FIXED_MIN = 5
FIXED_MAX = 8
VARIABLE_MIN = 6.5
VARIABLE_MAX = 6.7
# -----------------------------


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

    fig, ax = plt.subplots(figsize=(BASE_WIDTH, BASE_HEIGHT))

    # --- Plot country line ---
    ax.plot(years, c_vals, marker="o", label=geo_area)

    # --- Optional EU line ---
    if show_eu:
        ax.plot(years, eu_vals, marker="o", linestyle="--", label="EU average")

    ax.set_xlabel("Year", fontsize=AXIS_LABEL_SIZE, labelpad=X_LABEL_PADDING)
    ax.set_ylabel("Happiness (ladder) score", fontsize=AXIS_LABEL_SIZE)

    ax.tick_params(axis="both", labelsize=TICK_SIZE)
    ax.set_xticks(years)

    ax.grid(axis="y", linestyle="-", linewidth=1, alpha=1, color="#666666")

    # ------------------------------------------------
    # Y-axis behaviour toggle (stable ranges)
    #
    # fixed_scale == True  -> fixed EU-wide scale 5 to 8
    # fixed_scale == False -> "zoomed" scale that is stable even if showEU toggles
    #                        (computed using BOTH country+EU values regardless)
    # ------------------------------------------------

    # Always include EU values in the LIMIT calculation so toggling showEU
    # doesn't change the axis scale.
    limit_vals = c_vals + eu_vals

    if fixed_scale:
        # Fixed EU-wide scale (trial)
        ax.set_ylim(FIXED_MIN, FIXED_MAX)
    else:
        # Data-driven but stable (won't change when showEU is toggled)
        ymin = min(limit_vals) if limit_vals else VARIABLE_MIN
        ymax = max(limit_vals) if limit_vals else VARIABLE_MAX

        # Enforce your "guard rails":
        # - cap the minimum at 6.4 (i.e. don't let the lower bound go above 6.4)
        # - floor the maximum at 6.8 (i.e. don't let the upper bound go below 6.8)
        ymin = min(ymin, VARIABLE_MIN)
        ymax = max(ymax, VARIABLE_MAX)

        # Small padding for aesthetics (won't change with toggling)
        pad = (ymax - ymin) * 0.06
        ax.set_ylim(ymin - pad, ymax + pad)

    # ------------------------------------------------


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

